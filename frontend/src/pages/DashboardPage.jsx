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
  const [theme, setTheme] = useState(localStorage.getItem("theme") || "dark");
  const [loading, setLoading] = useState(true);
  const [editableReport, setEditableReport] = useState(null);

  useEffect(() => {
    document.documentElement.classList.toggle("light", theme === "light");
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

  const fetchReports = async (searchTerm = "") => {
    try {
      setLoading(true);
      const { data } = await api.get("/reports", { params: searchTerm ? { search: searchTerm } : {} });
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

  const summaryCards = useMemo(
    () => [
      { label: "Role", value: user?.role || "doctor" },
      { label: "Reports", value: reports.length },
      { label: "Search", value: search || "All" }
    ],
    [reports.length, search, user?.role]
  );

  return (
    <main className="dashboard-shell">
      <section className="hero-panel">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.3em] text-sky-300">Radiology AI Workspace</p>
            <h1 className="mt-3 text-4xl font-bold text-white">Voice dictation to structured report, locally powered.</h1>
            <p className="mt-3 max-w-2xl text-slate-300">Upload audio, monitor asynchronous processing, review encrypted reports, and export clean PDFs for delivery.</p>
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
              <p className="mt-2 text-2xl font-bold text-white">{card.value}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-8 grid gap-8 xl:grid-cols-[1.25fr_0.75fr]">
        <div className="space-y-8">
          <SpeechReportUI
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
                placeholder="Search by audio hash"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
              <button className="primary-button" onClick={() => fetchReports(search)}>Search</button>
            </div>

            <div className="space-y-3">
              {loading ? <div className="spinner" /> : null}
              {reports.map((report) => (
                <div key={report.id} className="report-row">
                  <button className="flex-1 text-left" onClick={() => setSelectedReport(report)}>
                    <p className="font-medium text-white">{report.report.impression}</p>
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
          <h2 className="text-2xl font-bold text-white">Structured Report</h2>
          {editableReport ? (
            <div className="mt-6 space-y-5">
              <div>
                <p className="section-title">Findings</p>
                <textarea
                  className="report-editor"
                  value={editableReport.report.findings}
                  onChange={(event) =>
                    setEditableReport({
                      ...editableReport,
                      report: { ...editableReport.report, findings: event.target.value }
                    })
                  }
                />
              </div>
              <div>
                <p className="section-title">Impression</p>
                <textarea
                  className="report-editor"
                  value={editableReport.report.impression}
                  onChange={(event) =>
                    setEditableReport({
                      ...editableReport,
                      report: { ...editableReport.report, impression: event.target.value }
                    })
                  }
                />
              </div>
              <div>
                <p className="section-title">Recommendations</p>
                <textarea
                  className="report-editor"
                  value={editableReport.report.recommendations}
                  onChange={(event) =>
                    setEditableReport({
                      ...editableReport,
                      report: { ...editableReport.report, recommendations: event.target.value }
                    })
                  }
                />
              </div>
              <div>
                <p className="section-title">Transcription</p>
                <textarea
                  className="report-editor report-editor-transcription"
                  value={editableReport.transcription}
                  onChange={(event) =>
                    setEditableReport({
                      ...editableReport,
                      transcription: event.target.value
                    })
                  }
                />
              </div>
              <button className="primary-button w-full" onClick={() => exportReportPdf(editableReport)}>
                <FileDown size={16} />
                Download PDF
              </button>
            </div>
          ) : (
            <p className="mt-6 text-slate-400">Generate or select a report to review the structured output.</p>
          )}
        </aside>
      </section>
    </main>
  );
}
