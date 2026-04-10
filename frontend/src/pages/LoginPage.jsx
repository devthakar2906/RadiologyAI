import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import AuthCard from "../components/AuthCard";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await login({
        email: form.email.trim().toLowerCase(),
        password: form.password
      });
      navigate("/report");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Login failed");
    }
  };

  return (
    <main className="auth-shell">
      <AuthCard title="Welcome Back" subtitle="Sign in to generate radiology reports from voice dictations.">
        <form className="space-y-4" onSubmit={handleSubmit}>
          <input className="input" placeholder="Email" type="email" required onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="input" placeholder="Password" type="password" required onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <button className="primary-button w-full" type="submit">Login</button>
        </form>
        <p className="mt-4 text-sm text-slate-600 dark:text-slate-300">
          Need an account? <Link className="text-slate-700 dark:text-sky-300" to="/signup">Sign up</Link>
        </p>
      </AuthCard>
    </main>
  );
}
