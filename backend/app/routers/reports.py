from datetime import datetime, timedelta
from typing import Optional, Literal
from fastapi import APIRouter, HTTPException, Depends, Query

from app.auth import require_role
from app.storage.deps import get_storage
from app.storage.base import Storage
from app.utils.time import now_utc
from app.utils.pdf import pdf_table_response
from app.utils.excel import xlsx_response

router = APIRouter(prefix="/reports", tags=["reports"])

Format = Literal["pdf", "excel"]


@router.get("/members")
async def report_members(
    format: Format = "excel",
    status: Optional[str] = None,
    user: dict = Depends(require_role("staff")),
    storage: Storage = Depends(get_storage),
):
    docs = await storage.members.list(status=status, limit=5000)
    headers = ["Member ID", "Full Name", "Gender", "DOB", "Status", "Phone", "Email", "City"]
    rows = [
        [
            d.get("member_id", ""), f"{d.get('first_name', '')} {d.get('last_name', '')}",
            d.get("gender", ""), d.get("date_of_birth", ""), d.get("membership_status", ""),
            d.get("phone_primary", ""), d.get("email", ""), d.get("address_city", ""),
        ]
        for d in docs
    ]
    if format == "excel":
        return xlsx_response(headers, rows, "Members", "member_directory.xlsx")
    return pdf_table_response("Member Directory", headers, rows, "member_directory.pdf")


@router.get("/birthdays")
async def report_birthdays(
    month: int = Query(..., ge=1, le=12),
    format: Format = "excel",
    user: dict = Depends(require_role("staff")),
    storage: Storage = Depends(get_storage),
):
    docs = await storage.members.list(birthday_month=month, limit=5000)
    headers = ["Member ID", "Full Name", "DOB", "Phone", "Email"]
    rows = [
        [
            d.get("member_id", ""), f"{d.get('first_name', '')} {d.get('last_name', '')}",
            d.get("date_of_birth", ""), d.get("phone_primary", ""), d.get("email", ""),
        ]
        for d in docs
    ]
    month_name = datetime(2000, month, 1).strftime("%B")
    if format == "excel":
        return xlsx_response(headers, rows, "Birthdays", f"birthdays_{month_name}.xlsx")
    return pdf_table_response(f"Birthdays — {month_name}", headers, rows, f"birthdays_{month_name}.pdf")


@router.get("/anniversaries")
async def report_anniversaries(
    month: int = Query(..., ge=1, le=12),
    format: Format = "excel",
    user: dict = Depends(require_role("staff")),
    storage: Storage = Depends(get_storage),
):
    docs = await storage.members.list(anniversary_month=month, limit=5000)
    headers = ["Member ID", "Full Name", "Anniversary", "Phone", "Email"]
    rows = [
        [
            d.get("member_id", ""), f"{d.get('first_name', '')} {d.get('last_name', '')}",
            d.get("wedding_anniversary", ""), d.get("phone_primary", ""), d.get("email", ""),
        ]
        for d in docs
    ]
    month_name = datetime(2000, month, 1).strftime("%B")
    if format == "excel":
        return xlsx_response(headers, rows, "Anniversaries", f"anniversaries_{month_name}.xlsx")
    return pdf_table_response(f"Anniversaries — {month_name}", headers, rows, f"anniversaries_{month_name}.pdf")


