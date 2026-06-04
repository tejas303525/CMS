# Church Management System (CMS) — Product Requirements

## Original Problem Statement
"Develop this software" — based on attached **Church Management System SRS** specifying member, family, financial (tithes & offerings), pastoral, search, reporting, and access-control modules.

## User Choices
- **Scope**: Full v1.0
- **Auth**: Username + password (NOT email); roles Super Admin / Admin / Staff / Read-Only
- **Currency**: AED only (hard-coded)
- **Reports**: PDF + Excel
- **Notifications**: In-app only (no external email/WhatsApp)

## Architecture
- **Backend**: FastAPI + Motor (async MongoDB) + PyJWT + bcrypt + reportlab (PDF) + openpyxl (Excel)
- **Frontend**: React 19 + React Router v7 + Axios + Tailwind + shadcn/ui + lucide-react
- **Theme**: Organic & Earthy. Cormorant Garamond (headings) + Manrope (body). Deep olive (#2A4B3C) brand + warm gold accent (#C49A45). Warm off-white (#FDFBF7) surfaces.

## User Personas
- **Super Admin**: Church IT / Senior Pastor — full access + user mgmt
- **Admin**: Church Secretary / Finance — members, families, tithes, reports
- **Staff**: Ministry Leaders — view + edit members/families; reports excluding finance
- **Read-Only**: Ushers / Cell Leaders — view members + dashboard (no financial figures)

## What's been implemented (2026-06-04)
- ✅ Auth: JWT username/password, 4 seeded users, RBAC via `require_role` dep
- ✅ Members: CRUD, auto `CHM00001` IDs, advanced search (name/ID/phone/email/ministry/status/birthday month/anniversary month), pastoral notes visibility restricted to admin+, soft-delete
- ✅ Families: head-of-household + members with relationship_type, enriched view with ages & wedding anniversary
- ✅ Tithes & Offerings: contribution recording, auto `RCP000001` receipts, AED currency, monthly per-member summary table (Tithe / Offering / Other / Total + annual)
- ✅ Dashboard: active members, new this month, tithes vs last month, upcoming birthdays/anniversaries (7 days), recent activity, quick-add buttons
- ✅ Reports: Members, Birthdays, Anniversaries, Monthly Contributions, Member Statement, Non-Contributing, Families — all with PDF + Excel
- ✅ Users module (Super Admin) + Audit Trail viewer (Admin+)
- ✅ Indexes on users.username, members.member_id, contributions.receipt_no, audit_logs.timestamp

## Test results
- Backend: 35/35 passing (pytest)
- Frontend: 17/17 smoke steps passing
- Test file: /app/backend/tests/test_cms_backend.py

## Backlog / Future Enhancements (per SRS v1.0+)
- **P1**: Document attachment upload (baptism certificates) — needs file storage integration
- **P1**: Bulk CSV import for members
- **P2**: Print individual member profile to PDF
- **P2**: Member transfer between branches (multi-branch support)
- **P2**: SMS/Email/WhatsApp notifications for birthdays & receipts
- **P3**: Cell group / ministry catalogues (currently free-text)
- **P3**: Forgot-password flow
- **P3**: Configurable currency / locale settings UI (currently env-driven)
- **P3**: Member self-service portal
- **P3**: Split server.py into modules (auth, members, contributions, reports)
