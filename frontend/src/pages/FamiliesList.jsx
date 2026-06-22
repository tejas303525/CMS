import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Users2, Plus } from "lucide-react";

export default function FamiliesList() {
  const { hasRole } = useAuth();
  const [families, setFamilies] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.get("/families"), api.get("/members")])
      .then(([f, m]) => { setFamilies(f.data); setMembers(m.data); })
      .finally(() => setLoading(false));
  }, []);

  const membersById = Object.fromEntries(members.map((m) => [m.id, m]));

  return (
    <div data-testid="families-page">
      <div className="flex items-end justify-between mb-8">
        <div>
          <div className="small-label">Households</div>
          <h1 className="font-display text-4xl mt-2">Families</h1>
        </div>
        {hasRole("staff") && (
          <Link to="/families/new" className="btn-primary inline-flex items-center gap-2" data-testid="add-family-button">
            <Plus className="w-4 h-4" /> New family
          </Link>
        )}
      </div>

      {loading ? (
        <div>Loading…</div>
      ) : families.length === 0 ? (
        <div className="surface-card p-12 text-center">
          <Users2 className="w-8 h-8 mx-auto accent-text mb-3" />
          <h3 className="font-display text-2xl">No families yet</h3>
          <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>Create a family record to group members together.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {families.map((f) => {
            const head = membersById[f.head_member_id];
            return (
              <Link to={`/families/${f.id}`} key={f.id} className="surface-card p-6 hover:shadow-md transition-shadow" data-testid={`family-card-${f.id}`}>
                <div className="small-label">{f.members?.length + 1 || 1} members</div>
                <h3 className="font-display text-2xl mt-2">{f.family_name}</h3>
                <div className="text-sm mt-3" style={{ color: "var(--text-secondary)" }}>
                  Head: {head ? `${head.first_name} ${head.last_name}` : "—"}
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

