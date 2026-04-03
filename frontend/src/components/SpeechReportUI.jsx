import { Mic, MicOff, Sparkles, Upload } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import toast from "react-hot-toast";
import ReactQuill from "react-quill-new";
import "quill/dist/quill.snow.css";
import api from "../api/client";

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

function htmlToPlainText(value) {
  const container = document.createElement("div");
  container.innerHTML = value || "";
  return (container.textContent || container.innerText || "").replace(/\s+/g, " ").trim();
}

export default function SpeechReportUI({ onReportReady }) {
  const [transcript, setTranscript] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [audioFile, setAudioFile] = useState(null);
  const [jobState, setJobState] = useState(null);
  const [isRefining, setIsRefining] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const recognitionRef = useRef(null);
  const finalTranscriptRef = useRef("");
  const mediaRecorderRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    if (!SpeechRecognition) {
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";
    recognition.onresult = (event) => {
      let interim = "";
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const current = event.results[index][0].transcript.trim();
        if (event.results[index].isFinal) {
          finalTranscriptRef.current = `${finalTranscriptRef.current} ${current}`.trim();
        } else {
          interim = `${interim} ${current}`.trim();
        }
      }
      setTranscript(`${finalTranscriptRef.current} ${interim}`.trim());
    };
    recognition.onend = () => setIsRecording(false);
    recognitionRef.current = recognition;
  }, []);

  const startMic = async () => {
    if (!recognitionRef.current) {
      toast.error("Web Speech API is not supported in this browser.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
      audioChunksRef.current = [];

      const mimeType = MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : MediaRecorder.isTypeSupported("audio/mp4")
          ? "audio/mp4"
          : "";
      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      recorder.onstop = () => {
        const blobType = recorder.mimeType || "audio/webm";
        const extension = blobType.includes("mp4") ? "mp4" : "webm";
        const blob = new Blob(audioChunksRef.current, { type: blobType });
        if (blob.size > 0) {
          const recordedFile = new File([blob], `radiology-recording.${extension}`, { type: blobType });
          setAudioFile(recordedFile);
          toast.success("Recording ready for report generation");
          refineAudioTranscript(recordedFile);
        }
        mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
        mediaStreamRef.current = null;
      };
      mediaRecorderRef.current = recorder;
      finalTranscriptRef.current = "";
      setTranscript("");
      recorder.start();
    } catch {
      toast.error("Microphone access was denied.");
      return;
    }
    finalTranscriptRef.current = "";
    setTranscript("");
    recognitionRef.current.start();
    setIsRecording(true);
  };

  const stopMic = () => {
    recognitionRef.current?.stop();
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  };

  const refineAudioTranscript = async (recordedFile) => {
    const formData = new FormData();
    formData.append("file", recordedFile);
    try {
      setIsRefining(true);
      const { data } = await api.post("/transcribe-audio", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      if (data.transcription) {
        finalTranscriptRef.current = data.transcription;
        setTranscript(data.transcription);
        toast.success("Transcript refined from full audio");
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to refine transcript");
    } finally {
      setIsRefining(false);
    }
  };

  const pollStatus = async (jobId) => {
    const interval = setInterval(async () => {
      try {
        const { data } = await api.get(`/status/${jobId}`);
        setJobState(data.status);
        if (data.status === "completed" && data.result) {
          clearInterval(interval);
          onReportReady(data.result);
          toast.success("Report generated");
        }
        if (data.status === "failed") {
          clearInterval(interval);
          toast.error(data.error || "Report generation failed");
        }
      } catch (error) {
        clearInterval(interval);
        toast.error(error.response?.data?.detail || "Unable to fetch job status");
      }
    }, 2500);
  };

  const handleGenerate = async () => {
    const formData = new FormData();
    const cleanedTranscript = htmlToPlainText(transcript);
    if (!audioFile && !cleanedTranscript) {
      toast.error("Please record, upload, or type findings first.");
      return;
    }
    // Prefer the edited textbox content when present so report generation
    // isn't blocked by microphone/audio format issues.
    if (cleanedTranscript) {
      formData.append("transcription_text", cleanedTranscript);
    } else if (audioFile) {
      formData.append("file", audioFile);
    }
    try {
      setIsGenerating(true);
      setJobState("processing");
      const { data } = await api.post("/process-audio", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      if (data.cached && data.data) {
        onReportReady(data.data);
        setJobState("completed");
        toast.success("Loaded cached report");
        return;
      }
      if (data.status === "completed" && data.data) {
        onReportReady(data.data);
        setJobState("completed");
        toast.success("Report generated");
        return;
      }
      setJobState(data.status);
      pollStatus(data.job_id);
    } catch (error) {
      setJobState("failed");
      toast.error(error.response?.data?.detail || "Failed to start processing");
    } finally {
      setIsGenerating(false);
    }
  };

  const recordingGlow = useMemo(
    () => (isRecording ? "shadow-[0_0_50px_rgba(34,197,94,0.45)]" : "shadow-[0_0_40px_rgba(14,165,233,0.18)]"),
    [isRecording]
  );

  return (
    <div className={`rounded-[2rem] border border-white/10 bg-slate-950/70 p-6 transition-all ${recordingGlow}`}>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">SpeechReportUI</h2>
          <p className="mt-1 text-sm text-slate-400">Capture findings, edit the transcript, and send audio for AI reporting.</p>
        </div>
        <div className={`h-4 w-4 rounded-full ${isRecording ? "animate-pulse bg-emerald-400" : "bg-slate-600"}`} />
      </div>

      <div className="mb-4 flex flex-wrap gap-3">
        <button onClick={startMic} className="inline-flex items-center gap-2 rounded-full bg-emerald-500 px-4 py-2 font-medium text-white transition hover:bg-emerald-400">
          <Mic size={18} />
          Start Mic
        </button>
        <button onClick={stopMic} className="inline-flex items-center gap-2 rounded-full bg-rose-500 px-4 py-2 font-medium text-white transition hover:bg-rose-400">
          <MicOff size={18} />
          Stop Mic
        </button>
        <label className="inline-flex cursor-pointer items-center gap-2 rounded-full bg-slate-800 px-4 py-2 font-medium text-slate-100 transition hover:bg-slate-700">
          <Upload size={18} />
          Upload Audio
          <input type="file" accept="audio/*" className="hidden" onChange={(event) => setAudioFile(event.target.files?.[0] || null)} />
        </label>
        <button onClick={handleGenerate} className="inline-flex items-center gap-2 rounded-full bg-sky-500 px-4 py-2 font-medium text-white transition hover:bg-sky-400">
          <Sparkles size={18} />
          {isGenerating ? "Generating..." : "Generate Report"}
        </button>
      </div>

      <div className="mb-4 min-h-10 text-sm text-slate-400">
        {audioFile ? `Selected file: ${audioFile.name}` : "Upload a radiology dictation audio file to start backend processing."}
        {isRefining ? " Refining full-audio transcription..." : ""}
        {jobState ? ` Current job state: ${jobState}.` : ""}
      </div>

      <ReactQuill theme="snow" value={transcript} onChange={setTranscript} className="quill-card" />
    </div>
  );
}
