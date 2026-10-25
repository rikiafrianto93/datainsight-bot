
# DataInsight Bot

DataInsight Bot adalah aplikasi chatbot AI untuk membantu
pengguna memahami dan mengeksplorasi data menggunakan
bahasa alami.

## Fitur
- Chatbot berbasis Google Gemini API.
- Unggah file CSV dan Excel.
- Ringkasan jumlah baris dan kolom.
- Pemeriksaan nilai kosong.
- Statistik deskriptif.
- Visualisasi kolom numerik.
- Tanya jawab berbasis konteks dataset.

## Teknologi
- Python
- Streamlit
- Google Gemini API
- Pandas
- OpenPyXL

## Instalasi
1. Clone repositori.
2. Buat virtual environment.
3. Instal dependensi:

   pip install -r requirements.txt

4. Buat `.streamlit/secrets.toml` dan isi API key.
5. Jalankan aplikasi:

   streamlit run app.py

## Keamanan
Jangan unggah API key ke repositori.
Jangan gunakan dataset rahasia atau data pribadi
tanpa izin yang sesuai.
