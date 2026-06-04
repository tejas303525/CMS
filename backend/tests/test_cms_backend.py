"""Comprehensive backend tests for Church Management System v1.0.

Covers: auth, RBAC, members CRUD, pastoral notes visibility, families,
contributions, dashboard summary, reports (pdf/excel), users (super_admin),
and audit log.
"""
import os
import uuid
import pytest
import requests
from datetime import datetime, timezone

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://dev-forge-97.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

CREDS = {
    "super_admin": ("superadmin", "Admin@123"),
    "admin":       ("admin",      "Admin@123"),
    "staff":       ("staff",      "Staff@123"),
    "read_only":   ("viewer",     "View@123"),
}


def _login(username: str, password: str) -> str:
    r = requests.post(f"{API}/auth/login", json={"username": username, "password": password}, timeout=15)
    assert r.status_code == 200, f"login failed for {username}: {r.status_code} {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def tokens():
    return {role: _login(u, p) for role, (u, p) in CREDS.items()}


def H(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


# ---------- Auth ----------
class TestAuth:
    def test_login_all_roles(self):
        for role, (u, p) in CREDS.items():
            r = requests.post(f"{API}/auth/login", json={"username": u, "password": p})
            assert r.status_code == 200, f"{role} login failed: {r.text}"
            data = r.json()
            assert "access_token" in data and isinstance(data["access_token"], str)
            assert data["user"]["username"] == u
            assert data["user"]["role"] == role

    def test_login_invalid(self):
        r = requests.post(f"{API}/auth/login", json={"username": "superadmin", "password": "WRONG"})
        assert r.status_code == 401

    def test_me_returns_user(self, tokens):
        r = requests.get(f"{API}/auth/me", headers=H(tokens["super_admin"]))
        assert r.status_code == 200
        assert r.json()["username"] == "superadmin"

    def test_me_no_token(self):
        r = requests.get(f"{API}/auth/me")
        assert r.status_code == 401


# ---------- RBAC + Members ----------
class TestMembersAndRBAC:
    member_id = None  # cls-level handle

    def test_viewer_cannot_create_member(self, tokens):
        payload = {"first_name": "Z", "last_name": "X", "gender": "Male", "date_of_birth": "1990-05-12", "marital_status": "Single"}
        r = requests.post(f"{API}/members", json=payload, headers=H(tokens["read_only"]))
        assert r.status_code == 403

    def test_staff_can_create_member(self, tokens):
        payload = {
            "first_name": "TEST_John",
            "last_name": f"Doe_{uuid.uuid4().hex[:6]}",
            "gender": "Male",
            "date_of_birth": "1992-07-15",
            "marital_status": "Married",
            "wedding_anniversary": "2018-11-20",
            "phone_primary": "+971500000000",
            "email": "test_john@example.com",
            "ministries": ["Choir"],
            "notes": "Pastoral private note",
        }
        r = requests.post(f"{API}/members", json=payload, headers=H(tokens["staff"]))
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["first_name"] == "TEST_John"
        assert d.get("member_id", "").startswith("CHM") and len(d["member_id"]) == 8
        TestMembersAndRBAC.member_id = d["id"]

    def test_list_members(self, tokens):
        r = requests.get(f"{API}/members", headers=H(tokens["staff"]))
        assert r.status_code == 200
        assert isinstance(r.json(), list) and len(r.json()) >= 1

    def test_search_filters(self, tokens):
        r = requests.get(f"{API}/members", params={"q": "TEST_John"}, headers=H(tokens["staff"]))
        assert r.status_code == 200
        assert any(m["first_name"] == "TEST_John" for m in r.json())
        # birthday month filter
        r2 = requests.get(f"{API}/members", params={"birthday_month": 7}, headers=H(tokens["staff"]))
        assert r2.status_code == 200
        for m in r2.json():
            assert m.get("date_of_birth", "0000-00-")[5:7] == "07"

    def test_get_member_notes_visibility(self, tokens):
        mid = TestMembersAndRBAC.member_id
        # admin sees notes
        r = requests.get(f"{API}/members/{mid}", headers=H(tokens["admin"]))
        assert r.status_code == 200
        assert r.json()["notes"] == "Pastoral private note"
        # staff sees empty notes
        r2 = requests.get(f"{API}/members/{mid}", headers=H(tokens["staff"]))
        assert r2.status_code == 200
        assert r2.json()["notes"] == ""
        # viewer too
        r3 = requests.get(f"{API}/members/{mid}", headers=H(tokens["read_only"]))
        assert r3.status_code == 200
        assert r3.json()["notes"] == ""

    def test_patch_member(self, tokens):
        mid = TestMembersAndRBAC.member_id
        body = {
            "first_name": "TEST_John",
            "last_name": "DoeUpdated",
            "gender": "Male",
            "date_of_birth": "1992-07-15",
            "marital_status": "Married",
        }
        r = requests.patch(f"{API}/members/{mid}", json=body, headers=H(tokens["staff"]))
        assert r.status_code == 200
        assert r.json()["last_name"] == "DoeUpdated"

    def test_soft_delete_requires_admin(self, tokens):
        mid = TestMembersAndRBAC.member_id
        # staff blocked
        r = requests.delete(f"{API}/members/{mid}", headers=H(tokens["staff"]))
        assert r.status_code == 403
        # admin ok
        r2 = requests.delete(f"{API}/members/{mid}", headers=H(tokens["admin"]))
        assert r2.status_code == 200
        # verify status -> Inactive
        rg = requests.get(f"{API}/members/{mid}", headers=H(tokens["admin"]))
        assert rg.status_code == 200 and rg.json()["membership_status"] == "Inactive"


# ---------- Contributions ----------
class TestContributions:
    contribution_id = None
    target_member_id = None

    def test_admin_creates_contribution(self, tokens):
        # create a fresh member
        m = requests.post(f"{API}/members", json={
            "first_name": "TEST_Contrib", "last_name": "Member",
            "gender": "Female", "date_of_birth": "1985-03-21", "marital_status": "Single",
        }, headers=H(tokens["staff"]))
        assert m.status_code == 200
        TestContributions.target_member_id = m.json()["id"]

        # staff cannot create contribution
        bad = requests.post(f"{API}/contributions", json={
            "member_id": TestContributions.target_member_id,
            "contribution_date": "2026-01-12",
            "contribution_type": "Tithe", "amount": 500.0, "payment_mode": "Cash",
        }, headers=H(tokens["staff"]))
        assert bad.status_code == 403

        ok = requests.post(f"{API}/contributions", json={
            "member_id": TestContributions.target_member_id,
            "contribution_date": "2026-01-12",
            "contribution_type": "Tithe", "amount": 500.0, "payment_mode": "Cash",
        }, headers=H(tokens["admin"]))
        assert ok.status_code == 200, ok.text
        d = ok.json()
        assert d["receipt_no"].startswith("RCP") and len(d["receipt_no"]) == 9
        assert d["currency"] == "AED"
        assert d["year"] == 2026 and d["month"] == 1
        TestContributions.contribution_id = d["id"]

    def test_list_filter(self, tokens):
        r = requests.get(f"{API}/contributions", params={"year": 2026, "month": 1, "type": "Tithe"}, headers=H(tokens["admin"]))
        assert r.status_code == 200
        assert any(c["id"] == TestContributions.contribution_id for c in r.json())

    def test_viewer_blocked(self, tokens):
        r = requests.get(f"{API}/contributions", headers=H(tokens["read_only"]))
        assert r.status_code == 403

    def test_summary(self, tokens):
        r = requests.get(f"{API}/contributions/summary/{TestContributions.target_member_id}", params={"year": 2026}, headers=H(tokens["admin"]))
        assert r.status_code == 200
        s = r.json()
        assert set(s["months"].keys()) == {str(i) for i in range(1, 13)} or set(s["months"].keys()) == set(range(1, 13))
        # months may be int keys serialized; access via str
        m1 = s["months"][1] if 1 in s["months"] else s["months"]["1"]
        assert m1["Tithe"] == 500.0
        assert m1["Total"] == 500.0
        assert s["annual_total"] == 500.0


# ---------- Families ----------
class TestFamilies:
    family_id = None

    def test_create_and_enrich(self, tokens):
        m1 = requests.post(f"{API}/members", json={
            "first_name": "TEST_Fam", "last_name": "Head",
            "gender": "Male", "date_of_birth": "1980-01-01", "marital_status": "Married",
        }, headers=H(tokens["staff"])).json()
        m2 = requests.post(f"{API}/members", json={
            "first_name": "TEST_Fam", "last_name": "Spouse",
            "gender": "Female", "date_of_birth": "1982-04-15", "marital_status": "Married",
        }, headers=H(tokens["staff"])).json()

        payload = {
            "family_name": f"TEST_Fam_{uuid.uuid4().hex[:6]}",
            "head_member_id": m1["id"],
            "members": [{"member_id": m2["id"], "relationship_type": "Spouse"}],
        }
        r = requests.post(f"{API}/families", json=payload, headers=H(tokens["staff"]))
        assert r.status_code == 200, r.text
        TestFamilies.family_id = r.json()["id"]

        # enriched
        rg = requests.get(f"{API}/families/{TestFamilies.family_id}", headers=H(tokens["admin"]))
        assert rg.status_code == 200
        fam = rg.json()
        assert fam["head_member"]["id"] == m1["id"]
        assert any(em["relationship_type"] == "Spouse" for em in fam["enriched_members"])

    def test_delete_family_requires_admin(self, tokens):
        r = requests.delete(f"{API}/families/{TestFamilies.family_id}", headers=H(tokens["staff"]))
        assert r.status_code == 403
        r2 = requests.delete(f"{API}/families/{TestFamilies.family_id}", headers=H(tokens["admin"]))
        assert r2.status_code == 200


# ---------- Dashboard ----------
class TestDashboard:
    def test_admin_dashboard_has_finance(self, tokens):
        r = requests.get(f"{API}/dashboard/summary", headers=H(tokens["admin"]))
        assert r.status_code == 200
        d = r.json()
        assert "active_members" in d and isinstance(d["active_members"], int)
        assert d["show_finance"] is True
        assert "upcoming_birthdays" in d and isinstance(d["upcoming_birthdays"], list)
        assert "recent_activity" in d

    def test_viewer_dashboard_no_finance(self, tokens):
        r = requests.get(f"{API}/dashboard/summary", headers=H(tokens["read_only"]))
        assert r.status_code == 200
        d = r.json()
        assert d["show_finance"] is False
        assert d["tithes_this_month"] == 0
        assert d["tithes_last_month"] == 0


# ---------- Users (super_admin only) ----------
class TestUsers:
    new_user_id = None
    new_username = f"TEST_user_{uuid.uuid4().hex[:6]}"

    def test_admin_cannot_list_users(self, tokens):
        r = requests.get(f"{API}/users", headers=H(tokens["admin"]))
        assert r.status_code == 403

    def test_super_admin_list_users(self, tokens):
        r = requests.get(f"{API}/users", headers=H(tokens["super_admin"]))
        assert r.status_code == 200
        usernames = [u["username"] for u in r.json()]
        for required in ["superadmin", "admin", "staff", "viewer"]:
            assert required in usernames

    def test_create_user(self, tokens):
        payload = {"username": TestUsers.new_username, "password": "Pass@123", "full_name": "TEST User", "role": "staff"}
        r = requests.post(f"{API}/users", json=payload, headers=H(tokens["super_admin"]))
        assert r.status_code == 200, r.text
        TestUsers.new_user_id = r.json()["id"]
        # duplicate
        r2 = requests.post(f"{API}/users", json=payload, headers=H(tokens["super_admin"]))
        assert r2.status_code == 400

    def test_patch_user(self, tokens):
        r = requests.patch(f"{API}/users/{TestUsers.new_user_id}",
                           json={"full_name": "TEST Updated", "role": "admin"},
                           headers=H(tokens["super_admin"]))
        assert r.status_code == 200
        assert r.json()["full_name"] == "TEST Updated"
        assert r.json()["role"] == "admin"

    def test_cannot_delete_self(self, tokens):
        me = requests.get(f"{API}/auth/me", headers=H(tokens["super_admin"])).json()
        r = requests.delete(f"{API}/users/{me['id']}", headers=H(tokens["super_admin"]))
        assert r.status_code == 400

    def test_delete_other(self, tokens):
        r = requests.delete(f"{API}/users/{TestUsers.new_user_id}", headers=H(tokens["super_admin"]))
        assert r.status_code == 200


# ---------- Audit log ----------
class TestAuditLog:
    def test_audit_log_admin(self, tokens):
        r = requests.get(f"{API}/audit-logs", headers=H(tokens["admin"]))
        assert r.status_code == 200
        logs = r.json()
        assert isinstance(logs, list) and len(logs) > 0
        first = logs[0]
        for k in ["username", "action", "entity", "timestamp"]:
            assert k in first

    def test_audit_log_staff_blocked(self, tokens):
        r = requests.get(f"{API}/audit-logs", headers=H(tokens["staff"]))
        assert r.status_code == 403


# ---------- Reports ----------
class TestReports:
    def test_members_excel(self, tokens):
        r = requests.get(f"{API}/reports/members", params={"format": "excel"}, headers=H(tokens["staff"]))
        assert r.status_code == 200
        assert "spreadsheetml" in r.headers.get("Content-Type", "")
        assert "attachment" in r.headers.get("Content-Disposition", "")

    def test_members_pdf(self, tokens):
        r = requests.get(f"{API}/reports/members", params={"format": "pdf"}, headers=H(tokens["staff"]))
        assert r.status_code == 200
        assert r.headers.get("Content-Type", "").startswith("application/pdf")
        assert r.content[:4] == b"%PDF"

    def test_birthdays_requires_month(self, tokens):
        r = requests.get(f"{API}/reports/birthdays", headers=H(tokens["staff"]))
        assert r.status_code == 422
        r2 = requests.get(f"{API}/reports/birthdays", params={"month": 7, "format": "excel"}, headers=H(tokens["staff"]))
        assert r2.status_code == 200

    def test_anniversaries(self, tokens):
        r = requests.get(f"{API}/reports/anniversaries", params={"month": 11, "format": "pdf"}, headers=H(tokens["staff"]))
        assert r.status_code == 200

    def test_contrib_monthly_admin_only(self, tokens):
        r = requests.get(f"{API}/reports/contributions-monthly", params={"year": 2026, "month": 1, "format": "excel"}, headers=H(tokens["staff"]))
        assert r.status_code == 403
        r2 = requests.get(f"{API}/reports/contributions-monthly", params={"year": 2026, "month": 1, "format": "pdf"}, headers=H(tokens["admin"]))
        assert r2.status_code == 200

    def test_non_contributing(self, tokens):
        r = requests.get(f"{API}/reports/non-contributing", params={"months": 2, "format": "excel"}, headers=H(tokens["admin"]))
        assert r.status_code == 200

    def test_families_report(self, tokens):
        r = requests.get(f"{API}/reports/families", params={"format": "excel"}, headers=H(tokens["staff"]))
        assert r.status_code == 200

    def test_member_statement(self, tokens):
        # use one existing member
        members = requests.get(f"{API}/members", headers=H(tokens["admin"])).json()
        if not members:
            pytest.skip("No members in db")
        mid = members[0]["id"]
        r = requests.get(f"{API}/reports/member-statement/{mid}", params={"year": 2026, "format": "pdf"}, headers=H(tokens["admin"]))
        assert r.status_code == 200
        assert r.content[:4] == b"%PDF"
