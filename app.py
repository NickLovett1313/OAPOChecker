import streamlit as st
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="PO vs OA Comparator", layout="wide")

st.title("📄 PO vs OA Comparator")
st.write("Upload a Purchase Order and an Order Acknowledgement PDF to compare them for discrepancies.")

uploaded_po = st.file_uploader("Upload Purchase Order (PO)", type=["pdf"], key="po")
uploaded_oa = st.file_uploader("Upload Order Acknowledgement (OA)", type=["pdf"], key="oa")

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def find_lines(text):
    pattern = re.compile(r"(\d{5})\s+(.*?)\s+(\d+\.\d{2})\s+(\d+\.\d{2})\s+(\d{2,4}-[A-Za-z]{3}-\d{4}|[A-Za-z]{3} \d{1,2}, \d{4})", re.MULTILINE)
    return pattern.findall(text)

if uploaded_po and uploaded_oa:
    po_text = extract_text_from_pdf(uploaded_po)
    oa_text = extract_text_from_pdf(uploaded_oa)

    po_lines = find_lines(po_text)
    oa_lines = find_lines(oa_text)

    st.subheader("🔍 Discrepancy Report")

    if not po_lines or not oa_lines:
        st.warning("Could not extract line items from one or both documents. Please ensure they follow a consistent format.")
    else:
        for po_line in po_lines:
            po_id, po_model, po_price, po_total, po_date = po_line
            match_found = False
            for oa_line in oa_lines:
                oa_id, oa_model, oa_price, oa_total, oa_date = oa_line
                if po_id == oa_id:
                    match_found = True
                    issues = []
                    if po_model.strip() != oa_model.strip():
                        issues.append("Model mismatch")
                    if po_price != oa_price:
                        issues.append("Unit price mismatch")
                    if po_total != oa_total:
                        issues.append("Total price mismatch")
                    if po_date != oa_date:
                        issues.append("Ship date mismatch")
                    if issues:
                        st.error(f"Line {po_id}: " + ", ".join(issues))
                    break
            if not match_found:
                st.warning(f"Line {po_id} not found in OA.")