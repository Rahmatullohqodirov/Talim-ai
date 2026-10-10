import React from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useApp } from "../../context/AppContext.jsx";
import StatusPill from "../../components/StatusPill.jsx";
import "./App.css";

const studentNav = [
  { group: "O'qish" },
  { to: "dashboard", label: "Bosh sahifa", dot: "oklch(0.6 0.15 275)" },
  { to: "ai-chat", label: "AI Ustoz", dot: "oklch(0.6 0.15 275)" },
  { to: "chat", label: "Avatar suhbat", dot: "oklch(0.65 0.15 200)" },
  { group: "Mashq" },
  { to: "vocabulary", label: "So'zlar", dot: "oklch(0.65 0.18 50)" },
  { to: "quiz", label: "Quiz", dot: "oklch(0.6 0.18 300)" },
  { to: "math", label: "Matematika", dot: "oklch(0.7 0.15 85)" },
  { group: "Resurslar" },
  { to: "dictionary", label: "Lug'at", dot: "oklch(0.6 0.14 155)" },
  { to: "videos", label: "Video darslar", dot: "oklch(0.65 0.18 25)" },
  { to: "courses", label: "Tashqi kurslar", dot: "oklch(0.6 0.15 155)" },
  { group: "Men" },
  { to: "leaderboard", label: "Reyting", dot: "oklch(0.65 0.18 25)" },
  { to: "billing", label: "Obuna", dot: "oklch(0.7 0.15 85)" },
];

export default function AppLayout() {
  const { role, logout } = useApp();
  const navigate = useNavigate();
  const { pathname } = useLocation();

  function handleLogout() {
    logout();
    navigate("/");
  }

  // Admin panelning o'z menyusi bor — ikkinchi (bo'sh) sidebar ko'rsatilmaydi
  if (role === "admin" && pathname.startsWith("/app/admin")) return <Outlet />;

  return (
    <div className="app-shell">
      <div className="sidebar">
        <div className="sidebar-brand">Talim</div>

        {role === "admin" ? (
          <NavLink
            to="admin"
            className={({ isActive }) =>
              "nav-item" + (isActive ? " active" : "")
            }
          >
            <span
              className="nav-dot"
              style={{ background: "oklch(0.7 0.15 275)" }}
            />
            <span>Admin panel</span>
          </NavLink>
        ) : (
          studentNav.map((n) => n.group ? (
            <div key={n.group} className="nav-group">{n.group}</div>
          ) : (
            <NavLink
              key={n.to}
              to={n.to}
              className={({ isActive }) =>
                "nav-item" + (isActive ? " active" : "")
              }
            >
              <span
                className="nav-dot"
                style={{ background: n.dot }}
              />
              <span>{n.label}</span>
            </NavLink>
          ))
        )}

        <div style={{ flex: 1 }} />

        <div style={{ padding: "0 12px 12px" }}>
          <StatusPill />
        </div>

        <div
          className="logout-item"
          onClick={handleLogout}
        >
          Chiqish
        </div>
      </div>

      <div className="content">
        <Outlet />
      </div>
    </div>
  );
}