@router.get("/contributions-monthly")
async def report_contrib_monthly(
    year: int,
    month: int = Query(..., ge=1, le=12),
    format: Format = "excel",
    user: dict = Depends(require_role("admin")),
    storage: Storage = Depends(get_storage),
):
    docs = await storage.contributions.list_by_month(year, month)
    headers = ["Date", "Receipt #", "Member ID", "Member", "Type", "Amount (INR)", "Payment Mode", "Reference"]
    rows = [
        [
            d.get("contribution_date", ""), d.get("receipt_no", ""), d.get("member_external_id", ""),
            d.get("member_name", ""), d.get("contribution_type", ""), f"{d.get('amount', 0):.2f}",
            d.get("payment_mode", ""), d.get("reference_no", ""),
        ]
        for d in docs
    ]
    total = sum(d.get("amount", 0) for d in docs)
    rows.append(["", "", "", "", "TOTAL", f"{total:.2f}", "", ""])
    month_name = datetime(2000, month, 1).strftime("%B")
    title = f"Monthly Contributions — {month_name} {year}"
    if format == "excel":
        return xlsx_response(headers, rows, "Contributions", f"contributions_{year}_{month:02d}.xlsx")
    return pdf_table_response(title, headers, rows, f"contributions_{year}_{month:02d}.pdf")


@router.get("/member-statement/{member_id}")
async def report_member_statement(
    member_id: str,
    year: int,
    format: Format = "pdf",
    user: dict = Depends(require_role("admin")),
    storage: Storage = Depends(get_storage),
):
    from app.routers.contributions import member_contribution_summary
    member = await storage.members.get_by_id(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    summary = await member_contribution_summary(member_id, year, user, storage)
    headers = ["Month", "Tithe (INR)", "Offering (INR)", "Other (INR)", "Total (INR)"]
    rows = [
        [
            datetime(2000, m, 1).strftime("%B"),
            f"{v['Tithe']:.2f}", f"{v['Offering']:.2f}", f"{v['Other']:.2f}", f"{v['Total']:.2f}",
        ]
        for m, v in summary["months"].items()
    ]
    rows.append(["ANNUAL TOTAL", "", "", "", f"{summary['annual_total']:.2f}"])
    name = f"{member['first_name']} {member['last_name']}"
    title = f"Contribution Statement — {name} ({year})"
    subtitle = f"Member ID: {member['member_id']}"
    if format == "excel":
        return xlsx_response(headers, rows, "Statement", f"statement_{member['member_id']}_{year}.xlsx")
    return pdf_table_response(title, headers, rows, f"statement_{member['member_id']}_{year}.pdf", subtitle=subtitle)


@router.get("/non-contributing")
async def report_non_contrib(
    months: int = 2,
    format: Format = "excel",
    user: dict = Depends(require_role("admin")),
    storage: Storage = Depends(get_storage),
):
    today = now_utc().date()
    cutoff_iso = (today - timedelta(days=months * 30)).isoformat()
    members = await storage.members.list_active()
    rows = []
    for m in members:
        last_c = await storage.contributions.last_by_member(m["id"])
        last_date = last_c["contribution_date"] if last_c else None
        if not last_date or last_date < cutoff_iso:
            rows.append([
                m.get("member_id", ""), f"{m.get('first_name', '')} {m.get('last_name', '')}",
                m.get("phone_primary", ""), m.get("email", ""), last_date or "—",
            ])
    headers = ["Member ID", "Full Name", "Phone", "Email", "Last Contribution"]
    title = f"Non-Contributing Members (no record in {months} months)"
    if format == "excel":
        return xlsx_response(headers, rows, "Non-Contributing", "non_contributing.xlsx")
    return pdf_table_response(title, headers, rows, "non_contributing.pdf")


@router.get("/families")
async def report_families(
    format: Format = "excel",
    user: dict = Depends(require_role("staff")),
    storage: Storage = Depends(get_storage),
):
    fams = await storage.families.list_all()
    rows = []
    for f in fams:
        ids = [f["head_member_id"]]
        heads = await storage.members.get_by_ids(ids)
        head = heads[0] if heads else None
        head_name = f"{head['first_name']} {head['last_name']}" if head else "—"
        rows.append([f["family_name"], head_name, len(f.get("members", []))])
    headers = ["Family Name", "Head", "Member Count"]
    if format == "excel":
        return xlsx_response(headers, rows, "Families", "families.xlsx")
    return pdf_table_response("Family Report", headers, rows, "families.pdf")
