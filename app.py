
import streamlit as st
import pandas as pd
from google import genai
from google.genai import types

st.set_page_config(
    page_title="DataInsight Bot",
    page_icon="📊",
    layout="wide"
)

st.title("📊 DataInsight Bot")
st.caption("Asisten analisis data berbasis Gemini AI")

with st.sidebar:
    st.header("Pengaturan")
    st.write("AI: Google Gemini")
    st.write("Analisis: Python + Pandas")
    st.info(
        "Unggah CSV atau Excel untuk mulai "
        "menganalisis data."
    )

    uploaded_file = st.file_uploader(
        "Unggah dataset",
        type=["csv", "xlsx"]
    )

    if st.button("Hapus percakapan"):
        st.session_state.messages = []
        st.rerun()

# Membaca dataset
df = None

if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("📁 Dataset")
        col1, col2, col3 = st.columns(3)

        col1.metric("Jumlah Baris", f"{len(df):,}")
        col2.metric("Jumlah Kolom", len(df.columns))
        col3.metric(
            "Nilai Kosong",
            f"{int(df.isna().sum().sum()):,}"
        )

        with st.expander("Lihat data", expanded=True):
            st.dataframe(df.head(100), use_container_width=True)

        with st.expander("Statistik deskriptif"):
            st.dataframe(
                df.describe(include="all").transpose(),
                use_container_width=True
            )

        with st.expander("Nilai kosong per kolom"):
            missing = df.isna().sum().rename("Nilai Kosong")
            st.dataframe(missing.to_frame())

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_columns:
            st.subheader("📈 Grafik")
            selected_column = st.selectbox(
                "Pilih kolom numerik",
                numeric_columns
            )
            st.bar_chart(df[selected_column].dropna())

    except Exception as error:
        st.error(f"File gagal dibaca: {error}")
        df = None

# Menyimpan percakapan
if "messages" not in st.session_state:
    st.session_state.messages = []

# Menampilkan percakapan sebelumnya
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input(
    "Tanyakan sesuatu tentang data atau topik lainnya..."
)

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)

        system_instruction = """
        Kamu adalah DataInsight Bot, asisten AI untuk analisis data.
        Jawab menggunakan bahasa Indonesia yang jelas dan ramah.
        Jelaskan konsep data science dengan bahasa yang mudah dipahami.
        Jangan mengarang angka atau hasil analisis.
        Bedakan fakta yang dihitung dari data dan interpretasi AI.
        Jika informasi tidak tersedia, katakan dengan jujur.
        """

        data_context = (
            "Belum ada dataset yang diunggah."
        )

        if df is not None:
            data_context = f"""
            Nama file: {uploaded_file.name}
            Jumlah baris: {len(df)}
            Jumlah kolom: {len(df.columns)}
            Nama kolom: {df.columns.tolist()}
            Tipe data:
            {df.dtypes.astype(str).to_dict()}
            Nilai kosong:
            {df.isna().sum().to_dict()}
            Statistik deskriptif:
            {df.describe(include="all").to_string()}
            Contoh maksimal 10 baris:
            {df.head(10).to_string(index=False)}
            """

        history = []
        for message in st.session_state.messages[-10:]:
            role = (
                "Pengguna"
                if message["role"] == "user"
                else "Asisten"
            )
            history.append(f"{role}: {message['content']}")

        prompt = f"""
        {system_instruction}

        KONTEKS DATASET:
        {data_context}

        RIWAYAT PERCAKAPAN:
        {"".join(history)}

        Berikan jawaban untuk pertanyaan terakhir pengguna.
        """

        with st.chat_message("assistant"):
            with st.spinner("Gemini sedang berpikir..."):
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3
                    )
                )
                answer = response.text or (
                    "Maaf, AI belum menghasilkan jawaban teks."
                )
                st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

    except Exception as error:
        st.error(
            "Terjadi kendala saat menghubungi Gemini. "
            "Periksa API key, koneksi internet, akses model, "
            "dan batas penggunaan API."
        )
        st.caption(f"Detail kendala: {error}")
