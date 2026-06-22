import React, { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import api from "@/lib/api";
import { useAuth } from "@/lib/auth";
import {
  MEMBERSHIP_STATUSES, GENDERS, MARITAL, apiErrorMessage,
} from "@/lib/constants";
import { ArrowLeft, Save, Trash2 } from "lucide-react";

const empty = {
  first_name: "", middle_name: "", last_name: "",
  gender: "Male", date_of_birth: "",
  membership_status: "Active", membership_date: "", baptism_date: "",
  ministries: [], cell_group: "",
  marital_status: "Single", wedding_anniversary: "",
  occupation: "", employer: "", notes: "",
  phone_primary: "", phone_secondary: "", whatsapp: "", email: "",
  address_street: "", address_city: "", country_origin: "", country_current: "",
  photo_url: "",
};

export default function MemberForm() {
  const { id } = useParams();
  const isEdit = !!id;
  const { hasRole } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(empty);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isEdit) return;
    api.get(`/members/${id}`)
      .then((r) => setForm({ ...empty, ...r.data, ministries: r.data.ministries || [] }))
      .catch((e) => setError(apiErrorMessage(e)))
      .finally(() => setLoading(false));
  }, [id, isEdit]);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  const setMin = (e) => setForm((f) => ({
    ...f,
    ministries: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
  }));

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const payload = { ...form };
      // ensure date strings as ISO
      ["date_of_birth","membership_date","baptism_date","wedding_anniversary"].forEach(k => {
        if (payload[k] === "") payload[k] = null;
      });
      if (isEdit) {
        await api.patch(`/members/${id}`, payload);
      } else {
        await api.post("/members", payload);
      }
      navigate("/members");
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const remove = async () => {
    if (!window.confirm("Deactivate this member? Records are retained.")) return;
    await api.delete(`/members/${id}`);
    navigate("/members");
  };

  if (loading) return <div>Loading…</div>;

  return (
    <div data-testid="member-form-page">
      <Link to="/members" className="inline-flex items-center text-sm mb-6" style={{ color: "var(--text-secondary)" }}>
        <ArrowLeft className="w-4 h-4 mr-1" /> Back to members
      </Link>
      <h1 className="font-display text-4xl mb-8">{isEdit ? "Edit Member" : "Add New Member"}</h1>

      <form onSubmit={submit} className="space-y-8" data-testid="member-form">
        <Section title="Identity">
          <Grid>
            <Field label="First name *"><input className="input-field" required value={form.first_name} onChange={set("first_name")} data-testid="first-name-input" /></Field>
            <Field label="Middle name"><input className="input-field" value={form.middle_name} onChange={set("middle_name")} /></Field>
            <Field label="Last name *"><input className="input-field" required value={form.last_name} onChange={set("last_name")} data-testid="last-name-input" /></Field>
            <Field label="Gender"><Select value={form.gender} onChange={set("gender")} options={GENDERS} /></Field>
            <Field label="Date of birth *"><input type="date" required className="input-field" value={form.date_of_birth || ""} onChange={set("date_of_birth")} data-testid="dob-input" /></Field>
            <Field label="Photo URL (optional)"><input className="input-field" value={form.photo_url} onChange={set("photo_url")} /></Field>
          </Grid>
        </Section>

        <Section title="Membership">
          <Grid>
            <Field label="Status"><Select value={form.membership_status} onChange={set("membership_status")} options={MEMBERSHIP_STATUSES} /></Field>
            <Field label="Membership date"><input type="date" className="input-field" value={form.membership_date || ""} onChange={set("membership_date")} /></Field>
            <Field label="Baptism date"><input type="date" className="input-field" value={form.baptism_date || ""} onChange={set("baptism_date")} /></Field>
            <Field label="Cell group / Zone"><input className="input-field" value={form.cell_group} onChange={set("cell_group")} /></Field>
            <Field label="Ministries (comma-separated)"><input className="input-field" value={(form.ministries || []).join(", ")} onChange={setMin} /></Field>
            <Field label="Marital status"><Select value={form.marital_status} onChange={set("marital_status")} options={MARITAL} /></Field>
            {form.marital_status === "Married" && (
              <Field label="Wedding anniversary"><input type="date" className="input-field" value={form.wedding_anniversary || ""} onChange={set("wedding_anniversary")} /></Field>
            )}
            <Field label="Occupation"><input className="input-field" value={form.occupation} onChange={set("occupation")} /></Field>
            <Field label="Employer"><input className="input-field" value={form.employer} onChange={set("employer")} /></Field>
          </Grid>
        </Section>

        <Section title="Contact">
          <Grid>
            <Field label="Primary phone"><input className="input-field" value={form.phone_primary} onChange={set("phone_primary")} /></Field>
            <Field label="Secondary phone"><input className="input-field" value={form.phone_secondary} onChange={set("phone_secondary")} /></Field>
            <Field label="WhatsApp"><input className="input-field" value={form.whatsapp} onChange={set("whatsapp")} /></Field>
            <Field label="Email"><input type="email" className="input-field" value={form.email} onChange={set("email")} /></Field>
            <Field label="Street"><input className="input-field" value={form.address_street} onChange={set("address_street")} /></Field>
            <Field label="City"><input className="input-field" value={form.address_city} onChange={set("address_city")} /></Field>
            <Field label="Country of origin"><input className="input-field" value={form.country_origin} onChange={set("country_origin")} /></Field>
            <Field label="Current country"><input className="input-field" value={form.country_current} onChange={set("country_current")} /></Field>
          </Grid>
        </Section>

        {hasRole("admin") && (
          <Section title="Pastoral Notes (admin only)">
            <textarea
              className="input-field"
              rows={4}
              value={form.notes}
              onChange={set("notes")}
              data-testid="pastoral-notes-input"
              placeholder="Private notes visible only to Admins…"
            />
          </Section>
        )}

        {error && <div className="text-sm py-2 px-3 rounded-md" style={{ background: "rgba(139,58,58,0.08)", color: "var(--danger)" }} data-testid="member-form-error">{error}</div>}

        <div className="flex justify-between items-center pt-2">
          {isEdit && hasRole("admin") ? (
            <button type="button" className="text-sm flex items-center gap-2" style={{ color: "var(--danger)" }} onClick={remove} data-testid="member-deactivate">
              <Trash2 className="w-4 h-4" /> Deactivate member
            </button>
          ) : <div />}
          <div className="flex gap-3">
            <button type="button" className="btn-secondary" onClick={() => navigate("/members")}>Cancel</button>
            <button type="submit" className="btn-primary flex items-center gap-2" disabled={saving} data-testid="member-save-button">
              <Save className="w-4 h-4" /> {saving ? "Saving…" : "Save member"}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}

const Section = ({ title, children }) => (
  <div className="surface-card p-6 sm:p-8">
    <h2 className="font-display text-2xl mb-5">{title}</h2>
    {children}
  </div>
);
const Grid = ({ children }) => <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">{children}</div>;
const Field = ({ label, children }) => (
  <div>
    <label className="field-label">{label}</label>
    {children}
  </div>
);
const Select = ({ value, onChange, options }) => (
  <select className="input-field" value={value} onChange={onChange}>
    {options.map((o) => <option key={o} value={o}>{o}</option>)}
  </select>
);

