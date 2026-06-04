import React, { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "@/lib/auth";
import { apiErrorMessage } from "@/lib/constants";
import { Church } from "lucide-react";

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (user) return <Navigate to="/" replace />;

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(username.trim(), password);
      navigate("/", { replace: true });
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2" data-testid="login-page">
      {/* Left visual panel */}
      <div className="hidden lg:flex relative overflow-hidden brand-bg">
        <div className="absolute inset-0 opacity-90">
          <img
            src="https://images.unsplash.com/photo-1473177104440-ffee2f376098?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwxfHxjaHVyY2glMjBhcmNoaXRlY3R1cmUlMjBpbnRlcmlvciUyMGxpZ2h0fGVufDB8fHx8MTc4MDU1NzI4OHww&ixlib=rb-4.1.0&q=85"
            alt="Cathedral interior"
            className="w-full h-full object-cover mix-blend-multiply opacity-70"
          />
        </div>
        <div className="absolute inset-0" style={{ background: "linear-gradient(180deg, rgba(42,75,60,0.55), rgba(28,25,23,0.85))" }} />
        <div className="relative z-10 flex flex-col justify-between p-12 text-white w-full">
          <div className="flex items-center gap-3">
            <Church className="w-7 h-7" style={{ color: "#C49A45" }} />
            <span className="small-label" style={{ color: "#E8E4D9" }}>Church Management System</span>
          </div>
          <div className="max-w-md">
            <h1 className="font-display text-5xl xl:text-6xl leading-[1.05] mb-4">
              Tend the flock with quiet excellence.
            </h1>
            <p className="text-base text-white/80 leading-relaxed">
              A calm, dignified workspace for members, families, and offerings —
              built for the rhythms of church life.
            </p>
          </div>
          <div className="text-xs text-white/60">v1.0 · Internal staff portal</div>
        </div>
      </div>

      {/* Right form panel */}
      <div className="flex items-center justify-center p-8 lg:p-16" style={{ background: "var(--bg-primary)" }}>
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <Church className="w-6 h-6 brand-text" />
            <span className="small-label">Church CMS</span>
          </div>
          <h2 className="font-display text-4xl mb-2">Welcome back</h2>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            Sign in with your assigned username to continue.
          </p>

          <form className="mt-10 space-y-5" onSubmit={submit}>
            <div>
              <label className="field-label">Username</label>
              <input
                className="input-field"
                type="text"
                placeholder="e.g. superadmin"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoFocus
                data-testid="login-username-input"
              />
            </div>
            <div>
              <label className="field-label">Password</label>
              <input
                className="input-field"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                data-testid="login-password-input"
              />
            </div>

            {error && (
              <div className="text-sm py-2 px-3 rounded-md" data-testid="login-error" style={{ background: "rgba(139,58,58,0.08)", color: "var(--danger)" }}>
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full mt-2 disabled:opacity-60"
              data-testid="login-submit-button"
            >
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </form>

          <div className="mt-10 text-xs leading-relaxed p-4 rounded-md" style={{ background: "var(--bg-secondary)", color: "var(--text-secondary)" }} data-testid="seeded-credentials">
            <div className="small-label mb-2">Seeded accounts</div>
            <div>superadmin / Admin@123 — Super Admin</div>
            <div>admin / Admin@123 — Admin</div>
            <div>staff / Staff@123 — Staff</div>
            <div>viewer / View@123 — Read-Only</div>
          </div>
        </div>
      </div>
    </div>
  );
}
