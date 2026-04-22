import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
import time
import json
from fpdf import FPDF
import io
import streamlit.components.v1 as components

# Load environment variables
load_dotenv()

# File to store history
HISTORY_FILE = "chat_history.json"

# --- UTILS & FUNCTIONS ---

def save_history(messages):
    serializable_messages = []
    for msg in messages:
        new_msg = msg.copy()
        if "pdf_bytes" in new_msg:
            del new_msg["pdf_bytes"]
        serializable_messages.append(new_msg)
    with open(HISTORY_FILE, "w") as f:
        json.dump(serializable_messages, f)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def calculate_cost(input_tokens, output_tokens, model, kurs_rate):
    price_input = 0.15 / 1_000_000
    price_output = 0.60 / 1_000_000
    if "llama" in model:
        price_input = 0.15 / 1_000_000
        price_output = 0.15 / 1_000_000
    cost_usd = (input_tokens * price_input) + (output_tokens * price_output)
    cost_idr = cost_usd * kurs_rate
    return cost_usd, cost_idr

def get_analogy(idr_val):
    if idr_val < 50:
        return "Setara dengan sebutir debu di server (Hampir gratis!)"
    elif idr_val < 500:
        return "Setara dengan harga satu butir permen karet yang udah keras 🍬"
    elif idr_val < 2500:
        return f"Setara dengan biaya kencing di WC Umum Terminal (Tanpa sabun) 🚽"
    elif idr_val < 5000:
        return "Setara dengan bayar parkir motor tapi ga dikasih karcis 🛵"
    elif idr_val < 15000:
        return "Setara dengan satu porsi seblak level 0 (Cuma kerupuk doang) 🥣"
    elif idr_val < 30000:
        return "Setara dengan harga kuota 1GB yang masa aktifnya tinggal 2 jam 📶"
    elif idr_val < 50000:
        return "Setara dengan patungan beli kado buat temen yang ga deket-deket banget 🎁"
    elif idr_val < 100000:
        return "Setara dengan biaya admin ganti kartu ATM yang ketelen 💳"
    else:
        return "Setara dengan harga top-up diamond ML demi skin trial 💎"

# Constant for Receipt CSS
RECEIPT_CSS = """
    .receipt {
        background-color: #fff;
        color: #000;
        font-family: 'Courier New', Courier, monospace;
        padding: 20px;
        border: 1px solid #ddd;
        border-radius: 5px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        max-width: 400px;
        margin: 10px auto;
        line-height: 1.2;
    }
    .receipt-header {
        text-align: center;
        border-bottom: 1px dashed #000;
        margin-bottom: 10px;
        padding-bottom: 10px;
    }
    .receipt-title {
        font-size: 20px;
        font-weight: bold;
    }
    .receipt-item {
        display: flex;
        justify-content: space-between;
        margin: 5px 0;
    }
    .receipt-footer {
        border-top: 1px dashed #000;
        margin-top: 10px;
        padding-top: 10px;
        text-align: center;
    }
    .total {
        font-weight: bold;
        font-size: 18px;
    }
    .analogy {
        font-style: italic;
        color: #555;
        margin-top: 10px;
        font-size: 14px;
    }

    /* Aggressively hide all Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display:none;}
    div[data-testid="stStatusWidget"] {display:none;}
    div[data-testid="stHeader"] {display:none;}
    div[data-testid="stToolbar"] {display:none;}
    div[data-testid="stDecoration"] {display:none;}
    #stDecoration {display:none;}
    .css-1rs6os {display:none;}
    .css-1v8v4p6 {display:none;}
    .st-emotion-cache-18ni7ap {display: none !important;}
    .st-emotion-cache-6qob1r {display: none !important;}
    .st-emotion-cache-z5fcl4 {display: none !important;}
    .st-emotion-cache-1vq4p4l {display: none !important;}
    .st-emotion-cache-12fmjuu {display: none !important;}
"""

