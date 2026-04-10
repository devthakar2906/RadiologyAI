import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export default function CTA() {
  return (
    <section className="rounded-[2rem] border border-slate-200/70 bg-gradient-to-r from-slate-950 to-slate-700 px-6 py-12 text-white shadow-[0_24px_80px_rgba(15,23,42,0.18)] dark:border-white/10 dark:from-gray-900 dark:to-gray-800 sm:px-8">
      <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div>
          <h3 className="text-2xl font-bold">Start Now</h3>
          <p className="mt-2 text-sm text-slate-200">
            Launch the reporting workspace and generate your first structured report.
          </p>
        </div>
        <Link
          to="/report"
          className="inline-flex items-center gap-2 rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-slate-100"
        >
          Start Reporting
          <ArrowRight size={16} />
        </Link>
      </div>
    </section>
  );
}
