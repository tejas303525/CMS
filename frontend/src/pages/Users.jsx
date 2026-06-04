import React, { useEffect, useState } from "react";
import api from "@/lib/api";
import { ROLES, apiErrorMessage, formatDate } from "@/lib/constants";
import { UserPlus, Shield, Trash2, X } from "lucide-react";

export default function Users() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [editing, setEditing] = useState(null);

  const load = () => {
    setLoading(true);
    api.get("/users").then((r) => setUsers(r.data)).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

  return (
    <div data-testid="users-page">
      <div className="flex items-end justify-between mb-8">
        <div>
          <div className="small-label">Access control</div>
          <h1 className="font-display text-4xl mt-2">Users</h1>
        </div>
        <button className="btn-primary flex items-center gap-2" onClick={() => setCreating(true)} data-testid="add-user-button">
          <UserPlus className="w-4 h-4" /> New user
        </button>
      </div>

      <div className="surface-card overflow-hidden">
        <table className="cms-table" data-testid="users-table">
          <thead><tr><th>Username</th><th>Full name</th><th>Role</th><th>Status</th><th>Last login</th><th></th></tr></thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={6} className="text-center" style={{ color: "var(--text-secondary)" }}>Loading…</td></tr>
            ) : users.map((u) => (
              <tr key={u.id} data-testid={`user-row-${u.username}`}>
                <td className="font-medium">{u.username}</td>
                <td>{u.full_name}</td>
                <td><span className="status-pill status-active capitalize">{u.role.replace("_", " ")}</span></td>
                <td>{u.is_active ? "Active" : <span style={{ color: "var(--danger)" }}>Disabled</span>}</td>
                <td className="text-xs" style={{ color: "var(--text-secondary)" }}>{u.last_login ? formatDate(u.last_login) : "Never"}</td>
                <td className="text-right">
                  <button className="text-sm brand-text mr-3 hover:underline" onClick={() => setEditing(u)} data-testid={`edit-user-${u.username}`}>Edit</button>
                  <button className="text-sm" style={{ color: "var(--danger)" }} onClick={async () => {
                    if (!window.confirm(`Delete user ${u.username}?`)) return;
                    await api.delete(`/users/${u.id}`);
                    load();
                  }}>
                    <Trash2 className="w-4 h-4 inline" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {(creating || editing) && (
        <UserModal user={editing} onClose={() => { setCreating(false); setEditing(null); }} onSaved={() => { setCreating(false); setEditing(null); load(); }} />
      )}
    </div>
  );
}

function UserModal({ user, onClose, onSaved }) {
  const isEdit = !!user;
  const [form, setForm] = useState({
    username: user?.username || "",
    full_name: user?.full_name || "",
    role: user?.role || "staff",
    is_active: user?.is_active ?? true,
    password: "",
  });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true); setError("");
    try {
      if (isEdit) {
        const payload = { full_name: form.full_name, role: form.role, is_active: form.is_active };
        if (form.password) payload.password = form.password;
        await api.patch(`/users/${user.id}`, payload);
      } else {
        await api.post("/users", form);
      }
      onSaved();
    } catch (err) { setError(apiErrorMessage(err)); }
    finally { setSaving(false); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "rgba(28,25,23,0.45)" }} data-testid="user-modal">
      <div className="surface-card p-6 w-full max-w-md" style={{ background: "white" }}>
        <div className="flex items-start justify-between mb-4">
          <h3 className="font-display text-2xl">{isEdit ? "Edit User" : "New User"}</h3>
          <button onClick={onClose}><X className="w-5 h-5" /></button>
        </div>
        <form onSubmit={submit} className="space-y-4">
          {!isEdit && (
            <div>
              <label className="field-label">Username *</label>
              <input className="input-field" required value={form.username} onChange={set("username")} data-testid="user-username-input" />
            </div>
          )}
          <div>
            <label className="field-label">Full name *</label>
            <input className="input-field" required value={form.full_name} onChange={set("full_name")} data-testid="user-fullname-input" />
          </div>
          <div>
            <label className="field-label">Role *</label>
            <select className="input-field" value={form.role} onChange={set("role")} data-testid="user-role-input">
              {ROLES.map((r) => <option key={r.value} value={r.value}>{r.label}</option>)}
            </select>
          </div>
          <div>
            <label className="field-label">{isEdit ? "New password (leave blank to keep)" : "Password *"}</label>
            <input className="input-field" type="password" required={!isEdit} value={form.password} onChange={set("password")} data-testid="user-password-input" />
          </div>
          {isEdit && (
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={form.is_active} onChange={(e) => setForm((f) => ({ ...f, is_active: e.target.checked }))} />
              Active account
            </label>
          )}
          {error && <div className="text-sm py-2 px-3 rounded-md" style={{ background: "rgba(139,58,58,0.08)", color: "var(--danger)" }}>{error}</div>}
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn-primary" disabled={saving} data-testid="user-save-button">
              {saving ? "Saving…" : "Save user"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
