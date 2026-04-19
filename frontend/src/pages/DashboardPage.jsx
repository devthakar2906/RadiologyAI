import { Moon, Search, Sun, Trash2, FileDown, LogOut } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";
import api from "../api/client";
import SpeechReportUI from "../components/SpeechReportUI";
import { useAuth } from "../context/AuthContext";
import { exportReportPdf } from "../utils/pdf";

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [reports, setReports] = useState([]);
  const [selectedReport, setSelectedReport] = useState(null);
  const [search, setSearch] = useState("");
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "dark");
  const [loading, setLoading] = useState(true);
  const [editableReport, setEditableReport] = useState(null);
  const [doctorOptions, setDoctorOptions] = useState([]);
  const [doctorFilter, setDoctorFilter] = useState("");
  const [isSavingReport, setIsSavingReport] = useState(false);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    localStorage.setItem("theme", theme);
  }, [theme]);

  useEffect(() => {
    if (selectedReport) {
      setEditableReport({
        ...selectedReport,
        report: {
          ...selectedReport.report
        }
      });
    } else {
      setEditableReport(null);
    }
  }, [selectedReport]);

  const fetchReports = async (searchTerm = "", selectedDoctorId = doctorFilter) => {
    try {
      setLoading(true);
      const params = {};
      if (searchTerm) params.search = searchTerm;
      if (selectedDoctorId) params.doctor_id = selectedDoctorId;
      const { data } = await api.get("/reports", { params });
      setReports(data);
      if (!selectedReport && data[0]) {
        setSelectedReport(data[0]);
      }
    } catch {
      toast.error("Failed to load reports");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  useEffect(() => {
    const fetchDoctors = async () => {
      if (user?.role !== "admin") {
        return;
      }
      try {
        const { data } = await api.get("/doctors");
        setDoctorOptions(data);
      } catch {
        toast.error("Failed to load doctors");
      }
    };
    fetchDoctors();
  }, [user?.role]);

  const handleDelete = async (id) => {
    try {
      await api.delete(`/reports/${id}`);
      toast.success("Report deleted");
      const next = reports.filter((report) => report.id !== id);
      setReports(next);
      setSelectedReport(next[0] || null);
    } catch {
      toast.error("Unable to delete report");
    }
  };

  const handleSaveReport = async () => {
    if (!editableReport) {
      return;
    }
    try {
      setIsSavingReport(true);
      const { data } = await api.post(`/reports/save`, {
        report_id: editableReport.id || null,
        transcription: editableReport.transcription,
        report: editableReport.report
      });
      setEditableReport(data);
      setSelectedReport(data);
      setReports((current) => {
        const existingIndex = current.findIndex((report) => report.id === data.id);
        if (existingIndex >= 0) {
          return current.map((report) => (report.id === data.id ? data : report));
        }
        const filtered = current.filter((report) => report.id !== editableReport.id);
        return [data, ...filtered];
      });
      toast.success("Report saved");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to save report");
    } finally {
      setIsSavingReport(false);
    }
  };

  const updateReportSection = (path, nextValue) => {
    setEditableReport((current) => {
      if (!current) return current;
      const nextReport = structuredClone(current.report);
      let cursor = nextReport;
      for (let index = 0; index < path.length - 1; index += 1) {
        cursor = cursor[path[index]];
      }
      cursor[path[path.length - 1]] = nextValue;
      return { ...current, report: nextReport };
    });
  };

  const renderReportFields = (node, path = [], depth = 0) =>
    Object.entries(node)
      .filter(([section]) => !(depth === 0 && (section === "Transcription" || section === "_meta")))
      .map(([section, value]) => {
      const nextPath = [...path, section];
      const titleClass = depth === 0 ? "section-title section-title-main" : "section-title section-title-sub";
      if (value && typeof value === "object" && !Array.isArray(value)) {
        return (
          <div key={nextPath.join(".")} className="space-y-4">
            <p className={titleClass}>{section}</p>
            <div className={depth === 0 ? "report-group-main" : "report-group-sub"}>
              {renderReportFields(value, nextPath, depth + 1)}
            </div>
          </div>
        );
      }

      return (
        <div key={nextPath.join(".")} className={depth === 0 ? "report-item-main" : "report-item-sub"}>
          <p className={titleClass}>
            {depth === 0 ? section : `${section}:`}
          </p>
          <textarea
            className={depth === 0 ? "report-editor report-editor-main" : "report-editor report-editor-sub"}
            value={value ?? ""}
            onChange={(event) => updateReportSection(nextPath, event.target.value)}
          />
        </div>
      );
    });

  const getPreviewText = (report) => {
    const templateTitle = report.template_name || report.template || "";
    const studyTitle = report.study_type || "";
    if (templateTitle && studyTitle && templateTitle !== studyTitle) {
      return `${templateTitle} - ${studyTitle}`;
    }
    if (templateTitle || studyTitle) {
      return templateTitle || studyTitle;
    }
    const flatten = (node) => {
      if (node && typeof node === "object" && !Array.isArray(node)) {
        return Object.values(node).flatMap(flatten);
      }
      return [String(node || "")];
    };
    return report.report.Impression || report.report.Findings || flatten(report.report).find(Boolean) || "Untitled report";
  };

  const summaryCards = useMemo(
    () => [
      { label: "Role", value: user?.role || "doctor" },
      { label: "Reports", value: reports.length }
    ],
    [reports.length, user?.role]
  );

  return (
    <main className="dashboard-shell">
      <section className="hero-panel">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.3em] text-slate-500 dark:text-sky-300">Radiology AI Workspace</p>
            <h1 className="mt-3 text-4xl font-bold text-slate-900 dark:text-white">Hello, {user?.name || "Doctor"}.</h1>
          </div>
          <div className="flex gap-3">
            <button className="icon-button" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
              {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <button className="icon-button" onClick={logout}>
              <LogOut size={18} />
            </button>
          </div>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {summaryCards.map((card) => (
            <div key={card.label} className="stat-card">
              <p className="text-sm text-slate-400">{card.label}</p>
              <p className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{card.value}</p>
            </div>
          ))}
          <div className="stat-card">
            <p className="text-sm text-slate-400">{user?.role === "admin" ? "Doctor" : "Search"}</p>
            {user?.role === "admin" ? (
              <select
                className="input mt-2"
                value={doctorFilter}
                onChange={(e) => {
                  const nextDoctor = e.target.value;
                  setDoctorFilter(nextDoctor);
                  fetchReports(search, nextDoctor);
                }}
              >
                <option value="">All</option>
                {doctorOptions.map((doctor) => (
                  <option key={doctor.id} value={doctor.id}>
                    {doctor.name}
                  </option>
                ))}
              </select>
            ) : (
              <p className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{search || "All"}</p>
            )}
          </div>
        </div>

      </section>

      <section className="mt-8 grid gap-8 xl:grid-cols-[1.25fr_0.75fr]">
        <div className="space-y-8">
          <SpeechReportUI
            theme={theme}
            onReportReady={(report) => {
              setSelectedReport(report);
              setEditableReport({
                ...report,
                report: {
                  ...report.report
                }
              });
              fetchReports(search);
            }}
          />

          <div className="panel">
            <div className="mb-4 flex items-center gap-3">
              <Search className="text-slate-400" size={18} />
              <input
                className="input"
                placeholder="Search by report words"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              {user?.role === "admin" ? (
                <select
                  className="input max-w-64"
                  value={doctorFilter}
                  onChange={(e) => setDoctorFilter(e.target.value)}
                >
                  <option value="">All Doctors</option>
                  {doctorOptions.map((doctor) => (
                    <option key={doctor.id} value={doctor.id}>
                      {doctor.name}
                    </option>
                  ))}
                </select>
              ) : null}
              <button className="primary-button" onClick={() => fetchReports(search, doctorFilter)}>Search</button>
            </div>

            <div className="space-y-3">
              {loading ? <div className="spinner" /> : null}
              {reports.map((report) => (
                <div key={report.id} className="report-row">
                  <button className="flex-1 text-left" onClick={() => setSelectedReport(report)}>
                    <p className="font-medium text-slate-900 dark:text-white">{getPreviewText(report)}</p>
                    <p className="mt-1 text-xs text-slate-400">{new Date(report.created_at).toLocaleString()}</p>
                  </button>
                  <button className="icon-button" onClick={() => exportReportPdf(report)}>
                    <FileDown size={16} />
                  </button>
                  <button className="icon-button" onClick={() => handleDelete(report.id)}>
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        <aside className="panel sticky top-6 h-fit">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Structured Report</h2>
          {editableReport ? (
            <div className="mt-6 space-y-5">
              <div className="rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-3 dark:border-white/10 dark:bg-slate-900/70">
                <p className="text-xs uppercase tracking-[0.22em] text-slate-500 dark:text-slate-400">Template</p>
                <p className="mt-1 text-lg font-semibold text-slate-900 dark:text-white">
                  {editableReport.template_name || editableReport.template || editableReport.study_type || "Structured Radiology"}
                </p>
                <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                  {editableReport.generated_at_ist || (editableReport.created_at ? new Date(editableReport.created_at).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" }) + " IST" : "")}
                </p>
              </div>
              {renderReportFields(editableReport.report)}
              <div className="flex gap-3">
                <button className="primary-button flex-1" onClick={handleSaveReport} disabled={isSavingReport}>
                  {isSavingReport ? "Saving..." : "Save"}
                </button>
                <button className="primary-button flex-1" onClick={() => exportReportPdf(editableReport)}>
                  <FileDown size={16} />
                  Download PDF
                </button>
              </div>
            </div>
          ) : (
            <p className="mt-6 text-slate-400">Generate or select a report to review the structured output.</p>
          )}
        </aside>
      </section>
    </main>
  );
}
