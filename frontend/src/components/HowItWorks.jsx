export default function HowItWorks() {
  const steps = [
    "Speak findings",
    "AI transcribes & refines",
    "Generate structured report"
  ];

  return (
    <section className="rounded-[2rem] border border-slate-200/70 bg-white/85 p-6 shadow-[0_20px_70px_rgba(15,23,42,0.06)] dark:border-white/10 dark:bg-gray-900/70 sm:p-8">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-[0.26em] text-slate-500 dark:text-slate-300">How it works</p>
        <h2 className="mt-3 text-3xl font-bold text-slate-950 dark:text-white">
          From speech to report in three steps
        </h2>
      </div>

      <div className="grid gap-5 md:grid-cols-3">
        {steps.map((step, index) => (
          <div
            key={step}
            className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-gray-900"
          >
            <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">Step {index + 1}</p>
            <p className="mt-3 text-lg font-semibold text-slate-900 dark:text-white">{step}</p>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
              Keep your workflow moving with instant AI feedback and structured templates.
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
