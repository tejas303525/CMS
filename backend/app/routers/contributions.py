import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends

from app.auth import require_role
from app.audit import audit
from app.storage.deps import get_storage
from app.storage.base import Storage
from app.models import ContributionIn
from app.utils.time import now_utc
from app.utils.pdf import pdf_receipt_response

router = APIRouter(prefix="/contributions", tags=["contributions"])


@router.get("")
async def list_contributions(
    member_id: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    type: Optional[str] = None,
    user: dict = Depends(require_role("admin")),
    storage: Storage = Depends(get_storage),
):
    return await storage.contributions.list(
        member_id=member_id, year=year, month=month, contribution_type=type
    )


@router.post("")
async def create_contribution(
    body: ContributionIn,
    user: dict = Depends(require_role("admin")),
    storage: Storage = Depends(get_storage),
):
    member = await storage.members.get_by_id(body.member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    dt = datetime.fromisoformat(body.contribution_date)
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["currency"] = "INR"
    doc["year"] = dt.year
    doc["month"] = dt.month
    doc["member_name"] = f"{member['first_name']} {member['last_name']}"
    doc["member_external_id"] = member["member_id"]
    doc["recorded_by"] = user["username"]
    doc["created_at"] = now_utc().isoformat()
    created = await storage.contributions.create(doc)
    await audit(
        storage, user, "create", "contribution", created["id"],
        {"receipt_no": created["receipt_no"], "amount": created["amount"]},
    )
    return created


@router.delete("/{contribution_id}")
async def delete_contribution(
    contribution_id: str,
    user: dict = Depends(require_role("admin")),
    storage: Storage = Depends(get_storage),
):
    await storage.contributions.delete(contribution_id)
    await audit(storage, user, "delete", "contribution", contribution_id)
    return {"ok": True}


@router.get("/{contribution_id}/receipt")
async def contribution_receipt(
    contribution_id: str,
    user: dict = Depends(require_role("admin")),
    storage: Storage = Depends(get_storage),
):
    c = await storage.contributions.get_by_id(contribution_id)
    if not c:
        raise HTTPException(status_code=404, detail="Contribution not found")
    member = await storage.members.get_by_id(c["member_id"]) or {}
    return pdf_receipt_response(c, member)


@router.get("/summary/{member_id}")
async def member_contribution_summary(
    member_id: str,
    year: int,
    user: dict = Depends(require_role("admin")),
    storage: Storage = Depends(get_storage),
):
    docs = await storage.contributions.list_by_member_year(member_id, year)
    months = {m: {"Tithe": 0.0, "Offering": 0.0, "Other": 0.0, "Total": 0.0} for m in range(1, 13)}
    for d in docs:
        m = d["month"]
        bucket = (
            "Tithe" if d["contribution_type"] == "Tithe"
            else "Offering" if d["contribution_type"] == "Offering"
            else "Other"
        )
        months[m][bucket] += d["amount"]
        months[m]["Total"] += d["amount"]
    return {
        "year": year,
        "months": months,
        "annual_total": sum(v["Total"] for v in months.values()),
        "transactions": docs,
    }
