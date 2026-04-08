import { jsPDF } from "jspdf";

function isMeaningfulNode(node) {
  if (node && typeof node === "object" && !Array.isArray(node)) {
    return Object.values(node).some(isMeaningfulNode);
  }
  const value = String(node || "").trim();
  return value !== "" && value.toLowerCase() !== "not mentioned";
}

function ensurePage(doc, y, needed = 16) {
  if (y + needed <= 280) {
    return y;
  }
  doc.addPage();
  return 20;
}

function renderEntries(doc, node, y, depth = 0) {
  Object.entries(node || {}).forEach(([section, value]) => {
    if (!isMeaningfulNode(value)) {
      return;
    }

    y = ensurePage(doc, y, depth === 0 ? 18 : 14);

    if (depth === 0) {
      doc.setFont("helvetica", "bold");
      doc.setFontSize(15);
      doc.text(section, 20, y);
      y += 9;
    } else {
      doc.setFont("helvetica", "bold");
      doc.setFontSize(11);
      doc.text(`• ${section}:`, 28, y);
      y += 7;
    }

    if (value && typeof value === "object" && !Array.isArray(value)) {
      y = renderEntries(doc, value, y, depth + 1);
    } else {
      y = ensurePage(doc, y, 14);
      doc.setFont("helvetica", "normal");
      doc.setFontSize(depth === 0 ? 11 : 10.5);
      const textX = depth === 0 ? 24 : 36;
      const lines = doc.splitTextToSize(String(value || "Not mentioned"), 165 - depth * 8);
      doc.text(lines, textX, y);
      y += lines.length * 6 + 6;
    }
  });

  return y;
}

export function exportReportPdf(report) {
  const doc = new jsPDF();
  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.text("Radiology Report", 20, 20);

  let y = 34;
  y = renderEntries(doc, report.report || {}, y, 0);

  if (report.transcription && isMeaningfulNode(report.transcription)) {
    y = ensurePage(doc, y, 18);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(15);
    doc.text("Transcription", 20, y);
    y += 9;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(11);
    const transcriptionLines = doc.splitTextToSize(String(report.transcription), 170);
    y = ensurePage(doc, y, transcriptionLines.length * 6 + 10);
    doc.text(transcriptionLines, 24, y);
  }

  doc.save(`radiology-report-${report.id}.pdf`);
}
