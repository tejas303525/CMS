import React from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/lib/auth";

import Login from "@/pages/Login";
import AppLayout from "@/pages/AppLayout";
import Dashboard from "@/pages/Dashboard";
import MembersList from "@/pages/MembersList";
import MemberForm from "@/pages/MemberForm";
import MemberDetail from "@/pages/MemberDetail";
import FamiliesList from "@/pages/FamiliesList";
import FamilyForm from "@/pages/FamilyForm";
import Contributions from "@/pages/Contributions";
import ContributionForm from "@/pages/ContributionForm";
import Reports from "@/pages/Reports";
import Users from "@/pages/Users";
import AuditLog from "@/pages/AuditLog";

function Protected({ children, role }) {
  const { user, loading, hasRole } = useAuth();
  if (loading) return <div className="min-h-screen flex items-center justify-center text-sm" style={{ color: "var(--text-secondary)" }}>Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (role && !hasRole(role)) return <Navigate to="/" replace />;
  return children;
}

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route element={<Protected><AppLayout /></Protected>}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/members" element={<MembersList />} />
              <Route path="/members/new" element={<Protected role="staff"><MemberForm /></Protected>} />
              <Route path="/members/:id" element={<MemberDetail />} />
              <Route path="/members/:id/edit" element={<Protected role="staff"><MemberForm /></Protected>} />
              <Route path="/families" element={<FamiliesList />} />
              <Route path="/families/new" element={<Protected role="staff"><FamilyForm /></Protected>} />
              <Route path="/families/:id" element={<Protected role="staff"><FamilyForm /></Protected>} />
              <Route path="/contributions" element={<Protected role="admin"><Contributions /></Protected>} />
              <Route path="/contributions/new" element={<Protected role="admin"><ContributionForm /></Protected>} />
              <Route path="/reports" element={<Protected role="staff"><Reports /></Protected>} />
              <Route path="/users" element={<Protected role="super_admin"><Users /></Protected>} />
              <Route path="/audit" element={<Protected role="admin"><AuditLog /></Protected>} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </div>
  );
}

export default App;
