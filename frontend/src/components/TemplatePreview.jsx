export default function TemplatePreview() {
  return (
    <section className="rounded-[2rem] border border-slate-200/70 bg-white/85 p-6 shadow-[0_20px_70px_rgba(15,23,42,0.06)] dark:border-white/10 dark:bg-gray-900/70 sm:p-8">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-[0.26em] text-slate-500 dark:text-slate-300">Preview</p>
        <h2 className="mt-3 text-3xl font-bold text-slate-950 dark:text-white">See the reporting workspace</h2>
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-[0_18px_60px_rgba(15,23,42,0.08)] dark:border-white/10 dark:bg-gray-900">
        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-5 text-slate-600 dark:border-white/10 dark:bg-gray-950 dark:text-slate-400">
            <p className="text-sm font-semibold">Live Dictation Panel</p>
            <p className="mt-3 text-sm">
              Dictate findings and watch the transcription appear instantly. Audio refinement runs only after you stop.
            </p>
          </div>
          <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-5 text-slate-600 dark:border-white/10 dark:bg-gray-950 dark:text-slate-400">
            <p className="text-sm font-semibold">Structured Report Output</p>
            <p className="mt-3 text-sm">
              Templates align with RadReport sections so you can review and export clean PDFs.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
