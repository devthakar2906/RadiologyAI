import { CheckCircle2 } from "lucide-react";

const features = [
  "Live Dictation",
  "AI Structured Reports",
  "Fast & Accurate Transcription",
  "Template-Based Reporting",
  "No Heavy Local Processing"
];

export default function Features() {
  return (
    <section className="rounded-[2rem] border border-slate-200/70 bg-white/85 p-6 shadow-[0_20px_70px_rgba(15,23,42,0.06)] dark:border-white/10 dark:bg-gray-900/70 sm:p-8">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-[0.26em] text-slate-500 dark:text-slate-300">Features</p>
        <h2 className="mt-3 text-3xl font-bold text-slate-950 dark:text-white">
          Built for radiology teams
        </h2>
      </div>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {features.map((item) => (
          <div
            key={item}
            className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-1 dark:border-white/10 dark:bg-gray-900"
          >
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-slate-700 dark:bg-white/10 dark:text-white">
              <CheckCircle2 size={18} />
            </div>
            <p className="text-base font-semibold text-slate-900 dark:text-white">{item}</p>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
              Streamline reporting with modern AI workflows tailored to radiology.
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
