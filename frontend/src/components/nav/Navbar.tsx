import { AudioWaveform, Plus } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import "./Navbar.css";

const links = [
  { label: "Home", path: "/" },
  { label: "New Investigation", path: "/investigate" },
  { label: "Bulk Upload", path: "/bulk-upload" },
  { label: "History", path: "/history" },
];

function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <button
          className="navbar-logo"
          onClick={() => navigate("/")}
        >
          <span className="navbar-logo-mark">
            <AudioWaveform size={17} strokeWidth={2.4} />
          </span>

          <span className="navbar-logo-text">
            <strong>
              AKGP<span>.intel</span>
            </strong>
            <small>PRODUCT INTELLIGENCE</small>
          </span>
        </button>

        <nav className="navbar-links">
          {links.map((link) => {
            const active =
              link.path === "/"
                ? location.pathname === "/"
                : location.pathname.startsWith(link.path);

            return (
              <button
                key={link.path}
                className={
                  active
                    ? "navbar-link active"
                    : "navbar-link"
                }
                onClick={() => navigate(link.path)}
              >
                {link.label}
              </button>
            );
          })}
        </nav>

        <button
          className="navbar-cta"
          onClick={() => navigate("/investigate")}
        >
          <Plus size={15} strokeWidth={2.6} />
          New
        </button>
      </div>
    </header>
  );
}

export default Navbar;