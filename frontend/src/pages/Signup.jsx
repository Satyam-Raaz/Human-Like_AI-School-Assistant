import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerStudent, registerTeacher, registerParent } from "../api/api.js";

const ROLES = [
  { value: "student", label: "Student" },
  { value: "teacher", label: "Teacher" },
  { value: "parent", label: "Parent" },
];

const INITIAL_EXTRA = {
  class_name: "",
  roll_number: "",
  subject: "",
  phone: "",
  student_id: "",
};

export default function Signup() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("student");
  const [extra, setExtra] = useState(INITIAL_EXTRA);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const navigate = useNavigate();

  function updateExtra(field, value) {
    setExtra((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const base = { name, email, password };

      if (role === "student") {
        await registerStudent({
          ...base,
          class_name: extra.class_name,
          roll_number: extra.roll_number,
        });
      } else if (role === "teacher") {
        await registerTeacher({
          ...base,
          subject: extra.subject,
          class_name: extra.class_name,
        });
      } else {
        await registerParent({
          ...base,
          phone: extra.phone,
          student_id: extra.student_id,
        });
      }

      setSuccess(true);
      setTimeout(() => navigate("/login"), 1200);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-screen">
      <form className="auth-card auth-card--wide" onSubmit={handleSubmit}>
        <h1>Create your account</h1>
        <p className="auth-card__subtitle">Join as a student, teacher, or parent</p>

        {error && <div className="form-error">{error}</div>}
        {success && <div className="form-success">Account created. Redirecting to sign in...</div>}

        <label className="field">
          <span>Full name</span>
          <input value={name} onChange={(e) => setName(e.target.value)} required />
        </label>

        <label className="field">
          <span>Email</span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
          />
        </label>

        <label className="field">
          <span>Password</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="new-password"
          />
        </label>

        <fieldset className="role-picker">
          <legend>I am a...</legend>
          {ROLES.map((r) => (
            <label key={r.value} className="role-option">
              <input
                type="radio"
                name="role"
                value={r.value}
                checked={role === r.value}
                onChange={() => setRole(r.value)}
              />
              {r.label}
            </label>
          ))}
        </fieldset>

        {role === "student" && (
          <div className="field-group">
            <label className="field">
              <span>Class</span>
              <input value={extra.class_name} onChange={(e) => updateExtra("class_name", e.target.value)} required />
            </label>
            <label className="field">
              <span>Roll number</span>
              <input value={extra.roll_number} onChange={(e) => updateExtra("roll_number", e.target.value)} required />
            </label>
          </div>
        )}

        {role === "teacher" && (
          <div className="field-group">
            <label className="field">
              <span>Subject</span>
              <input value={extra.subject} onChange={(e) => updateExtra("subject", e.target.value)} required />
            </label>
            <label className="field">
              <span>Class</span>
              <input value={extra.class_name} onChange={(e) => updateExtra("class_name", e.target.value)} required />
            </label>
          </div>
        )}

        {role === "parent" && (
          <div className="field-group">
            <label className="field">
              <span>Phone</span>
              <input value={extra.phone} onChange={(e) => updateExtra("phone", e.target.value)} required />
            </label>
            <label className="field">
              <span>Child's student ID</span>
              <input value={extra.student_id} onChange={(e) => updateExtra("student_id", e.target.value)} required />
            </label>
          </div>
        )}

        <button type="submit" className="btn btn--primary" disabled={submitting}>
          {submitting ? "Creating account..." : "Create account"}
        </button>

        <p className="auth-card__footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </form>
    </div>
  );
}
