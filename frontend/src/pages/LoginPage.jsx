import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthCard from "../components/AuthCard";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });

  const handleSubmit = async (event) => {
    event.preventDefault();
    await login(form);
    navigate("/");
  };

  return (
    <main className="auth-shell">
      <AuthCard title="Welcome Back" subtitle="Sign in to generate radiology reports from voice dictations.">
        <form className="space-y-4" onSubmit={handleSubmit}>
          <input className="input" placeholder="Email" type="email" required onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="input" placeholder="Password" type="password" required onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <button className="primary-button w-full" type="submit">Login</button>
        </form>
        <p className="mt-4 text-sm text-slate-300">
          Need an account? <Link className="text-sky-300" to="/signup">Sign up</Link>
        </p>
      </AuthCard>
    </main>
  );
}