def generate_pdf_receipt(usage, model, cost_usd, cost_idr, analogy, timestamp):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=12)
    pdf.cell(200, 10, txt="STRUK AI", ln=True, align='C')
    pdf.cell(200, 10, txt="---------------------------", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Date: {timestamp}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Model: {model}", ln=True, align='C')
    pdf.cell(200, 10, txt="---------------------------", ln=True, align='C')
    pdf.cell(100, 10, txt=f"Input Tokens ({usage['prompt_tokens']})")
    pdf.cell(100, 10, txt=f"${(usage['prompt_tokens'] * (0.15/1e6)):.6f}", ln=True, align='R')
    pdf.cell(100, 10, txt=f"Output Tokens ({usage['completion_tokens']})")
    pdf.cell(100, 10, txt=f"${(usage['completion_tokens'] * (0.60/1e6)):.6f}", ln=True, align='R')
    pdf.cell(200, 10, txt="---------------------------", ln=True, align='C')
    pdf.set_font("Courier", style='B', size=14)
    pdf.cell(100, 10, txt="TOTAL USD")
    pdf.cell(100, 10, txt=f"${cost_usd:.6f}", ln=True, align='R')
    pdf.set_text_color(211, 47, 47)
    pdf.cell(100, 10, txt="TOTAL IDR")
    pdf.cell(100, 10, txt=f"Rp {cost_idr:.2f}", ln=True, align='R')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Courier", style='I', size=10)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=f'"{analogy}"', align='C')
    pdf.ln(10)
    pdf.set_font("Courier", size=8)
    pdf.cell(200, 10, txt="Terima kasih telah berhemat!", ln=True, align='C')
    return bytes(pdf.output())

def print_receipt_button(receipt_html, key):
    html_content = f"""
        <script>
        function printDiv() {{
            var printContents = `{receipt_html}`;
            var originalStyle = `<style>
                {RECEIPT_CSS} 
                body {{ 
                    margin: 0; 
                    padding: 20px; 
                    display: flex; 
                    justify-content: center; 
                    align-items: flex-start;
                    background-color: #f0f2f6;
                }} 
                @media print {{
                    body {{ background-color: white; padding: 0; }}
                    .receipt {{ box-shadow: none; border: none; }}
                }}
            </style>`;
            var win = window.open('', '_blank');
            win.document.write('<html><head><title>Print Receipt - Struk AI</title>');
            win.document.write(originalStyle);
            win.document.write('</head><body>');
            win.document.write(printContents);
            win.document.write('</body></html>');
            win.document.close();
            win.focus();
            setTimeout(function() {{
                win.print();
                win.close();
            }}, 500);
        }}
        </script>
        <button onclick="printDiv()" style="
            background-color: white;
            color: #31333f;
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            padding: 0.45rem 1rem;
            cursor: pointer;
            font-size: 14px;
            width: 100%;
            height: 38px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            font-family: 'Source Sans Pro', sans-serif;
        ">
            🖨️ Print
        </button>
    """
    components.html(html_content, height=45)

# --- APP CONFIG & UI ---

st.set_page_config(page_title="Struk AI - Cost Counter", page_icon="🧾", layout="centered")
st.markdown(f"<style>{RECEIPT_CSS}</style>", unsafe_allow_html=True)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = load_history()
if "context_summary" not in st.session_state:
    st.session_state.context_summary = ""

# API Key check from Environment only
api_key_env = os.getenv("GROQ_API_KEY", "")

# --- SUMMARY LOGIC ---
def summarize_history(messages, client, model):
    if len(messages) < 4: return ""
    prompt = "Summarize the conversation so far in one short paragraph. Focus on key points."
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": history_text}],
            max_tokens=150
        )
        return response.choices[0].message.content
    except:
        return ""

