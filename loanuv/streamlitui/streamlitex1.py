import streamlit as st


uploaded_file = st.file_uploader("Choose a file")



from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

data = "Hello, this is your file content"

buffer = BytesIO()
doc = SimpleDocTemplate(buffer)
styles = getSampleStyleSheet()

content = []
content.append(Paragraph(data, styles["Normal"]))

doc.build(content)
buffer.seek(0)

st.download_button(
    label="Download PDF",
    data=buffer,
    file_name="output.pdf",
    mime="application/pdf"
)