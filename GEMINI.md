# Project: AI Receipt (Struk AI) 🧾

Project freelance untuk aplikasi penghitung cost prompting AI dengan output berupa struk kasir dan analogi biaya hidup sehari-hari (gorengan, kopi, dsb).

## Tech Stack
- **Language:** Python 3.x
- **Frontend/UI:** Streamlit
- **AI Engine:** Groq API (Model: `openai/gpt-oss-120b`)
- **Cost Calculation:** Custom logic berdasarkan pricing Groq per 1M token.

## Core Features
1. **ChatGPT-like Chat Interface:** Menggunakan native Streamlit chat elements.
2. **Dynamic Receipt Component:** Menampilkan struk belanja setiap kali AI selesai merespon.
3. **Analogy Engine:** Mengonversi total biaya (USD -> IDR) menjadi jumlah gorengan atau kebutuhan sehari-hari lainnya.
4. **Downloadable Receipt:** (Optional/Future) Fitur untuk simpan struk.

## Pricing Logic (Groq - GPT-OSS 120B)
- **Input:** $0.15 / 1.000.000 tokens
- **Output:** $0.60 / 1.000.000 tokens
- **Kurs Estimasi:** Rp 16.000 (Adjustable)

## Directory Structure
- `app.py`: Entry point aplikasi.
- `requirements.txt`: Daftar library yang dibutuhkan.
- `.env`: API Key storage (diabaikan oleh git).
- `utils/`: Logic untuk hitung-hitungan cost.
