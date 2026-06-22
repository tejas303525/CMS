import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { MEMBERSHIP_STATUSES, MONTHS, formatDate } from "@/lib/constants";
import { Search, UserPlus, Filter, ChevronRight } from "lucide-react";

const StatusBadge = ({ status }) => {
  const map = {
    Active: "status-active",
    Inactive: "status-inactive",
    Visitor: "status-visitor",
    Transferred: "status-transferred",
  };
  return <span className={`status-pill ${map[status] || ""}`}>{status}</span>;
};

export default function MembersList() {
  const { hasRole } = useAuth();
  const navigate = useNavigate();
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("");
  const [birthdayMonth, setBirthdayMonth] = useState("");
  const [anniversaryMonth, setAnniversaryMonth] = useState("");

  const load = () => {
    setLoading(true);
    const params = {};
    if (q) params.q = q;
    if (status) params.status = status;
    if (birthdayMonth) params.birthday_month = birthdayMonth;
    if (anniversaryMonth) params.anniversary_month = anniversaryMonth;
    api.get("/members", { params })
      .then((r) => setMembers(r.data))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, []);

  return (
    <div data-testid="members-page">
      <div className="flex items-end justify-between mb-8">
        <div>
          <div className="small-label">Directory</div>
          <h1 className="font-display text-4xl mt-2">Members</h1>
        </div>
        {hasRole("staff") && (
          <button
            className="btn-primary flex items-center gap-2"
            onClick={() => navigate("/members/new")}
            data-testid="add-member-button"
          >
            <UserPlus className="w-4 h-4" /> Add member
          </button>
        )}
      </div>

      <div className="surface-card p-5 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <div className="md:col-span-2 relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2" style={{ color: "var(--text-muted)" }} />
            <input
              className="input-field pl-10"
              placeholder="Search by name, ID, phone, email…"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && load()}
              data-testid="members-search-input"
            />
          </div>
          <select className="input-field" value={status} onChange={(e) => setStatus(e.target.value)} data-testid="members-status-filter">
            <option value="">All statuses</option>
            {MEMBERSHIP_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
          <select className="input-field" value={birthdayMonth} onChange={(e) => setBirthdayMonth(e.target.value)} data-testid="members-birthday-filter">
            <option value="">Birthday: any month</option>
            {MONTHS.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
          </select>
          <select className="input-field" value={anniversaryMonth} onChange={(e) => setAnniversaryMonth(e.target.value)} data-testid="members-anniversary-filter">
            <option value="">Anniversary: any month</option>
            {MONTHS.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
          </select>
        </div>
        <div className="flex justify-end mt-3 gap-2">
          <button className="btn-secondary text-sm flex items-center gap-2" onClick={() => { setQ(""); setStatus(""); setBirthdayMonth(""); setAnniversaryMonth(""); setTimeout(load, 0); }} data-testid="members-clear-filters">
            Clear
          </button>
          <button className="btn-primary text-sm flex items-center gap-2" onClick={load} data-testid="members-apply-filters">
            <Filter className="w-4 h-4" /> Apply filters
          </button>
        </div>
      </div>

      <div className="surface-card overflow-hidden">
        <table className="cms-table" data-testid="members-table">
          <thead>
            <tr>
              <th>Member ID</th>
              <th>Name</th>
              <th>Gender</th>
              <th>Phone</th>
              <th>Status</th>
              <th>DOB</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={7} className="text-center" style={{ color: "var(--text-secondary)" }}>Loading…</td></tr>
            ) : members.length === 0 ? (
              <tr><td colSpan={7} className="text-center" style={{ color: "var(--text-secondary)" }}>No members found.</td></tr>
            ) : members.map((m) => (
              <tr key={m.id} data-testid={`member-row-${m.member_id}`}>
                <td className="font-mono text-xs">{m.member_id}</td>
                <td>
                  <Link to={`/members/${m.id}`} className="font-medium hover:underline">
                    {m.first_name} {m.last_name}
                  </Link>
                  {m.email && <div className="text-xs" style={{ color: "var(--text-muted)" }}>{m.email}</div>}
                </td>
                <td>{m.gender}</td>
                <td>{m.phone_primary || "—"}</td>
                <td><StatusBadge status={m.membership_status} /></td>
                <td>{formatDate(m.date_of_birth)}</td>
                <td className="text-right">
                  <Link to={`/members/${m.id}`} className="inline-flex items-center text-sm brand-text hover:underline">
                    Open <ChevronRight className="w-4 h-4" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

