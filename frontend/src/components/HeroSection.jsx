import { ArrowRight, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

export default function HeroSection() {
  return (
    <section className="relative overflow-hidden rounded-[2rem] border border-slate-200/70 bg-gradient-to-br from-slate-50 via-white to-slate-100 px-6 py-14 shadow-[0_25px_80px_rgba(15,23,42,0.08)] dark:border-white/10 dark:from-gray-900 dark:via-gray-900 dark:to-gray-800 dark:shadow-[0_25px_80px_rgba(2,6,23,0.45)] sm:px-10 lg:px-12">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.18),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(14,165,233,0.14),transparent_34%)] dark:bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.22),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(14,116,144,0.2),transparent_34%)]" />

      <div className="relative grid gap-12 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-500 dark:text-slate-300">
            Radiology AI Platform
          </p>
          <h1 className="mt-5 max-w-3xl text-4xl font-black leading-tight text-slate-950 dark:text-white sm:text-5xl">
            AI-Powered Radiology Reporting
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">
            From dictation to structured reports in seconds.
          </p>

          <div className="mt-8 flex flex-wrap gap-4">
            <Link
              to="/report"
              className="inline-flex items-center gap-2 rounded-full bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-slate-800 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-100"
            >
              Start Reporting
              <ArrowRight size={16} />
            </Link>
            <Link
              to="/report"
              className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-900 transition hover:-translate-y-0.5 hover:border-slate-400 dark:border-white/20 dark:bg-gray-900 dark:text-white"
            >
              Try Demo
            </Link>
          </div>
        </div>

        <div className="rounded-[2rem] border border-slate-200 bg-white/90 p-6 shadow-[0_18px_60px_rgba(15,23,42,0.08)] backdrop-blur dark:border-white/10 dark:bg-gray-900/80">
          <div className="flex items-center justify-between">
            <p className="text-sm font-semibold text-slate-500 dark:text-slate-400">Structured Preview</p>
            <Sparkles className="text-slate-900 dark:text-white" size={18} />
          </div>
          <div className="mt-6 space-y-4 text-sm">
            <div>
              <p className="font-semibold text-slate-700 dark:text-slate-200">Findings</p>
              <p className="mt-1 text-slate-600 dark:text-slate-400">
                No acute intracranial hemorrhage. Ventricles are normal size.
              </p>
            </div>
            <div>
              <p className="font-semibold text-slate-700 dark:text-slate-200">Impression</p>
              <p className="mt-1 text-slate-600 dark:text-slate-400">No acute intracranial abnormality.</p>
            </div>
            <div>
              <p className="font-semibold text-slate-700 dark:text-slate-200">Recommendations</p>
              <p className="mt-1 text-slate-600 dark:text-slate-400">Clinical correlation recommended.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
