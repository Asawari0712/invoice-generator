import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from io import BytesIO
from datetime import date
from xml.sax.saxutils import escape

st.set_page_config(page_title="Invoice Generator", page_icon="🧾")
st.title("🧾 Automatic Invoice Generator")
st.caption("Create and download professional PDF invoices.")

st.header("Customer Details")
customer = st.text_input("Customer Name", "Priya Stationery")
invoice_no = st.text_input("Invoice Number", "INV-001")
invoice_date = st.date_input("Invoice Date", date.today())

st.header("Products")
if "items" not in st.session_state:
    st.session_state.items = [
        {"name": "Notebook", "qty": 5, "price": 40.0},
        {"name": "Pen", "qty": 10, "price": 5.0}
    ]

for i, item in enumerate(st.session_state.items):
    st.subheader(f"Product {i + 1}")
    c1, c2, c3 = st.columns([3, 1, 2])
    item["name"] = c1.text_input("Product", item["name"], key=f"n{i}")
    item["qty"] = c2.number_input("Quantity", min_value=1, step=1, value=item["qty"], key=f"q{i}")
    item["price"] = c3.number_input("Price (₹)", min_value=0.0, value=float(item["price"]), step=1.0, key=f"p{i}")

c1, c2 = st.columns(2)
if c1.button("➕ Add Product"):
    st.session_state.items.append({"name": "", "qty": 1, "price": 0.0})
    st.rerun()

if c2.button("➖ Remove Last"):
    if len(st.session_state.items) > 1:
        st.session_state.items.pop()
        st.rerun()

subtotal = sum(x["qty"] * x["price"] for x in st.session_state.items)
tax_rate = st.number_input("Tax (%)", min_value=0.0, max_value=100.0, value=0.0)
tax = subtotal * tax_rate / 100
total = subtotal + tax

st.header("Invoice Summary")
c1, c2 = st.columns(2)
c1.metric("Subtotal", f"₹{subtotal:,.2f}")
c2.metric("Grand Total", f"₹{total:,.2f}")
st.write(f"Tax amount: ₹{tax:,.2f}")

def create_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("INVOICE", styles["Title"]),
        Spacer(1, 15),
        Paragraph(f"Invoice No: {escape(invoice_no)}", styles["Normal"]),
        Paragraph(f"Date: {invoice_date.strftime('%d-%m-%Y')}", styles["Normal"]),
        Paragraph(f"Customer: {escape(customer)}", styles["Normal"]),
        Spacer(1, 20)
    ]

    data = [["Product", "Quantity", "Unit Price", "Amount"]]
    for x in st.session_state.items:
        data.append([
            escape(x["name"]),
            str(x["qty"]),
            f"Rs. {x['price']:.2f}",
            f"Rs. {x['qty'] * x['price']:.2f}"
        ])

    data.extend([
        ["", "", "Subtotal", f"Rs. {subtotal:.2f}"],
        ["", "", f"Tax ({tax_rate:g}%)", f"Rs. {tax:.2f}"],
        ["", "", "GRAND TOTAL", f"Rs. {total:.2f}"]
    ])

    table = Table(data, colWidths=[220, 70, 90, 100], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243B53")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -4), 0.5, colors.grey),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#DCEFE5")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8)
    ]))
    story.append(table)
    story.append(Spacer(1, 15))
    story.append(Paragraph("Thank you for your business!", styles["Normal"]))
    doc.build(story)
    return buffer.getvalue()

st.header("Download Invoice")
if st.button("Generate PDF Invoice", type="primary"):
    if not customer.strip() or not invoice_no.strip():
        st.error("Enter the customer name and invoice number.")
    elif any(not x["name"].strip() for x in st.session_state.items):
        st.error("Enter a name for every product.")
    else:
        pdf = create_pdf()
        st.success("Invoice created successfully!")
        st.download_button(
            "⬇️ Download PDF",
            data=pdf,
            file_name=f"{invoice_no}.pdf",
            mime="application/pdf"
        )
