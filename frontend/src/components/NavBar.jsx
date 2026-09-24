import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function NavBar() {
  const { isAuthenticated, role, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header className="nav">
      <Link to="/" className="nav__brand">
        Schoolhouse
      </Link>

      {isAuthenticated && (
        <nav className="nav__links">
          <Link to="/chat">Chat</Link>
          <Link to="/profile">Profile</Link>
          <span className="nav__role">{role}</span>
          <button className="nav__logout" onClick={handleLogout}>
            Log out
          </button>
        </nav>
      )}
    </header>
  );
}
