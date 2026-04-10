import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import AuthCard from "../components/AuthCard";
import { useAuth } from "../context/AuthContext";

export default function SignupPage() {
  const navigate = useNavigate();
  const { signup } = useAuth();
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "doctor" });

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      await signup({
        ...form,
        email: form.email.trim().toLowerCase()
      });
      navigate("/");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Signup failed");
    }
  };

  return (
    <main className="auth-shell">
      <AuthCard title="Create Account" subtitle="Set up doctor or admin access for the radiology workflow.">
        <form className="space-y-4" onSubmit={handleSubmit}>
          <input className="input" placeholder="Full name" required onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input className="input" placeholder="Email" type="email" required onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="input" placeholder="Password" type="password" required onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <select className="input" defaultValue="doctor" onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option value="doctor">doctor</option>
            <option value="admin">admin</option>
          </select>
          <button className="primary-button w-full" type="submit">Sign Up</button>
        </form>
        <p className="mt-4 text-sm text-slate-600 dark:text-slate-300">
          Already registered? <Link className="text-slate-700 dark:text-sky-300" to="/login">Login</Link>
        </p>
      </AuthCard>
    </main>
  );
}
