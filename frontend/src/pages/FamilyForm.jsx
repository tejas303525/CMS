import React, { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import api from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { RELATIONSHIPS, formatDate, ageFromDob, apiErrorMessage } from "@/lib/constants";
import { ArrowLeft, Save, Plus, Trash2, Cake, Heart } from "lucide-react";

export default function FamilyForm() {
  const { id } = useParams();
  const isEdit = !!id;
  const navigate = useNavigate();
  const { hasRole } = useAuth();
  const [members, setMembers] = useState([]);
  const [familyName, setFamilyName] = useState("");
  const [headId, setHeadId] = useState("");
  const [familyMembers, setFamilyMembers] = useState([]);
  const [enriched, setEnriched] = useState(null);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get("/members").then((r) => setMembers(r.data));
    if (isEdit) {
      api.get(`/families/${id}`).then((r) => {
        setFamilyName(r.data.family_name);
        setHeadId(r.data.head_member_id);
        setFamilyMembers(r.data.members || []);
        setEnriched(r.data);
      });
    }
  }, [id, isEdit]);

  const addRow = () => setFamilyMembers((arr) => [...arr, { member_id: "", relationship_type: "Spouse" }]);
  const removeRow = (i) => setFamilyMembers((arr) => arr.filter((_, idx) => idx !== i));
  const updateRow = (i, k, v) => setFamilyMembers((arr) => arr.map((row, idx) => idx === i ? { ...row, [k]: v } : row));

  const submit = async (e) => {
    e.preventDefault();
    if (!headId) { setError("Please choose a head of household."); return; }
    setSaving(true); setError("");
    try {
      const payload = {
        family_name: familyName,
        head_member_id: headId,
        members: familyMembers.filter((m) => m.member_id),
      };
      if (isEdit) await api.patch(`/families/${id}`, payload);
      else await api.post("/families", payload);
      navigate("/families");
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally { setSaving(false); }
  };

  const removeFamily = async () => {
    if (!window.confirm("Delete this family record?")) return;
    await api.delete(`/families/${id}`);
    navigate("/families");
  };

  return (
    <div data-testid="family-form-page">
      <Link to="/families" className="inline-flex items-center text-sm mb-6" style={{ color: "var(--text-secondary)" }}>
        <ArrowLeft className="w-4 h-4 mr-1" /> Back to families
      </Link>
      <h1 className="font-display text-4xl mb-8">{isEdit ? "Edit Family" : "New Family"}</h1>

      <form onSubmit={submit} className="space-y-6">
        <div className="surface-card p-6 grid md:grid-cols-2 gap-5">
          <div>
            <label className="field-label">Family name *</label>
            <input className="input-field" required value={familyName} onChange={(e) => setFamilyName(e.target.value)} data-testid="family-name-input" />
          </div>
          <div>
            <label className="field-label">Head of household *</label>
            <select className="input-field" required value={headId} onChange={(e) => setHeadId(e.target.value)} data-testid="family-head-select">
              <option value="">Select a member…</option>
              {members.map((m) => <option key={m.id} value={m.id}>{m.first_name} {m.last_name} — {m.member_id}</option>)}
            </select>
          </div>
        </div>

        <div className="surface-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-display text-2xl">Family Members</h2>
            <button type="button" className="btn-secondary text-sm flex items-center gap-2" onClick={addRow} data-testid="add-family-member-row">
              <Plus className="w-4 h-4" /> Add member
            </button>
          </div>
          {familyMembers.length === 0 ? (
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>No additional members yet.</p>
          ) : (
            <div className="space-y-3">
              {familyMembers.map((row, i) => (
                <div className="grid md:grid-cols-3 gap-3 items-end" key={i}>
                  <div>
                    <label className="field-label">Member</label>
                    <select className="input-field" value={row.member_id} onChange={(e) => updateRow(i, "member_id", e.target.value)}>
                      <option value="">Select…</option>
                      {members.filter((m) => m.id !== headId).map((m) => <option key={m.id} value={m.id}>{m.first_name} {m.last_name}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="field-label">Relationship</label>
                    <select className="input-field" value={row.relationship_type} onChange={(e) => updateRow(i, "relationship_type", e.target.value)}>
                      {RELATIONSHIPS.map((r) => <option key={r} value={r}>{r}</option>)}
                    </select>
                  </div>
                  <button type="button" className="text-sm flex items-center gap-2" style={{ color: "var(--danger)" }} onClick={() => removeRow(i)}>
                    <Trash2 className="w-4 h-4" /> Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {error && <div className="text-sm py-2 px-3 rounded-md" style={{ background: "rgba(139,58,58,0.08)", color: "var(--danger)" }}>{error}</div>}

        <div className="flex justify-between">
          {isEdit && hasRole("admin") ? (
            <button type="button" className="text-sm flex items-center gap-2" style={{ color: "var(--danger)" }} onClick={removeFamily}>
              <Trash2 className="w-4 h-4" /> Delete family
            </button>
          ) : <div />}
          <div className="flex gap-3">
            <button type="button" className="btn-secondary" onClick={() => navigate("/families")}>Cancel</button>
            <button type="submit" className="btn-primary flex items-center gap-2" disabled={saving} data-testid="family-save-button">
              <Save className="w-4 h-4" /> {saving ? "Saving…" : "Save family"}
            </button>
          </div>
        </div>
      </form>

      {isEdit && enriched && (
        <div className="surface-card p-6 mt-8">
          <h3 className="font-display text-2xl mb-4">Members in this family</h3>
          <table className="cms-table">
            <thead><tr><th>Name</th><th>Relationship</th><th>DOB</th><th>Age</th></tr></thead>
            <tbody>
              {[
                enriched.head_member && { ...enriched.head_member, relationship_type: "Head" },
                ...((enriched.enriched_members || []))
              ].filter(Boolean).map((m) => (
                <tr key={m.id}>
                  <td><Link to={`/members/${m.id}`} className="hover:underline font-medium">{m.first_name} {m.last_name}</Link></td>
                  <td>{m.relationship_type}</td>
                  <td>{formatDate(m.date_of_birth)} <UpcomingBirthdayBadge dob={m.date_of_birth} /></td>
                  <td>{ageFromDob(m.date_of_birth)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {enriched.head_member?.wedding_anniversary && (
            <div className="mt-4 flex items-center gap-2 text-sm" style={{ color: "var(--text-secondary)" }}>
              <Heart className="w-4 h-4 accent-text" />
              Wedding anniversary: {formatDate(enriched.head_member.wedding_anniversary)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const UpcomingBirthdayBadge = ({ dob }) => {
  if (!dob) return null;
  try {
    const today = new Date();
    const d = new Date(dob);
    const next = new Date(today.getFullYear(), d.getMonth(), d.getDate());
    if (next < today) next.setFullYear(today.getFullYear() + 1);
    const days = Math.round((next - today) / (1000 * 60 * 60 * 24));
    if (days <= 30) {
      return <span className="ml-2 status-pill status-visitor"><Cake className="w-3 h-3 mr-1" />in {days}d</span>;
    }
  } catch {}
  return null;
};
