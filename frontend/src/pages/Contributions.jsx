import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import api from "@/lib/api";
import { CONTRIBUTION_TYPES, PAYMENT_MODES, formatINR, formatDate, MONTHS, apiErrorMessage } from "@/lib/constants";
import { Plus, Receipt, Trash2, Download } from "lucide-react";
import { downloadAuthed } from "@/pages/MemberDetail";

export default function Contributions() {
  const navigate = useNavigate();
  const [contributions, setContributions] = useState([]);
  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState("");
  const [type, setType] = useState("");
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    const params = { year };
    if (month) params.month = month;
    if (type) params.type = type;
    api.get("/contributions", { params }).then((r) => setContributions(r.data)).finally(() => setLoading(false));
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, [year, month, type]);

  const total = contributions.reduce((s, c) => s + c.amount, 0);

  const remove = async (id) => {
    if (!window.confirm("Delete this contribution?")) return;
    await api.delete(`/contributions/${id}`);
    load();
  };

  return (
    <div data-testid="contributions-page">
      <div className="flex items-end justify-between mb-8">
        <div>
          <div className="small-label">Stewardship</div>
          <h1 className="font-display text-4xl mt-2">Tithes & Offerings</h1>
        </div>
        <button className="btn-primary flex items-center gap-2" onClick={() => navigate("/contributions/new")} data-testid="record-contribution-button">
          <Plus className="w-4 h-4" /> Record contribution
        </button>
      </div>

      <div className="surface-card p-5 mb-6 grid grid-cols-1 md:grid-cols-4 gap-3">
        <select className="input-field" value={year} onChange={(e) => setYear(Number(e.target.value))} data-testid="contrib-year-select">
          {Array.from({ length: 6 }).map((_, i) => {
            const y = new Date().getFullYear() - i;
            return <option key={y} value={y}>{y}</option>;
          })}
        </select>
        <select className="input-field" value={month} onChange={(e) => setMonth(e.target.value)} data-testid="contrib-month-select">
          <option value="">All months</option>
          {MONTHS.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
        </select>
        <select className="input-field" value={type} onChange={(e) => setType(e.target.value)} data-testid="contrib-type-select">
          <option value="">All types</option>
          {CONTRIBUTION_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
        <div className="surface-card p-3 flex items-center justify-between" style={{ background: "var(--bg-secondary)", border: "none" }}>
          <span className="small-label">Total</span>
          <span className="font-display text-2xl">{formatINR(total)}</span>
        </div>
      </div>

      <div className="surface-card overflow-hidden">
        <table className="cms-table" data-testid="contributions-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Receipt</th>
              <th>Member</th>
              <th>Type</th>
              <th>Mode</th>
              <th className="text-right">Amount</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={7} className="text-center" style={{ color: "var(--text-secondary)" }}>Loading…</td></tr>
            ) : contributions.length === 0 ? (
              <tr><td colSpan={7} className="text-center" style={{ color: "var(--text-secondary)" }}>No contributions found for the selected filters.</td></tr>
            ) : contributions.map((c) => (
              <tr key={c.id} data-testid={`contribution-row-${c.receipt_no}`}>
                <td>{formatDate(c.contribution_date)}</td>
                <td className="font-mono text-xs">{c.receipt_no}</td>
                <td>
                  <Link to={`/members/${c.member_id}`} className="font-medium hover:underline">{c.member_name}</Link>
                  <div className="text-xs" style={{ color: "var(--text-muted)" }}>{c.member_external_id}</div>
                </td>
                <td>{c.contribution_type}</td>
                <td>{c.payment_mode}</td>
                <td className="text-right font-medium">{formatINR(c.amount)}</td>
                <td className="text-right">
                  <button
                    onClick={() => downloadAuthed(`/contributions/${c.id}/receipt`, `receipt_${c.receipt_no}.pdf`)}
                    className="inline-flex items-center gap-1 text-xs mr-3 brand-text hover:underline"
                    data-testid={`download-receipt-${c.receipt_no}`}
                    title="Download receipt PDF"
                  >
                    <Download className="w-4 h-4" /> Receipt
                  </button>
                  <button onClick={() => remove(c.id)} className="text-xs" style={{ color: "var(--danger)" }} data-testid={`delete-contribution-${c.receipt_no}`}>
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
