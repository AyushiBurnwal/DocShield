import streamlit as st
from pathlib import Path
import tempfile

from extract import extract
from profiler import profile_dataframe
from charts import make_charts
from summariser import summarise
from detector import detect, detection_summary
from mapper import build_map, build_redaction_targets
from eraser import redact_pdf


st.set_page_config(
    page_title="DocShield",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ DocShield")
st.write("AI-Powered PDF Analysis & Data Protection System")


uploaded_file = st.file_uploader(
    "Upload a PDF document",
    type=["pdf"]
)


if uploaded_file:

    # Save uploaded PDF temporarily
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as temp_file:

        temp_file.write(uploaded_file.getbuffer())
        pdf_path = Path(temp_file.name)

    st.success("PDF uploaded successfully!")

    # -------------------------
    # 1. PDF EXTRACTION
    # -------------------------
    st.header("1. PDF Extraction")

    result = extract(pdf_path)

    st.success("PDF extraction completed.")

    # -------------------------
    # 2. DATA PROCESSING
    # -------------------------
    st.header("2. Data Profile")

    df = result.primary_table

    if df is not None and not df.empty:

        profile = profile_dataframe(df)

        st.dataframe(df)

        st.write("Rows:", profile["rows"])
        st.write("Columns:", profile["columns"])
        st.write("Missing Values:", profile["missing_values"])
        st.write("Duplicate Rows:", profile["duplicate_rows"])

    else:
        st.warning("No table data was found in the PDF.")

    # -------------------------
    # 3. VISUALIZATION
    # -------------------------
    st.header("3. Visualizations")

    if df is not None and not df.empty:

        charts = make_charts(df)

        for chart_name, figure in charts.items():

            if figure is not None:
                st.subheader(chart_name.title())
                st.plotly_chart(
                    figure,
                    use_container_width=True
                )

    # -------------------------
    # 4. AI SUMMARY
    # -------------------------
    st.header("4. AI Summary")

    if df is not None and not df.empty:

        summary = summarise(
            df,
            profile=profile,
            use_ai=True
        )

        st.write(summary)

    # -------------------------
    # 5. SENSITIVE DATA
    # -------------------------
    st.header("5. Sensitive Data Detection")

    findings = detect(result)

    st.write(
        detection_summary(findings)
    )

    # -------------------------
    # 6. ENTITY MAPPING
    # -------------------------
    st.header("6. Entity Mapping")

    entity_map = build_map(findings)

    st.json(entity_map)

    # -------------------------
    # 7. PDF REDACTION
    # -------------------------
    st.header("7. PDF Redaction")

    if findings:

        output_path = pdf_path.with_name(
            "redacted_" + uploaded_file.name
        )

        redact_pdf(
            pdf_path,
            output_path,
            findings
        )

        st.success("PDF redaction completed.")

        with open(output_path, "rb") as file:

            st.download_button(
                label="Download Redacted PDF",
                data=file,
                file_name="redacted_" + uploaded_file.name,
                mime="application/pdf"
            )

    else:

        st.info(
            "No sensitive information was detected."
        )