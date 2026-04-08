export default function AuthCard({ title, subtitle, children }) {
  return (
    <div className="mx-auto w-full max-w-md rounded-3xl border border-slate-200/70 bg-white/85 p-8 shadow-2xl shadow-sky-950/10 backdrop-blur dark:border-white/10 dark:bg-slate-900/75 dark:shadow-sky-950/20">
      <h1 className="text-3xl font-bold text-slate-900 dark:text-white">{title}</h1>
      <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{subtitle}</p>
      <div className="mt-8">{children}</div>
    </div>
  );
}
