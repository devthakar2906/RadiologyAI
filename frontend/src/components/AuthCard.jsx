export default function AuthCard({ title, subtitle, children }) {
  return (
    <div className="mx-auto w-full max-w-md rounded-3xl border border-white/10 bg-slate-900/75 p-8 shadow-2xl shadow-sky-950/20 backdrop-blur">
      <h1 className="text-3xl font-bold text-white">{title}</h1>
      <p className="mt-2 text-sm text-slate-300">{subtitle}</p>
      <div className="mt-8">{children}</div>
    </div>
  );
}
