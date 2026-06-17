import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import api from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatDate, formatINR, MONTHS, ageFromDob } from "@/lib/constants";
import { ArrowLeft, Mail, Phone, MessageCircle, MapPin, Edit, Plus, Receipt, Download } from "lucide-react";

const TABS = [
  { key: "personal", label: "Personal" },
  { key: "contact", label: "Contact" },
  { key: "family", label: "Family" },
  { key: "tithes", label: "Tithes & Offerings", role: "admin" },
  { key: "notes", label: "Pastoral Notes", role: "admin" },
];

export default function MemberDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { hasRole } = useAuth();
  const [member, setMember] = useState(null);
  const [tab, setTab] = useState("personal");
  const [year, setYear] = useState(new Date().getFullYear());
  const [summary, setSummary] = useState(null);
  const [families, setFamilies] = useState([]);

  useEffect(() => {
    api.get(`/members/${id}`).then((r) => setMember(r.data));
    api.get("/families").then((r) => setFamilies(r.data));
  }, [id]);

  useEffect(() => {
    if (tab === "tithes" && hasRole("admin")) {
      api.get(`/contributions/summary/${id}`, { params: { year } })
        .then((r) => setSummary(r.data));
    }
  }, [tab, year, id, hasRole]);

  if (!member) return <div>Loading…</div>;

  const family = families.find((f) =>
    f.head_member_id === id || (f.members || []).some((m) => m.member_id === id)
  );

  return (
    <div data-testid="member-detail-page">
      <Link to="/members" className="inline-flex items-center text-sm mb-6" style={{ color: "var(--text-secondary)" }}>
        <ArrowLeft className="w-4 h-4 mr-1" /> Back to members
      </Link>

      <div className="surface-card p-8 mb-6">
        <div className="flex items-start justify-between gap-6">
          <div className="flex items-center gap-5">
            <div className="w-20 h-20 rounded-full flex items-center justify-center text-white font-display text-3xl"
                 style={{ background: "var(--brand)" }}>
              {member.first_name[0]}{member.last_name[0]}
            </div>
            <div>
              <div className="small-label">{member.member_id}</div>
              <h1 className="font-display text-4xl mt-1">{member.first_name} {member.middle_name} {member.last_name}</h1>
              <div className="flex items-center gap-3 mt-2 text-sm" style={{ color: "var(--text-secondary)" }}>
                <span>{member.gender}</span>
                <span>·</span>
                <span>{ageFromDob(member.date_of_birth)} yrs</span>
                <span>·</span>
                <span>{member.marital_status}</span>
                <span className={`status-pill status-${member.membership_status.toLowerCase()}`}>{member.membership_status}</span>
              </div>
            </div>
          </div>
          {hasRole("staff") && (
            <button className="btn-secondary flex items-center gap-2" onClick={() => navigate(`/members/${id}/edit`)} data-testid="member-edit-button">
              <Edit className="w-4 h-4" /> Edit
            </button>
          )}
        </div>
      </div>

      <div className="flex gap-6 border-b mb-6" style={{ borderColor: "var(--border)" }}>
        {TABS.filter((t) => !t.role || hasRole(t.role)).map((t) => (
          <button
            key={t.key}
            className={`pb-3 text-sm font-medium transition-colors ${tab === t.key ? "brand-text" : ""}`}
            style={{
              color: tab === t.key ? "var(--brand)" : "var(--text-secondary)",
              borderBottom: tab === t.key ? "2px solid var(--brand)" : "2px solid transparent",
            }}
            onClick={() => setTab(t.key)}
            data-testid={`tab-${t.key}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "personal" && (
        <div className="surface-card p-8 grid md:grid-cols-2 gap-x-12 gap-y-5" data-testid="tab-content-personal">
          <Info label="Date of birth" value={formatDate(member.date_of_birth)} />
          <Info label="Membership date" value={formatDate(member.membership_date)} />
          <Info label="Baptism date" value={formatDate(member.baptism_date)} />
          <Info label="Cell group / Zone" value={member.cell_group || "—"} />
          <Info label="Ministries" value={(member.ministries || []).join(", ") || "—"} />
          <Info label="Marital status" value={member.marital_status} />
          {member.marital_status === "Married" && (
            <Info label="Wedding anniversary" value={formatDate(member.wedding_anniversary)} />
          )}
          <Info label="Occupation" value={member.occupation || "—"} />
          <Info label="Employer" value={member.employer || "—"} />
        </div>
      )}

      {tab === "contact" && (
        <div className="surface-card p-8 grid md:grid-cols-2 gap-x-12 gap-y-5" data-testid="tab-content-contact">
          <Info icon={Phone} label="Primary phone" value={member.phone_primary || "—"} />
          <Info icon={Phone} label="Secondary phone" value={member.phone_secondary || "—"} />
          <Info icon={MessageCircle} label="WhatsApp" value={member.whatsapp || "—"} />
          <Info icon={Mail} label="Email" value={member.email || "—"} />
          <Info icon={MapPin} label="Address" value={[member.address_street, member.address_city].filter(Boolean).join(", ") || "—"} />
          <Info label="Country of origin" value={member.country_origin || "—"} />
          <Info label="Current country" value={member.country_current || "—"} />
        </div>
      )}

      {tab === "family" && (
        <div className="surface-card p-8" data-testid="tab-content-family">
          {family ? (
            <div>
              <h3 className="font-display text-2xl mb-1">{family.family_name}</h3>
              <Link to={`/families/${family.id}`} className="text-sm brand-text hover:underline">
                Open family record →
              </Link>
            </div>
          ) : (
            <div>
              <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                This member is not yet linked to a family.
              </p>
              {hasRole("staff") && (
                <Link to="/families/new" className="btn-primary inline-flex mt-4">Create family</Link>
              )}
            </div>
          )}
        </div>
      )}

      {tab === "tithes" && hasRole("admin") && (
        <div className="surface-card p-8" data-testid="tab-content-tithes">
          <div className="flex items-center justify-between mb-5">
            <h3 className="font-display text-2xl">Contributions — {year}</h3>
            <div className="flex gap-2 items-center">
              <select className="input-field" style={{ width: 130 }} value={year} onChange={(e) => setYear(Number(e.target.value))} data-testid="tithes-year-select">
                {Array.from({ length: 6 }).map((_, i) => {
                  const y = new Date().getFullYear() - i;
                  return <option key={y} value={y}>{y}</option>;
                })}
              </select>
              <button className="btn-primary flex items-center gap-2" onClick={() => navigate(`/contributions/new?member_id=${id}`)} data-testid="add-contribution-button">
                <Plus className="w-4 h-4" /> Add contribution
              </button>
            </div>
          </div>

          {summary ? (
            <>
              <table className="cms-table">
                <thead>
                  <tr>
                    <th>Month</th>
                    <th className="text-right">Tithe</th>
                    <th className="text-right">Offering</th>
                    <th className="text-right">Other</th>
                    <th className="text-right">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {MONTHS.map((m, idx) => {
                    const v = summary.months[idx + 1];
                    const empty = v.Total === 0;
                    return (
                      <tr key={m} data-testid={`month-row-${idx+1}`}>
                        <td>{m}</td>
                        <td className="text-right">{empty ? "—" : formatINR(v.Tithe)}</td>
                        <td className="text-right">{empty ? "—" : formatINR(v.Offering)}</td>
                        <td className="text-right">{empty ? "—" : formatINR(v.Other)}</td>
                        <td className="text-right font-medium">{empty ? "—" : formatINR(v.Total)}</td>
                      </tr>
                    );
                  })}
                  <tr style={{ background: "var(--bg-secondary)" }}>
                    <td className="font-semibold uppercase text-xs tracking-wider">Annual total</td>
                    <td></td><td></td><td></td>
                    <td className="text-right font-display text-xl">{formatINR(summary.annual_total)}</td>
                  </tr>
                </tbody>
              </table>

              <div className="mt-8">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-display text-xl">Transactions</h4>
                  <a className="text-sm brand-text hover:underline" target="_blank" rel="noreferrer"
                     href={`${api.defaults.baseURL}/reports/member-statement/${id}?year=${year}&format=pdf`}
                     data-testid="download-statement-pdf"
                     onClick={(e) => {
                       e.preventDefault();
                       downloadAuthed(`/reports/member-statement/${id}?year=${year}&format=pdf`, `statement_${member.member_id}_${year}.pdf`);
                     }}>
                    Download statement PDF
                  </a>
                </div>
                <table className="cms-table">
                  <thead><tr><th>Date</th><th>Receipt</th><th>Type</th><th>Mode</th><th className="text-right">Amount</th><th></th></tr></thead>
                  <tbody>
                    {summary.transactions.length === 0 ? (
                      <tr><td colSpan={6} className="text-center" style={{ color: "var(--text-secondary)" }}>No contributions recorded.</td></tr>
                    ) : summary.transactions.map((t) => (
                      <tr key={t.id}>
                        <td>{formatDate(t.contribution_date)}</td>
                        <td className="font-mono text-xs">{t.receipt_no}</td>
                        <td>{t.contribution_type}</td>
                        <td>{t.payment_mode}</td>
                        <td className="text-right">{formatINR(t.amount)}</td>
                        <td className="text-right">
                          <button
                            onClick={() => downloadAuthed(`/contributions/${t.id}/receipt`, `receipt_${t.receipt_no}.pdf`)}
                            className="inline-flex items-center gap-1 text-xs brand-text hover:underline"
                            data-testid={`download-receipt-${t.receipt_no}`}
                          >
                            <Download className="w-3.5 h-3.5" /> Receipt
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <div className="text-sm" style={{ color: "var(--text-secondary)" }}>Loading…</div>
          )}
        </div>
      )}

      {tab === "notes" && hasRole("admin") && (
        <div className="surface-card p-8" data-testid="tab-content-notes">
          <h3 className="font-display text-2xl mb-3">Pastoral Notes</h3>
          <p className="whitespace-pre-wrap text-sm leading-relaxed" style={{ color: "var(--text-primary)" }}>
            {member.notes || "No notes recorded."}
          </p>
        </div>
      )}
    </div>
  );
}

const Info = ({ label, value, icon: Icon }) => (
  <div>
    <div className="small-label flex items-center gap-2">{Icon && <Icon className="w-3.5 h-3.5" />} {label}</div>
    <div className="mt-1 text-sm">{value}</div>
  </div>
);

export async function downloadAuthed(path, filename) {
  const token = localStorage.getItem("cms_token");
  const res = await fetch(`${api.defaults.baseURL}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) { alert("Failed to download"); return; }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; document.body.appendChild(a); a.click();
  a.remove(); URL.revokeObjectURL(url);
}
