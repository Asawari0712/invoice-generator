import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from io import BytesIO
from datetime import date
from xml.sax.saxutils import escape

# Page settings
st.set_page_config(
    page_title="Invoice Generator",
    page_icon="🧾",
    layout="centered"
)

st.title("🧾 Automatic Invoice Generator")
st.caption("Create and download professional PDF invoices.")

# Customer details
st.header("1. Customer Details")

customer = st.text_input("Customer Name", "Priya Stationery")
invoice_no = st.text_input("Invoice Number", "INV-001")
invoice_date = st.date_input("Invoice Date", date.today())

# Initialize products
if "items" not in st.session_state:
    st.session_state["items"] = [
        {"name": "Notebook", "qty": 5, "price": 40.0},
        {"name": "Pen", "qty": 10, "price": 5.0}
    ]

# Product section
st.header("2. Products")

for i, item in enumerate(st.session_state["items"]):
    st.subheader(f"Product {i + 1}")

    c1, c2, c3 = st.columns([3, 1, 2])

    item["name"] = c1.text_input(
        "Product Name",
        value=item["name"],
        key=f"name_{i}"
    )

    item["qty"] = c2.number_input(
        "Quantity",
        min_value=1,
        step=1,
        value=item["qty"],
        key=f"qty_{i}"
    )

    item["price"] = c3.number_input(
        "Price (₹)",
        min_value=0.0,
        step=1.0,
        value=float(item["price"]),
        key=f"price_{i}"
    )

# Add or remove products
c1, c2 = st.columns(2)

if c1.button("➕ Add Product"):
    st.session_state["items"].append(
        {"name": "", "qty": 1, "price": 0.0}
    )
    st.rerun()

if c2.button("➖ Remove Last"):
    if len(st.session_state["items"]) > 1:
        st.session_state["items"].pop()
        st.rerun()

# Calculate totals
subtotal = sum(
    item["qty"] * item["price"]
    for item in st.session_state["items"]
)

st.header("3. Invoice Summary")

tax_rate = st.number_input(
    "Optional Tax (%)",
    min_value=0.0,
    max_value=100.0,
    value=0.0,
    step=1.0
)

tax_amount = subtotal * tax_rate / 100
grand_total = subtotal + tax_amount

c1, c2 = st.columns(2)
c1.metric("Subtotal", f"₹{subtotal:,.2f}")
c2.metric("Grand Total", f"₹{grand_total:,.2f}")

st.write(f"Tax Amount: ₹{tax_amount:,.2f}")

# Generate PDF
def create_pdf():
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("INVOICE", styles["Title"]))
    story.append(Spacer(1, 15))

    story.append(Paragraph(
        f"<b>Invoice Number:</b> {escape(invoice_no.strip())}",
        styles["Normal"]
    ))

    story.append(Paragraph(
        f"<b>Date:</b> {invoice_date.strftime('%d-%m-%Y')}",
        styles["Normal"]
    ))

    story.append(Paragraph(
        f"<b>Customer:</b> {escape(customer.strip())}",
        styles["Normal"]
    ))

    story.append(Spacer(1, 20))

    data = [
        ["Product", "Quantity", "Unit Price", "Amount"]
    ]

    for item in st.session_state["items"]:
        data.append([
            escape(item["name"].strip()),
            str(item["qty"]),
            f"Rs. {item['price']:,.2f}",
            f"Rs. {item['qty'] * item['price']:,.2f}"
        ])

    data.extend([
        ["", "", "Subtotal", f"Rs. {subtotal:,.2f}"],
        ["", "", f"Tax ({tax_rate:g}%)",
         f"Rs. {tax_amount:,.2f}"],
        ["", "", "GRAND TOTAL", f"Rs. {grand_total:,.2f}"]
    ])

    table = Table(
        data,
        colWidths=[220, 70, 90, 100],
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#243B53")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -4), 0.5, colors.lightgrey),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("BACKGROUND", (0, -1), (-1, -1),
         colors.HexColor("#DCEFE5")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8)
    ]))

    story.append(table)
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "Thank you for your business!",
        styles["Normal"]
    ))

    doc.build(story)
    buffer.seek(0)

    return buffer.getvalue()

# Validate and download
st.header("4. Download Invoice")

if st.button("Generate PDF Invoice", type="primary"):

    if not customer.strip():
        st.error("Please enter the customer name.")

    elif not invoice_no.strip():
        st.error("Please enter an invoice number.")

    elif any(
        not item["name"].strip()
        for item in st.session_state["items"]
    ):
        st.error("Please enter a name for every product.")

    else:
        pdf_bytes = create_pdf()

        st.success("Invoice created successfully!")

        st.download_button(
            label="⬇️ Download Invoice PDF",
            data=pdf_bytes,
            file_name=f"{invoice_no.strip()}.pdf",
            mime="application/pdf"
        )
