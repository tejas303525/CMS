// Shared constants for the CMS frontend

export const MEMBERSHIP_STATUSES = ["Active", "Inactive", "Visitor", "Transferred"];
export const GENDERS = ["Male", "Female", "Other"];
export const MARITAL = ["Single", "Married", "Widowed", "Divorced"];
export const CONTRIBUTION_TYPES = ["Tithe", "Offering", "Seed", "Pledge", "First Fruit", "Special"];
export const PAYMENT_MODES = ["Cash", "Bank Transfer", "Cheque", "Online", "POS"];
export const RELATIONSHIPS = ["Spouse", "Son", "Daughter", "Parent", "Sibling", "Guardian", "Other"];
export const ROLES = [
  { value: "super_admin", label: "Super Admin" },
  { value: "admin", label: "Admin" },
  { value: "staff", label: "Staff" },
  { value: "read_only", label: "Read-Only" },
];
export const MONTHS = [
  "January","February","March","April","May","June",
  "July","August","September","October","November","December",
];

export const formatAED = (n) =>
  `AED ${Number(n || 0).toLocaleString("en-AE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

export const formatDate = (iso) => {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
  } catch { return iso; }
};

export const ageFromDob = (iso) => {
  if (!iso) return "";
  const d = new Date(iso);
  const now = new Date();
  let age = now.getFullYear() - d.getFullYear();
  const m = now.getMonth() - d.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < d.getDate())) age--;
  return age;
};

export const apiErrorMessage = (e) => {
  const d = e?.response?.data?.detail;
  if (!d) return e?.message || "Something went wrong";
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((x) => x?.msg || JSON.stringify(x)).join(", ");
  return String(d);
};
