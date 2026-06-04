import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { formatAED, formatDate } from "@/lib/constants";
import {
  UserPlus,
  Plus,
  CalendarHeart,
  Cake,
  TrendingUp,
  TrendingDown,
  Users,
  ArrowRight,
} from "lucide-react";

const StatCard = ({ label, value, sub, icon: Icon, testId, accent = false }) => (
  <div className="surface-card p-6" data-testid={testId}>
    <div className="flex items-start justify-between">
      <div>
        <div className="small-label">{label}</div>
        <div className="font-display text-4xl mt-3" style={{ color: accent ? "var(--brand)" : "var(--text-primary)" }}>
          {value}
        </div>
        {sub && <div className="text-xs mt-2" style={{ color: "var(--text-secondary)" }}>{sub}</div>}
      </div>
      <div className="w-10 h-10 rounded-lg flex items-center justify-center"
           style={{ background: "var(--bg-secondary)", color: "var(--brand)" }}>
        <Icon className="w-5 h-5" strokeWidth={1.75} />
      </div>
    </div>
  </div>
);

export default function Dashboard() {
  const { user, hasRole } = useAuth();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/dashboard/summary")
      .then((r) => setData(r.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-sm" style={{ color: "var(--text-secondary)" }}>Loading dashboard…</div>;
  if (!data) return null;

  const delta = data.tithes_this_month - data.tithes_last_month;
  const deltaPct = data.tithes_last_month
    ? ((delta / data.tithes_last_month) * 100).toFixed(1)
    : null;

  return (
    <div data-testid="dashboard-page">
      <div className="flex items-end justify-between mb-8">
        <div>
          <div className="small-label">Welcome back, {user?.full_name}</div>
          <h1 className="font-display text-4xl mt-2">Parish Overview</h1>
        </div>
        <div className="flex gap-3">
          {hasRole("staff") && (
            <button
              className="btn-secondary flex items-center gap-2"
              onClick={() => navigate("/members/new")}
              data-testid="quick-add-member"
            >
              <UserPlus className="w-4 h-4" /> Add member
            </button>
          )}
          {hasRole("admin") && (
            <button
              className="btn-primary flex items-center gap-2"
              onClick={() => navigate("/contributions/new")}
              data-testid="quick-record-tithe"
            >
              <Plus className="w-4 h-4" /> Record tithe
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <StatCard label="Active Members" value={data.active_members} icon={Users} testId="stat-active-members" accent />
        <StatCard label="New this month" value={data.new_members_this_month} icon={UserPlus} testId="stat-new-members"
                  sub="Since the 1st" />
        {data.show_finance ? (
          <>
            <StatCard
              label="Tithes (This Month)"
              value={formatAED(data.tithes_this_month)}
              icon={delta >= 0 ? TrendingUp : TrendingDown}
              testId="stat-tithes-month"
              sub={deltaPct != null ? `${delta >= 0 ? "▲" : "▼"} ${Math.abs(deltaPct)}% vs last month` : "No prior month data"}
            />
            <StatCard
              label="Tithes (Last Month)"
              value={formatAED(data.tithes_last_month)}
              icon={TrendingUp}
              testId="stat-tithes-last-month"
            />
          </>
        ) : (
          <div className="surface-card p-6 md:col-span-2 flex items-center" data-testid="finance-hidden">
            <div>
              <div className="small-label">Financial Overview</div>
              <p className="text-sm mt-2" style={{ color: "var(--text-secondary)" }}>
                Tithes & offerings are visible to Admins and above.
              </p>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <UpcomingList
          title="Upcoming Birthdays"
          icon={Cake}
          items={data.upcoming_birthdays}
          testId="upcoming-birthdays"
          emptyText="No birthdays in the next 7 days."
        />
        <UpcomingList
          title="Upcoming Anniversaries"
          icon={CalendarHeart}
          items={data.upcoming_anniversaries}
          testId="upcoming-anniversaries"
          emptyText="No anniversaries in the next 7 days."
        />

        <div className="surface-card p-6" data-testid="recent-activity">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-display text-xl">Recent Activity</h3>
          </div>
          {data.recent_activity.length === 0 ? (
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>No activity yet.</p>
          ) : (
            <ul className="space-y-3">
              {data.recent_activity.map((l) => (
                <li key={l.id} className="text-sm flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full mt-2" style={{ background: "var(--accent)" }} />
                  <div className="flex-1 min-w-0">
                    <div>
                      <span className="font-medium">{l.username}</span>{" "}
                      <span style={{ color: "var(--text-secondary)" }}>
                        {l.action} {l.entity}
                      </span>
                    </div>
                    <div className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
                      {formatDate(l.timestamp)}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

const UpcomingList = ({ title, icon: Icon, items, testId, emptyText }) => (
  <div className="surface-card p-6" data-testid={testId}>
    <div className="flex items-center justify-between mb-4">
      <h3 className="font-display text-xl flex items-center gap-2">
        <Icon className="w-4 h-4 accent-text" />
        {title}
      </h3>
    </div>
    {items.length === 0 ? (
      <p className="text-sm" style={{ color: "var(--text-secondary)" }}>{emptyText}</p>
    ) : (
      <ul className="space-y-3">
        {items.map((it) => (
          <li key={it.id + it.next_occurrence} className="flex items-center justify-between text-sm">
            <Link to={`/members/${it.id}`} className="hover:underline">
              <div className="font-medium">{it.name}</div>
              <div className="text-xs" style={{ color: "var(--text-muted)" }}>
                {formatDate(it.date)}
              </div>
            </Link>
            <span
              className="text-xs px-2 py-1 rounded-md"
              style={{ background: "var(--bg-secondary)", color: "var(--text-secondary)" }}
            >
              {it.in_days === 0 ? "Today" : `in ${it.in_days}d`}
            </span>
          </li>
        ))}
      </ul>
    )}
  </div>
);
