import React, { useEffect, useState } from "react";
import api from "@/lib/api";
import { formatDate } from "@/lib/constants";

export default function AuditLog() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/audit-logs", { params: { limit: 200 } })
      .then((r) => setLogs(r.data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div data-testid="audit-page">
      <div className="mb-8">
        <div className="small-label">System</div>
        <h1 className="font-display text-4xl mt-2">Audit Trail</h1>
        <p className="text-sm mt-2" style={{ color: "var(--text-secondary)" }}>
          Chronological log of significant activity across the system.
        </p>
      </div>

      <div className="surface-card overflow-hidden">
        <table className="cms-table">
          <thead><tr><th>Timestamp</th><th>User</th><th>Action</th><th>Entity</th><th>Details</th></tr></thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={5} className="text-center" style={{ color: "var(--text-secondary)" }}>Loading…</td></tr>
            ) : logs.length === 0 ? (
              <tr><td colSpan={5} className="text-center" style={{ color: "var(--text-secondary)" }}>No activity yet.</td></tr>
            ) : logs.map((l) => (
              <tr key={l.id}>
                <td className="text-xs" style={{ color: "var(--text-muted)" }}>{formatDate(l.timestamp)}</td>
                <td>{l.username}</td>
                <td className="capitalize">{l.action}</td>
                <td className="capitalize">{l.entity}</td>
                <td className="text-xs" style={{ color: "var(--text-secondary)" }}>{l.details && Object.keys(l.details).length ? JSON.stringify(l.details) : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
