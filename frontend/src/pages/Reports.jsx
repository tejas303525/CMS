import React, { useState } from "react";
import api from "@/lib/api";
import { MONTHS } from "@/lib/constants";
import { FileDown, FileSpreadsheet, FileText } from "lucide-react";
import { downloadAuthed } from "@/pages/MemberDetail";

const REPORTS = [
  {
    key: "members",
    title: "Member Directory",
    description: "Full list of members with contact details and status.",
    fields: [{ key: "status", label: "Status (optional)", type: "select", options: ["", "Active", "Inactive", "Visitor", "Transferred"] }],
    pathFn: (v) => `/reports/members?${v.status ? `status=${v.status}&` : ""}format=`,
    filenameBase: "member_directory",
    minRole: "staff",
  },
  {
    key: "birthdays",
    title: "Birthday Report",
    description: "Members with birthdays in a selected month.",
    fields: [{ key: "month", label: "Month *", type: "month", required: true }],
    pathFn: (v) => `/reports/birthdays?month=${v.month}&format=`,
    filenameBase: "birthdays",
    minRole: "staff",
  },
  {
    key: "anniversaries",
    title: "Anniversary Report",
    description: "Wedding anniversaries falling in a selected month.",
    fields: [{ key: "month", label: "Month *", type: "month", required: true }],
    pathFn: (v) => `/reports/anniversaries?month=${v.month}&format=`,
    filenameBase: "anniversaries",
    minRole: "staff",
  },
  {
    key: "contrib-monthly",
    title: "Monthly Contribution Summary",
    description: "All contributions recorded in a specific month and year.",
    fields: [
      { key: "year", label: "Year *", type: "year", required: true },
      { key: "month", label: "Month *", type: "month", required: true },
    ],
    pathFn: (v) => `/reports/contributions-monthly?year=${v.year}&month=${v.month}&format=`,
    filenameBase: "contributions_monthly",
    minRole: "admin",
  },
  {
    key: "non-contrib",
    title: "Non-Contributing Members",
    description: "Active members with no recorded contributions recently.",
    fields: [{ key: "months", label: "No contribution in (months)", type: "number", default: 2 }],
    pathFn: (v) => `/reports/non-contributing?months=${v.months || 2}&format=`,
    filenameBase: "non_contributing",
    minRole: "admin",
  },
  {
    key: "families",
    title: "Family Report",
    description: "List of families with heads and member counts.",
    fields: [],
    pathFn: () => `/reports/families?format=`,
    filenameBase: "families",
    minRole: "staff",
  },
];

export default function Reports() {
  return (
    <div data-testid="reports-page">
      <div className="mb-8">
        <div className="small-label">Insights</div>
        <h1 className="font-display text-4xl mt-2">Reports</h1>
        <p className="text-sm mt-2" style={{ color: "var(--text-secondary)" }}>
          Export church records in PDF or Excel. All financial figures in <strong>INR</strong>.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {REPORTS.map((r) => <ReportCard key={r.key} report={r} />)}
      </div>
    </div>
  );
}

function ReportCard({ report }) {
  const [vals, setVals] = useState(
    Object.fromEntries(report.fields.map((f) => [f.key, f.default ?? (f.type === "year" ? new Date().getFullYear() : (f.type === "month" ? new Date().getMonth() + 1 : ""))]))
  );
  const [busy, setBusy] = useState(false);

  const download = async (format) => {
    for (const f of report.fields) {
      if (f.required && !vals[f.key]) { alert(`Please provide ${f.label.replace(" *", "")}`); return; }
    }
    setBusy(true);
    try {
      const path = report.pathFn(vals) + format;
      const ext = format === "excel" ? "xlsx" : "pdf";
      await downloadAuthed(path, `${report.filenameBase}.${ext}`);
    } finally { setBusy(false); }
  };

  return (
    <div className="surface-card p-6" data-testid={`report-${report.key}`}>
      <h3 className="font-display text-2xl">{report.title}</h3>
      <p className="text-sm mt-1 mb-4" style={{ color: "var(--text-secondary)" }}>{report.description}</p>

      {report.fields.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-5">
          {report.fields.map((f) => (
            <div key={f.key}>
              <label className="field-label">{f.label}</label>
              {f.type === "select" ? (
                <select className="input-field" value={vals[f.key] || ""} onChange={(e) => setVals((v) => ({ ...v, [f.key]: e.target.value }))}>
                  {f.options.map((o) => <option key={o} value={o}>{o || "All"}</option>)}
                </select>
              ) : f.type === "month" ? (
                <select className="input-field" value={vals[f.key]} onChange={(e) => setVals((v) => ({ ...v, [f.key]: e.target.value }))}>
                  {MONTHS.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
                </select>
              ) : f.type === "year" ? (
                <select className="input-field" value={vals[f.key]} onChange={(e) => setVals((v) => ({ ...v, [f.key]: Number(e.target.value) }))}>
                  {Array.from({ length: 6 }).map((_, i) => {
                    const y = new Date().getFullYear() - i;
                    return <option key={y} value={y}>{y}</option>;
                  })}
                </select>
              ) : (
                <input type="number" className="input-field" value={vals[f.key] ?? ""} onChange={(e) => setVals((v) => ({ ...v, [f.key]: e.target.value }))} />
              )}
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-3">
        <button className="btn-secondary flex items-center gap-2" disabled={busy} onClick={() => download("pdf")} data-testid={`download-pdf-${report.key}`}>
          <FileText className="w-4 h-4" /> PDF
        </button>
        <button className="btn-primary flex items-center gap-2" disabled={busy} onClick={() => download("excel")} data-testid={`download-excel-${report.key}`}>
          <FileSpreadsheet className="w-4 h-4" /> Excel
        </button>
      </div>
    </div>
  );
}
