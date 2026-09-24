import { useEffect, useState } from "react";
import { getProfile } from "../api/api.js";
import { useAuth } from "../context/AuthContext.jsx";

const FIELD_LABELS = {
  id: "ID",
  name: "Name",
  email: "Email",
  class_name: "Class",
  roll_number: "Roll number",
  attendance: "Attendance",
  subject: "Subject",
  phone: "Phone",
  student_id: "Child's student ID",
};

export default function Profile() {
  const { role, token } = useAuth();
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    getProfile(role, token)
      .then((data) => {
        if (!cancelled) setProfile(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [role, token]);

  if (loading) return <div className="profile-screen">Loading profile...</div>;
  if (error) return <div className="profile-screen form-error">{error}</div>;
  if (!profile) return null;

  return (
    <div className="profile-screen">
      <div className="profile-card">
        <div className="profile-card__avatar">{profile.name?.[0]?.toUpperCase() ?? "?"}</div>
        <h1>{profile.name}</h1>
        <span className="profile-card__role">{role}</span>

        <dl className="profile-fields">
          {Object.entries(profile)
            .filter(([key]) => key !== "name")
            .map(([key, value]) => (
              <div className="profile-field" key={key}>
                <dt>{FIELD_LABELS[key] ?? key}</dt>
                <dd>{key === "attendance" && value !== null ? `${value}%` : String(value)}</dd>
              </div>
            ))}
        </dl>
      </div>
    </div>
  );
}
