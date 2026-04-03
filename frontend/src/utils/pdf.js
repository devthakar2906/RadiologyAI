import { jsPDF } from "jspdf";

export function exportReportPdf(report) {
  const doc = new jsPDF();
  doc.setFontSize(18);
  doc.text("Radiology Report", 20, 20);
  doc.setFontSize(12);
  doc.text(`Findings`, 20, 40);
  doc.text(doc.splitTextToSize(report.report.findings || "", 170), 20, 48);
  doc.text(`Impression`, 20, 100);
  doc.text(doc.splitTextToSize(report.report.impression || "", 170), 20, 108);
  doc.text(`Recommendations`, 20, 150);
  doc.text(doc.splitTextToSize(report.report.recommendations || "", 170), 20, 158);
  doc.save(`radiology-report-${report.id}.pdf`);
}