# Sidebar for Config & Actions
with st.sidebar:
    st.title("⚙️ Control Panel")
    
    if not api_key_env:
        st.error("❌ GROQ_API_KEY tidak ditemukan di file .env!")
    else:
        st.success("✅ API Connected")
    
    model_options = [
        "allam-2-7b",
        "groq/compound",
        "groq/compound-mini",
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "meta-llama/llama-prompt-guard-2-22m",
        "meta-llama/llama-prompt-guard-2-86m",
        "deepseek/deepseek-r1",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "openai/gpt-oss-safeguard-20b",
        "qwen/qwen3-32b"
    ]
    
    # Set default to openai/gpt-oss-120b
    default_index = model_options.index("openai/gpt-oss-120b")
    model_name = st.selectbox("Model AI", model_options, index=default_index)
    kurs = st.number_input("Kurs USD -> IDR", value=16000)

    st.divider()
    st.subheader("🧠 Memory Management")
    memory_limit = st.slider("Context Window (Messages)", 2, 20, 10, help="Jumlah pesan terakhir yang dikirim utuh ke AI. Sisanya akan dirangkum.")
    if st.button("🪄 Paksa Rangkum Histori"):
        with st.status("Merangkum..."):
            client = Groq(api_key=api_key_env)
            st.session_state.context_summary = summarize_history(st.session_state.messages, client, model_name)
            st.success("Histori berhasil dirangkum!")
    
    st.divider()
    st.subheader("📊 Statistik & Akumulasi")
    
    if st.button("📈 Hitung Total Belanja", use_container_width=True, type="primary"):
        total_input = 0
        total_output = 0
        for msg in st.session_state.messages:
            if "usage" in msg:
                total_input += msg["usage"]["prompt_tokens"]
                total_output += msg["usage"]["completion_tokens"]
        
        if total_input > 0:
            c_usd, c_idr = calculate_cost(total_input, total_output, model_name, kurs)
            analogy = get_analogy(c_idr)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            accumulated_html = f"""
            <div class="receipt" style="border: 2px solid #000;">
                <div class="receipt-header">
                    <div class="receipt-title">STRUK AKUMULASI</div>
                    <div>{timestamp}</div>
                    <div>Total dari {len([m for m in st.session_state.messages if m['role']=='user'])} prompts</div>
                </div>
                <div class="receipt-item">
                    <span>Total Input Tokens</span>
                    <span>{total_input}</span>
                </div>
                <div class="receipt-item">
                    <span>Total Output Tokens</span>
                    <span>{total_output}</span>
                </div>
                <div class="receipt-item total">
                    <span>TOTAL SPENDING</span>
                    <span>${c_usd:.4f}</span>
                </div>
                <div class="receipt-item total" style="color: #d32f2f;">
                    <span>TOTAL IDR</span>
                    <span>Rp {c_idr:.2f}</span>
                </div>
                <div class="receipt-footer">
                    <div class="analogy">"Total pengeluaranmu {analogy}"</div>
                    <div style="font-weight: bold; margin-top: 10px;">REKAP SELURUH CHAT</div>
                </div>
            </div>
            """
            st.markdown(accumulated_html, unsafe_allow_html=True)
            print_receipt_button(accumulated_html, key="print_accumulated")
        else:
            st.warning("Belum ada data.")

    if st.button("🗑️ Reset Chat & Histori", use_container_width=True):
        st.session_state.messages = []
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        st.rerun()

    st.divider()
    st.markdown("### 💡 Info Harga")
    st.write(f"Model: {model_name}")
    st.write("- Input: $0.15 / 1M")
    st.write("- Output: $0.60 / 1M")

# Main Content
st.title("🧾 Struk AI")
st.caption("Hitung biaya setiap prompt AI kamu dalam bentuk struk belanja!")

# Display Chat History
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "receipt_html" in message:
            st.markdown(message["receipt_html"], unsafe_allow_html=True)
            col1, col2 = st.columns([0.4, 0.6])
            with col1:
                print_receipt_button(message["receipt_html"], key=f"print_{i}")
            with col2:
                # Re-generate PDF on the fly for history display if not present in memory
                # (Since we don't save PDF bytes to JSON to save space)
                usage_data = message.get("usage", {"prompt_tokens": 0, "completion_tokens": 0})
                c_usd, c_idr = calculate_cost(usage_data["prompt_tokens"], usage_data["completion_tokens"], model_name, kurs)
                analogy = get_analogy(c_idr)
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                pdf_bytes = generate_pdf_receipt(usage_data, model_name, c_usd, c_idr, analogy, timestamp)
                
                st.download_button(
                    label=f"📥 Save PDF",
                    data=pdf_bytes,
                    file_name=f"struk_ai_{i}.pdf",
                    mime="application/pdf",
                    key=f"download_{i}",
                    use_container_width=True
                )

