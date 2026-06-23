from datetime import timedelta, datetime
from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.storage.deps import get_storage
from app.storage.base import Storage
from app.models import ROLE_LEVEL
from app.utils.time import now_utc

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
async def dashboard_summary(
    user: dict = Depends(get_current_user),
    storage: Storage = Depends(get_storage),
):
    today = now_utc().date()
    month_start = today.replace(day=1)
    last_month_start = (month_start - timedelta(days=1)).replace(day=1)

    active_members = await storage.members.count_active()
    new_members_this_month = await storage.members.count_new_since(month_start.isoformat())

    show_finance = ROLE_LEVEL.get(user["role"], 0) >= ROLE_LEVEL["admin"]
    this_month_total = 0.0
    last_month_total = 0.0
    if show_finance:
        this_month_total = await storage.contributions.sum_by_month(today.year, today.month)
        last_month_total = await storage.contributions.sum_by_month(
            last_month_start.year, last_month_start.month
        )

    members = await storage.members.list_non_inactive()

    def upcoming(field: str, days: int = 7):
        items = []
        for m in members:
            v = m.get(field)
            if not v:
                continue
            try:
                d = datetime.fromisoformat(v).date()
            except Exception:
                continue
            this_year = d.replace(year=today.year)
            if this_year < today:
                this_year = d.replace(year=today.year + 1)
            delta = (this_year - today).days
            if 0 <= delta <= days:
                items.append({
                    "id": m["id"],
                    "member_id": m.get("member_id"),
                    "name": f"{m['first_name']} {m['last_name']}",
                    "date": v,
                    "next_occurrence": this_year.isoformat(),
                    "in_days": delta,
                })
        items.sort(key=lambda x: x["in_days"])
        return items

    recent = await storage.audit.list_recent(limit=10)

    return {
        "active_members": active_members,
        "new_members_this_month": new_members_this_month,
        "tithes_this_month": this_month_total,
        "tithes_last_month": last_month_total,
        "upcoming_birthdays": upcoming("date_of_birth"),
        "upcoming_anniversaries": upcoming("wedding_anniversary"),
        "recent_activity": recent,
        "show_finance": show_finance,
    }
