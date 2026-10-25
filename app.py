
import streamlit as st
import pandas as pd
import time
from google import genai
from google.genai import types


# ==================================================
# 1. IDENTITAS APLIKASI
# ==================================================
st.set_page_config(
    page_title="DataInsight Bot by Riki",
    page_icon="📊",
    layout="wide"
)

# Judul utama
st.title("📊 DataInsight Bot by Riki")

st.markdown(
    """
    <p style="
        color: #64748b;
        font-size: 16px;
        margin-top: -12px;
    ">
        AI-Powered Data Analysis Dashboard
        &nbsp; | &nbsp; Developed by Riki
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# Pengantar aplikasi
st.markdown(
    """
    ### Ubah Data Menjadi Insight

    Selamat datang di **DataInsight Bot by Riki**.

    Aplikasi ini membantu Anda memahami dataset melalui
    ringkasan statistik, pemeriksaan kualitas data,
    visualisasi, dan analisis otomatis menggunakan
    Google Gemini AI.

    **Mulai dengan mengunggah file CSV atau Excel melalui
    sidebar di sebelah kiri.**
    """
)

st.caption(
    "Python · Pandas · Streamlit · Google Gemini API"
)

# ==================================================
# 2. FUNGSI GEMINI
# ==================================================



def ask_gemini(prompt):
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)

    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3
                )
            )

            return response.text or (
                "AI belum menghasilkan jawaban teks."
            )

        except Exception as error:
            error_message = str(error).upper()

            temporary_error = any(
                code in error_message
                for code in [
                    "503",
                    "UNAVAILABLE",
                    "429",
                    "RESOURCE_EXHAUSTED",
                    "500",
                    "502",
                    "504"
                ]
            )

            if temporary_error and attempt < max_attempts - 1:
                wait_seconds = 2 ** (attempt + 1)
                time.sleep(wait_seconds)
            else:
                raise


# ==================================================
# 3. SIDEBAR
# ==================================================
with st.sidebar:
    st.header("⚙️ Pengaturan")

    st.write("**Pengembang:** Riki")
    st.write("**AI:** Google Gemini")
    st.write("**Pengolahan data:** Python + Pandas")

    st.info(
        "Unggah file CSV atau Excel untuk memulai analisis."
    )

    uploaded_file = st.file_uploader(
        "📁 Unggah dataset",
        type=["csv", "xlsx"]
    )

    if st.button("🗑️ Hapus percakapan"):
        st.session_state.messages = []
        st.rerun()


# ==================================================
# 4. MEMBACA DATASET
# ==================================================
df = None

if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        if df.empty:
            st.warning("Dataset tidak memiliki baris data.")
            df = None

    except Exception as error:
        st.error(f"File gagal dibaca: {error}")


# ==================================================
# 5. DASHBOARD ANALISIS
# ==================================================
if df is not None:
    st.divider()
    st.subheader("📌 Ringkasan Dataset")
    st.caption(f"File yang dianalisis: {uploaded_file.name}")

    total_rows = len(df)
    total_columns = len(df.columns)
    total_missing = int(df.isna().sum().sum())
    total_duplicates = int(df.duplicated().sum())

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Jumlah Baris", f"{total_rows:,}")
    col2.metric("Jumlah Kolom", f"{total_columns:,}")
    col3.metric("Nilai Kosong", f"{total_missing:,}")
    col4.metric("Baris Duplikat", f"{total_duplicates:,}")

    # ----------------------------------------------
    # Tab dashboard
    # ----------------------------------------------
    tab_data, tab_quality, tab_chart, tab_insight = st.tabs([
        "📄 Data",
        "🔎 Kualitas Data",
        "📈 Visualisasi",
        "💡 Insight Otomatis"
    ])

    with tab_data:
        st.markdown("#### Pratinjau Dataset")
        st.dataframe(
            df.head(100),
            use_container_width=True,
            height=350
        )

        with st.expander("Statistik deskriptif"):
            st.dataframe(
                df.describe(include="all").transpose(),
                use_container_width=True
            )

    with tab_quality:
        st.markdown("#### Pemeriksaan Kualitas Data")

        missing = df.isna().sum()
        missing_table = pd.DataFrame({
            "Kolom": missing.index.astype(str),
            "Nilai Kosong": missing.values,
            "Persentase Kosong (%)": (
                missing.values / len(df) * 100
            ).round(2)
        })

        st.dataframe(
            missing_table,
            use_container_width=True,
            hide_index=True
        )

        if total_missing == 0:
            st.success("Tidak ditemukan nilai kosong.")
        else:
            st.warning(
                f"Ditemukan {total_missing:,} nilai kosong. "
                "Periksa kolom yang memiliki nilai kosong."
            )

        if total_duplicates > 0:
            st.warning(
                f"Ditemukan {total_duplicates:,} baris yang "
                "memiliki nilai sama pada seluruh kolom. "
                "Periksa sebelum memutuskan untuk menghapusnya."
            )
        else:
            st.success("Tidak ditemukan baris duplikat.")

        with st.expander("Tipe data setiap kolom"):
            type_table = pd.DataFrame({
                "Kolom": df.columns.astype(str),
                "Tipe Data": df.dtypes.astype(str).values
            })
            st.dataframe(
                type_table,
                use_container_width=True,
                hide_index=True
            )

    with tab_chart:
        st.markdown("#### Eksplorasi Visual")

        numeric_columns = df.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_columns:
            selected_column = st.selectbox(
                "Pilih kolom numerik",
                numeric_columns
            )

            numeric_data = df[selected_column].dropna()

            if not numeric_data.empty:
                st.markdown(f"**Distribusi nilai: {selected_column}**")
                st.bar_chart(numeric_data, use_container_width=True)

                chart_col1, chart_col2 = st.columns(2)
                chart_col1.metric(
                    "Rata-rata",
                    f"{numeric_data.mean():,.2f}"
                )
                chart_col2.metric(
                    "Median",
                    f"{numeric_data.median():,.2f}"
                )
            else:
                st.info("Kolom ini tidak memiliki nilai numerik terisi.")
        else:
            st.info(
                "Belum ada kolom numerik yang dapat divisualisasikan."
            )

        categorical_columns = df.select_dtypes(
            include=["object", "category", "bool"]
        ).columns.tolist()

        if categorical_columns:
            st.markdown("#### Perbandingan Kategori")

            selected_category = st.selectbox(
                "Pilih kolom kategori",
                categorical_columns,
                key="selected_category"
            )

            category_counts = (
                df[selected_category]
                .fillna("(Kosong)")
                .astype(str)
                .value_counts()
                .head(10)
            )

            st.bar_chart(
                category_counts,
                use_container_width=True
            )

            st.caption(
                "Grafik menampilkan maksimal 10 kategori teratas."
            )

    # ----------------------------------------------
    # INSIGHT OTOMATIS
    # ----------------------------------------------
    with tab_insight:
        st.markdown("#### 💡 Temukan Insight dari Data")

        st.write(
            "Pandas menghitung ringkasan data terlebih dahulu. "
            "Gemini kemudian membantu menjelaskan temuan "
            "berdasarkan ringkasan tersebut."
        )

        if st.button(
            "✨ Buat Insight Otomatis",
            type="primary",
            key="generate_insight"
        ):
            with st.spinner("Menghitung dan menyusun insight..."):
                try:
                    numeric_df = df.select_dtypes(
                        include="number"
                    )

                    numeric_summary = (
                        numeric_df.describe().round(2).to_string()
                        if not numeric_df.empty
                        else "Tidak ada kolom numerik."
                    )

                    missing_summary = (
                        df.isna().sum().to_string()
                    )

                    duplicate_count = int(df.duplicated().sum())

                    category_summaries = []
                    categorical_columns = df.select_dtypes(
                        include=["object", "category", "bool"]
                    ).columns.tolist()

                    for column in categorical_columns[:10]:
                        top_values = (
                            df[column]
                            .fillna("(Kosong)")
                            .astype(str)
                            .value_counts()
                            .head(5)
                            .to_dict()
                        )
                        category_summaries.append(
                            f"{column}: {top_values}"
                        )

                    category_context = (
                        "\n".join(category_summaries)
                        if category_summaries
                        else "Tidak ada kolom kategori."
                    )

                    dataset_context = f"""
                    NAMA FILE: {uploaded_file.name}
                    JUMLAH BARIS: {len(df)}
                    JUMLAH KOLOM: {len(df.columns)}
                    NAMA KOLOM: {df.columns.tolist()}
                    TIPE DATA:
                    {df.dtypes.astype(str).to_dict()}

                    STATISTIK NUMERIK:
                    {numeric_summary}

                    NILAI KOSONG PER KOLOM:
                    {missing_summary}

                    JUMLAH BARIS DUPLIKAT:
                    {duplicate_count}

                    LIMA KATEGORI TERATAS PER KOLOM:
                    {category_context}
                    """

                    prompt = f"""
                    Kamu adalah analis data pada DataInsight Bot by Riki.

                    Analisis dataset berikut dengan bahasa Indonesia
                    yang jelas, profesional, dan mudah dipahami.

                    Gunakan hanya fakta dan angka yang tersedia
                    dalam ringkasan data di bawah ini. Jangan
                    mengarang angka, hubungan sebab-akibat,
                    atau kesimpulan yang tidak didukung data.

                    {dataset_context}

                    Susun laporan dengan bagian berikut:
                    1. Gambaran umum dataset.
                    2. Tiga sampai lima temuan utama yang benar-benar
                       didukung oleh ringkasan data.
                    3. Kondisi kualitas data yang perlu diperhatikan.
                    4. Hal yang menarik atau perlu ditelusuri lebih lanjut.
                    5. Saran analisis berikutnya.

                    Jika data tidak cukup untuk menghasilkan sejumlah
                    temuan tertentu, sampaikan secara jujur.
                    Bedakan fakta statistik dari interpretasi.
                    Jangan menyimpulkan sebab-akibat hanya dari
                    statistik deskriptif.
                    """

                    insight = ask_gemini(prompt)

                    st.session_state.auto_insight = insight

                except Exception as error:
                    st.error(
                        "Insight gagal dibuat. Periksa koneksi, "
                        "API key, akses model, dan batas penggunaan API."
                    )
                    st.caption(f"Detail kendala: {error}")

        if st.session_state.get("auto_insight"):
            st.markdown("---")
            st.markdown("### Hasil Analisis")
            st.markdown(st.session_state.auto_insight)

            st.download_button(
                "⬇️ Unduh Insight (.txt)",
                data=st.session_state.auto_insight,
                file_name="insight_datainsight_by_riki.txt",
                mime="text/plain"
            )

else:
    st.info(
        "👈 Unggah dataset CSV atau Excel melalui sidebar "
        "untuk melihat dashboard analisis."
    )


# ==================================================
# 6. CHAT DENGAN GEMINI
# ==================================================
st.divider()
st.subheader("💬 Tanya Data dengan AI")

st.caption(
    "Ajukan pertanyaan tentang dataset atau konsep data science."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input(
    "Contoh: Apa temuan utama dari dataset ini?"
)

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    try:
        data_context = "Belum ada dataset yang diunggah."

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
            history.append(
                f"{role}: {message['content']}"
            )

        prompt = f"""
        Kamu adalah DataInsight Bot by Riki, asisten AI
        untuk analisis data.

        Jawab dalam bahasa Indonesia yang jelas dan ramah.
        Jelaskan konsep data science dengan bahasa sederhana.
        Jangan mengarang angka atau hasil analisis.
        Bedakan fakta dari interpretasi.

        KONTEKS DATASET:
        {data_context}

        RIWAYAT PERCAKAPAN:
        {"".join(history)}

        Jawab pertanyaan terakhir pengguna.
        """

        with st.chat_message("assistant"):
            with st.spinner("Gemini sedang berpikir..."):
                answer = ask_gemini(prompt)
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
