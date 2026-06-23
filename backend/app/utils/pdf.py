import io
from typing import List
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from app.utils.time import now_utc

BRAND = colors.HexColor("#2A4B3C")
ACCENT = colors.HexColor("#C49A45")
MUTED = colors.HexColor("#57534E")
DARK = colors.HexColor("#1C1917")
LIGHT_BG = colors.HexColor("#FDFBF7")
RULE = colors.HexColor("#E8E4D9")


def pdf_table_response(title: str, headers: List[str], rows: List[List[str]], filename: str, subtitle: str = "") -> StreamingResponse:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), topMargin=30, bottomMargin=30, leftMargin=30, rightMargin=30)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=18, textColor=BRAND)
    sub_style = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=10, textColor=MUTED)

    elements = [Paragraph(title, title_style), Spacer(1, 6)]
    if subtitle:
        elements += [Paragraph(subtitle, sub_style), Spacer(1, 6)]
    elements += [Paragraph(f"Generated: {now_utc().strftime('%Y-%m-%d %H:%M UTC')}", sub_style), Spacer(1, 12)]

    table = Table([headers] + rows, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.25, RULE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    doc.build(elements)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def pdf_receipt_response(c: dict, member: dict) -> StreamingResponse:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=40, bottomMargin=40, leftMargin=48, rightMargin=48)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("Title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=22, textColor=BRAND, alignment=0)
    label_style = ParagraphStyle("Lbl", parent=styles["Normal"], fontSize=8, textColor=MUTED, leading=10, spaceAfter=2)
    value_style = ParagraphStyle("Val", parent=styles["Normal"], fontSize=11, textColor=DARK, leading=14)
    small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=9, textColor=MUTED)
    big_amount = ParagraphStyle("Amt", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=28, textColor=BRAND, alignment=0)

    elements = []

    header_tbl = Table([[
        Paragraph("OFFICIAL RECEIPT", ParagraphStyle("H", parent=styles["Normal"], fontSize=9, textColor=ACCENT, leading=12, spaceAfter=4)),
    ], [
        Paragraph("Church Management System", title_style),
    ]], colWidths=[None])
    header_tbl.setStyle(TableStyle([("BOTTOMPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0)]))
    elements += [header_tbl, Spacer(1, 6),
                 Paragraph(f"Receipt No: <b>{c['receipt_no']}</b> &nbsp;&nbsp;|&nbsp;&nbsp; Date: <b>{c['contribution_date']}</b>", small),
                 Spacer(1, 18)]

    member_name = f"{member.get('first_name', '')} {member.get('last_name', '')}".strip() or c.get("member_name", "")
    member_tbl = Table([
        [Paragraph("RECEIVED FROM", label_style)],
        [Paragraph(member_name, value_style)],
        [Paragraph(f"Member ID: {member.get('member_id', c.get('member_external_id', ''))}", small)],
    ], colWidths=[None])
    member_tbl.setStyle(TableStyle([("BOTTOMPADDING", (0, 0), (-1, -1), 1), ("TOPPADDING", (0, 0), (-1, -1), 1)]))
    elements += [member_tbl, Spacer(1, 14)]

    amount_box = Table([
        [Paragraph("AMOUNT RECEIVED", label_style)],
        [Paragraph(f"INR {c['amount']:,.2f}", big_amount)],
    ], colWidths=[None])
    amount_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F2EA")),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements += [amount_box, Spacer(1, 18)]

    detail_rows = [
        ["Contribution Type", c.get("contribution_type", "")],
        ["Payment Mode", c.get("payment_mode", "")],
        ["Reference No.", c.get("reference_no") or "—"],
        ["Currency", "INR"],
        ["Recorded By", c.get("recorded_by", "")],
        ["Notes", c.get("notes") or "—"],
    ]
    details = Table(detail_rows, colWidths=[140, None])
    details.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
        ("TEXTCOLOR", (1, 0), (1, -1), DARK),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("LINEBELOW", (0, 0), (-1, -2), 0.25, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements += [details, Spacer(1, 24)]

    elements += [
        Paragraph("Thank you for your faithful giving.", ParagraphStyle("F1", parent=styles["Normal"], fontSize=11, textColor=BRAND, fontName="Helvetica-Oblique")),
        Spacer(1, 24),
        Table([["", ""]], colWidths=[180, 180], style=TableStyle([
            ("LINEABOVE", (0, 0), (0, 0), 0.5, DARK),
            ("LINEABOVE", (1, 0), (1, 0), 0.5, DARK),
        ])),
        Table([[Paragraph("Authorized signature", small), Paragraph("Recipient signature", small)]], colWidths=[180, 180]),
        Spacer(1, 30),
        Paragraph(f"Generated {now_utc().strftime('%Y-%m-%d %H:%M UTC')} · This is a system-generated receipt.", small),
    ]

    doc.build(elements)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="receipt_{c["receipt_no"]}.pdf"'},
    )