# Chat Input
if prompt := st.chat_input("Apa yang ingin kamu tanyakan?"):
    if not api_key_env:
        st.error("GROQ_API_KEY tidak ditemukan di file .env!")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    save_history(st.session_state.messages)
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        client = Groq(api_key=api_key_env)
        
        # Prepare context
        # 1. Start with the summary if it exists
        final_messages = []
        if st.session_state.context_summary:
            final_messages.append({"role": "system", "content": f"Previous conversation summary: {st.session_state.context_summary}"})
        
        # 2. Add only the last N messages based on memory_limit
        recent_messages = st.session_state.messages[-(memory_limit):]
        for m in recent_messages:
            final_messages.append({"role": m["role"], "content": m["content"]})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            completion = client.chat.completions.create(
                model=model_name,
                messages=final_messages,
                stream=False,
            )
            full_response = completion.choices[0].message.content
            usage = completion.usage
            message_placeholder.markdown(full_response)
            
            # Auto-Summarization check: if total messages > memory_limit + 2, trigger auto-summary
            if len(st.session_state.messages) > memory_limit + 2:
                st.session_state.context_summary = summarize_history(st.session_state.messages, client, model_name)

            cost_usd, cost_idr = calculate_cost(usage.prompt_tokens, usage.completion_tokens, model_name, kurs)
            analogy = get_analogy(cost_idr)
            
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Additional line in receipt if summary was used
            summary_note = " (Inc. Summary Context)" if st.session_state.context_summary else ""
            
            receipt_html = f"""
            <div class="receipt">
                <div class="receipt-header">
                    <div class="receipt-title">STRUK AI</div>
                    <div>{timestamp}</div>
                    <div>Model: {model_name}{summary_note}</div>
                </div>
                <div class="receipt-item">
                    <span>Input Tokens ({usage.prompt_tokens})</span>
                    <span>${(usage.prompt_tokens * (0.15/1e6)):.6f}</span>
                </div>
                <div class="receipt-item">
                    <span>Output Tokens ({usage.completion_tokens})</span>
                    <span>${(usage.completion_tokens * (0.60/1e6)):.6f}</span>
                </div>
                <div class="receipt-item total">
                    <span>TOTAL USD</span>
                    <span>${cost_usd:.6f}</span>
                </div>
                <div class="receipt-item total" style="color: #d32f2f;">
                    <span>TOTAL IDR</span>
                    <span>Rp {cost_idr:.2f}</span>
                </div>
                <div class="receipt-footer">
                    <div class="analogy">"{analogy}"</div>
                    <div style="font-size: 10px; margin-top: 10px;">Terima kasih telah berhemat!</div>
                </div>
            </div>
            """
            st.markdown(receipt_html, unsafe_allow_html=True)
            
            col1, col2 = st.columns([0.4, 0.6])
            with col1:
                print_receipt_button(receipt_html, key=f"print_new")
            with col2:
                usage_dict = {"prompt_tokens": usage.prompt_tokens, "completion_tokens": usage.completion_tokens}
                pdf_bytes = generate_pdf_receipt(usage_dict, model_name, cost_usd, cost_idr, analogy, timestamp)
                st.download_button(
                    label="📥 Save PDF",
                    data=pdf_bytes,
                    file_name=f"struk_ai_{int(time.time())}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_response,
                "receipt_html": receipt_html,
                "usage": usage_dict
            })
            save_history(st.session_state.messages)
    except Exception as e:
        st.error(f"Error: {str(e)}")
