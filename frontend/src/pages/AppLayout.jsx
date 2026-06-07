import React from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "@/lib/auth";
import {
  Church,
  LayoutDashboard,
  Users,
  Users2,
  Coins,
  FileBarChart,
  Settings,
  LogOut,
  Shield,
  Activity,
} from "lucide-react";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, min: "read_only", testId: "nav-dashboard" },
  { to: "/members", label: "Members", icon: Users, min: "read_only", testId: "nav-members" },
  { to: "/families", label: "Families", icon: Users2, min: "read_only", testId: "nav-families" },
  { to: "/contributions", label: "Tithes & Offerings", icon: Coins, min: "admin", testId: "nav-contributions" },
  { to: "/reports", label: "Reports", icon: FileBarChart, min: "staff", testId: "nav-reports" },
  { to: "/users", label: "Users", icon: Shield, min: "super_admin", testId: "nav-users" },
  { to: "/audit", label: "Audit Log", icon: Activity, min: "admin", testId: "nav-audit" },
];

export default function AppLayout() {
  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex" style={{ background: "var(--bg-primary)" }} data-testid="app-shell">
      <aside className="w-64 shrink-0 border-r flex flex-col" style={{ borderColor: "var(--border)", background: "var(--surface)" }}>
        <div className="p-6 border-b" style={{ borderColor: "var(--border)" }}>
          <div className="flex items-center gap-2">
            <Church className="w-6 h-6 brand-text" />
            <div>
              <div className="font-display text-xl leading-none">City revival ag church</div>
              <div className="small-label mt-1">Church CMS</div>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {NAV.filter((n) => hasRole(n.min)).map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.to === "/"}
              data-testid={n.testId}
              className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}
            >
              <n.icon className="w-4 h-4" strokeWidth={1.75} />
              <span>{n.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t" style={{ borderColor: "var(--border)" }}>
          <div className="flex items-center gap-3 mb-3">
            <div
              className="w-9 h-9 rounded-full flex items-center justify-center text-white font-medium"
              style={{ background: "var(--brand)" }}
            >
              {user?.full_name?.[0] || user?.username?.[0]?.toUpperCase()}
            </div>
            <div className="min-w-0">
              <div className="text-sm font-medium truncate">{user?.full_name}</div>
              <div className="text-xs capitalize" style={{ color: "var(--text-secondary)" }}>
                {user?.role?.replace("_", " ")}
              </div>
            </div>
          </div>
          <button
            onClick={() => { logout(); navigate("/login"); }}
            data-testid="logout-button"
            className="w-full flex items-center justify-center gap-2 text-sm py-2 rounded-md transition-colors"
            style={{ background: "var(--bg-secondary)", color: "var(--text-primary)" }}
          >
            <LogOut className="w-4 h-4" strokeWidth={1.75} />
            Sign out
          </button>
        </div>
      </aside>

      <main className="flex-1 min-w-0">
        <div className="px-8 py-8 max-w-[1400px] mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
