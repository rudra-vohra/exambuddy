import React, { useState, useEffect } from 'react';
import { FileText, UploadCloud, CheckCircle2, Image as ImageIcon, Layers, FileCode, Presentation, RefreshCw, Loader2 } from 'lucide-react';

export default function DocumentsView({ onSelectCitation, apiBase = 'http://localhost:8000' }) {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

  useEffect(() => {
    if (!uploadStatus) return;
    const timer = setTimeout(() => {
      setUploadStatus(null);
    }, 5000);
    return () => clearTimeout(timer);
  }, [uploadStatus]);

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/documents`);
      const data = await res.json();
      setDocuments(data.documents || []);
    } catch (err) {
      console.error("Failed to load documents:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, [apiBase]);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadStatus(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${apiBase}/api/documents/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");

      setUploadStatus({
        type: "success",
        msg: `Successfully indexed ${data.source}: ${data.pages_indexed} pages, ${data.chunks_indexed} chunks, OCR pages: ${data.ocr_pages}`
      });
      fetchDocs();
    } catch (err) {
      setUploadStatus({
        type: "error",
        msg: `Upload Error: ${err.message}`
      });
    } finally {
      setUploading(false);
      if (e.target) {
        e.target.value = '';
      }
    }
  };

  const getFormatIcon = (format) => {
    switch (format) {
      case 'slides':
        return <Presentation className="w-5 h-5 text-indigo-400" />;
      case 'markdown':
        return <FileCode className="w-5 h-5 text-emerald-400" />;
      case 'handwritten_image':
        return <ImageIcon className="w-5 h-5 text-amber-400" />;
      default:
        return <FileText className="w-5 h-5 text-blue-400" />;
    }
  };

  const totalPages = documents.reduce((acc, d) => acc + (d.total_pages || 0), 0);
  const totalChunks = documents.reduce((acc, d) => acc + (d.chunks_count || 0), 0);

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 sm:py-8 space-y-8">
      {/* Overview Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-slate-900 border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-slate-100">Course Materials & Ingested Corpus</h2>
          <p className="text-xs text-slate-400 mt-1">
            Multimodal dataset powering strict vector grounding across PDFs, slides, markdown, and handwritten scans.
          </p>
        </div>
        <div className="flex items-center space-x-6 text-xs font-mono">
          <div>
            <span className="text-slate-500 block">Total Documents</span>
            <span className="text-lg font-bold text-slate-200">{documents.length}</span>
          </div>
          <div className="border-l border-slate-800 pl-6">
            <span className="text-slate-500 block">Corpus Pages</span>
            <span className="text-lg font-bold text-blue-400">{totalPages} Pages</span>
          </div>
          <div className="border-l border-slate-800 pl-6">
            <span className="text-slate-500 block">Indexed Chunks</span>
            <span className="text-lg font-bold text-emerald-400">{totalChunks} Chunks</span>
          </div>
          <button
            onClick={fetchDocs}
            disabled={loading}
            className="p-2 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* Upload Zone */}
      <div className="border-2 border-dashed border-slate-800 hover:border-slate-700 rounded-2xl p-6 sm:p-8 text-center bg-slate-950/40 transition-all">
        <UploadCloud className="w-10 h-10 text-slate-500 mx-auto mb-3" />
        <h3 className="text-sm font-semibold text-slate-200 mb-1">Ingest Additional Course Material</h3>
        <p className="text-xs text-slate-400 mb-4 max-w-md mx-auto">
          Upload PDF lecture notes, slide decks, markdown cheat sheets, or photographed handwritten notes.
        </p>
        <label className="inline-flex items-center space-x-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium cursor-pointer shadow-md transition-all">
          {uploading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Processing Multimodal OCR & Vectorizing...</span>
            </>
          ) : (
            <>
              <UploadCloud className="w-4 h-4" />
              <span>Select Document (.pdf, .md, .txt, .png, .jpg)</span>
            </>
          )}
          <input
            type="file"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
            accept=".pdf,.md,.txt,.png,.jpg,.jpeg"
          />
        </label>

        {uploadStatus && (
          <div className={`mt-4 p-3 rounded-lg text-xs font-mono max-w-xl mx-auto flex items-center justify-between gap-3 ${
            uploadStatus.type === 'success'
              ? 'bg-emerald-950/50 text-emerald-300 border border-emerald-800/60'
              : 'bg-rose-950/50 text-rose-300 border border-rose-800/60'
          }`}>
            <span className="flex-1 text-left">{uploadStatus.msg}</span>
            <button
              onClick={() => setUploadStatus(null)}
              className="text-slate-400 hover:text-slate-200 px-1.5 py-0.5 rounded text-xs transition-colors"
              title="Dismiss"
            >
              ✕
            </button>
          </div>
        )}
      </div>

      {/* Documents Grid */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider font-mono">
          Ingested Course Corpus ({documents.length} Files)
        </h3>

        {loading ? (
          <div className="py-12 text-center text-slate-500 text-xs font-mono">
            Loading document library...
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {documents.map((doc, idx) => (
              <div
                key={idx}
                className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between space-y-4 shadow-sm"
              >
                <div>
                  <div className="flex items-start justify-between mb-3">
                    <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                      {getFormatIcon(doc.format)}
                    </div>
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                      {doc.format.toUpperCase()}
                    </span>
                  </div>

                  <h4 className="text-sm font-semibold text-slate-100 break-all mb-1 font-mono">
                    {doc.source}
                  </h4>
                  <p className="text-xs text-slate-400">
                    Ingested on {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : 'Exam Session'}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs font-mono text-slate-400">
                  <div className="space-x-3">
                    <span>{doc.total_pages} Pages</span>
                    <span>{doc.chunks_count} Chunks</span>
                  </div>
                  {doc.ocr_applied ? (
                    <span className="text-amber-400 font-medium">Gemini OCR</span>
                  ) : (
                    <span className="text-slate-500">Digital Text</span>
                  )}
                </div>

                <button
                  onClick={() => onSelectCitation({ source: doc.source, page_number: 1, text_snippet: "" })}
                  className="w-full py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors"
                >
                  Inspect Page 1 Evidence
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
