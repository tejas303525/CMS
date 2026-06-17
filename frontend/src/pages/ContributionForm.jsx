import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import api from "@/lib/api";
import { CONTRIBUTION_TYPES, PAYMENT_MODES, apiErrorMessage, formatINR } from "@/lib/constants";
import { ArrowLeft, Save, Download } from "lucide-react";
import { downloadAuthed } from "@/pages/MemberDetail";

export default function ContributionForm() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [members, setMembers] = useState([]);
  const [form, setForm] = useState({
    member_id: params.get("member_id") || "",
    contribution_date: new Date().toISOString().slice(0, 10),
    contribution_type: "Tithe",
    amount: "",
    payment_mode: "Cash",
    reference_no: "",
    notes: "",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [lastReceipt, setLastReceipt] = useState(null);

  useEffect(() => {
    api.get("/members", { params: { limit: 1000 } }).then((r) => setMembers(r.data));
  }, []);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true); setError("");
    try {
      const payload = { ...form, amount: parseFloat(form.amount) };
      const res = await api.post("/contributions", payload);
      setLastReceipt(res.data);
      // reset for next quick entry
      setForm((f) => ({ ...f, amount: "", reference_no: "", notes: "" }));
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally { setSaving(false); }
  };

  return (
    <div data-testid="contribution-form-page">
      <Link to="/contributions" className="inline-flex items-center text-sm mb-6" style={{ color: "var(--text-secondary)" }}>
        <ArrowLeft className="w-4 h-4 mr-1" /> Back to contributions
      </Link>
      <h1 className="font-display text-4xl mb-8">Record Contribution</h1>

      <form onSubmit={submit} className="surface-card p-6 sm:p-8 grid md:grid-cols-2 gap-5" data-testid="contribution-form">
        <div className="md:col-span-2">
          <label className="field-label">Member *</label>
          <select className="input-field" required value={form.member_id} onChange={set("member_id")} data-testid="contrib-member-select">
            <option value="">Select a member…</option>
            {members.map((m) => <option key={m.id} value={m.id}>{m.first_name} {m.last_name} — {m.member_id}</option>)}
          </select>
        </div>
        <div>
          <label className="field-label">Date *</label>
          <input type="date" className="input-field" required value={form.contribution_date} onChange={set("contribution_date")} data-testid="contrib-date-input" />
        </div>
        <div>
          <label className="field-label">Type *</label>
          <select className="input-field" required value={form.contribution_type} onChange={set("contribution_type")} data-testid="contrib-type-input">
            {CONTRIBUTION_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
        <div>
          <label className="field-label">Amount (INR) *</label>
          <input type="number" min="0" step="0.01" required className="input-field" value={form.amount} onChange={set("amount")} data-testid="contrib-amount-input" />
        </div>
        <div>
          <label className="field-label">Payment mode *</label>
          <select className="input-field" required value={form.payment_mode} onChange={set("payment_mode")} data-testid="contrib-mode-input">
            {PAYMENT_MODES.map((m) => <option key={m} value={m}>{m}</option>)}
          </select>
        </div>
        <div>
          <label className="field-label">Reference no.</label>
          <input className="input-field" value={form.reference_no} onChange={set("reference_no")} data-testid="contrib-ref-input" />
        </div>
        <div className="md:col-span-2">
          <label className="field-label">Notes</label>
          <textarea className="input-field" rows={2} value={form.notes} onChange={set("notes")} />
        </div>

        {error && <div className="md:col-span-2 text-sm py-2 px-3 rounded-md" style={{ background: "rgba(139,58,58,0.08)", color: "var(--danger)" }}>{error}</div>}

        {lastReceipt && (
          <div className="md:col-span-2 p-4 rounded-lg flex items-center justify-between" style={{ background: "rgba(52,92,73,0.08)", color: "var(--success)" }} data-testid="contrib-saved-toast">
            <div>
              <div className="font-medium">Saved · Receipt {lastReceipt.receipt_no}</div>
              <div className="text-xs">{lastReceipt.member_name} · {formatINR(lastReceipt.amount)} · {lastReceipt.contribution_type}</div>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                className="btn-secondary text-sm flex items-center gap-2"
                onClick={() => downloadAuthed(`/contributions/${lastReceipt.id}/receipt`, `receipt_${lastReceipt.receipt_no}.pdf`)}
                data-testid="contrib-download-receipt"
              >
                <Download className="w-4 h-4" /> Download receipt
              </button>
              <button type="button" className="btn-secondary text-sm" onClick={() => navigate("/contributions")}>Done</button>
            </div>
          </div>
        )}

        <div className="md:col-span-2 flex justify-end gap-3 pt-2">
          <button type="button" className="btn-secondary" onClick={() => navigate("/contributions")}>Cancel</button>
          <button type="submit" className="btn-primary flex items-center gap-2" disabled={saving} data-testid="contrib-save-button">
            <Save className="w-4 h-4" /> {saving ? "Saving…" : "Save & generate receipt"}
          </button>
        </div>
      </form>
    </div>
  );
}
