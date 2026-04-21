# Struk AI 🧾

Aplikasi sederhana untuk menghitung biaya penggunaan API AI (Groq) dan menampilkan hasilnya dalam bentuk struk belanja kasir yang estetik, lengkap dengan analogi harga barang di kehidupan nyata (seperti gorengan).

## Fitur
- Chat interface mirip ChatGPT.
- Struk belanja otomatis setiap kali ada respon dari AI.
- Hitung biaya berdasarkan token input & output.
- Analogi biaya ke harga gorengan, es teh, atau kopi.
- Support model `openai/gpt-oss-120b` di Groq.

## Cara Instalasi
1. Clone project ini.
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` menjadi `.env` dan isi `GROQ_API_KEY`.
4. Jalankan aplikasi:
   ```bash
   streamlit run app.py
   ```

## Tech Stack
- Python
- Streamlit
- Groq Cloud API
- Custom CSS (Receipt Styling)
