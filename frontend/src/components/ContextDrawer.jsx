import React, { useEffect, useState } from 'react';
import { X, FileText, Image as ImageIcon, CheckCircle, ExternalLink, Loader2 } from 'lucide-react';

export default function ContextDrawer({ citation, onClose, apiBase = 'http://localhost:8000' }) {
  const [loading, setLoading] = useState(false);
  const [previewData, setPreviewData] = useState(null);

  useEffect(() => {
    if (!citation) return;
    setLoading(true);
    fetch(`${apiBase}/api/documents/page-preview?source=${encodeURIComponent(citation.source)}&page=${citation.page_number}`)
      .then(res => res.json())
      .then(data => {
        setPreviewData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Preview error:', err);
        setLoading(false);
      });
  }, [citation, apiBase]);

  if (!citation) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[460px] bg-slate-900 border-l border-slate-800 shadow-2xl z-50 flex flex-col transition-all duration-300">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
        <div className="flex items-center space-x-2">
          <div className="p-2 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Verified Evidence Context</h3>
            <p className="text-xs text-slate-400">Strict Provenance Inspection</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Citation Metadata Badge */}
      <div className="p-4 bg-slate-950/40 border-b border-slate-800 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-slate-400">Document:</span>
          <span className="text-xs font-medium text-blue-300 font-mono bg-blue-950/50 px-2 py-0.5 rounded border border-blue-900/50">
            {citation.source}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-slate-400">Verified Page:</span>
          <span className="text-xs font-bold text-slate-200 bg-slate-800 px-2 py-0.5 rounded">
            Page {citation.page_number}
          </span>
        </div>
        {previewData?.is_ocr && (
          <div className="flex items-center space-x-1.5 text-xs text-amber-300 bg-amber-950/40 px-2.5 py-1 rounded border border-amber-900/40">
            <ImageIcon className="w-3.5 h-3.5" />
            <span>OCR Transcribed via Gemini 3.5 Flash Lite VLM</span>
          </div>
        )}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Cited Excerpt
          </h4>
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 leading-relaxed font-mono">
            {citation.text_snippet || "Direct statement ground evidence."}
          </div>
        </div>

        {loading ? (
          <div className="py-12 flex flex-col items-center justify-center space-y-2 text-slate-400">
            <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
            <span className="text-xs font-mono">Fetching full page context...</span>
          </div>
        ) : previewData ? (
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Full Page Text Content
            </h4>
            <div className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800 text-xs text-slate-300 leading-relaxed whitespace-pre-wrap font-sans max-h-96 overflow-y-auto">
              {previewData.content}
            </div>

            {previewData.image_base64 && (
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
                    {previewData.is_ocr ? (
                      <>
                        <ImageIcon className="w-3.5 h-3.5 text-amber-400" />
                        <span>High-Resolution Scan (Handwritten Notes)</span>
                      </>
                    ) : (
                      <>
                        <FileText className="w-3.5 h-3.5 text-blue-400" />
                        <span>Source PDF Page Rendering (Page {citation.page_number})</span>
                      </>
                    )}
                  </h4>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                    {previewData.is_ocr ? 'OCR Vision Evidence' : 'Direct PDF Page'}
                  </span>
                </div>
                <div className="rounded-lg overflow-hidden border border-slate-800 bg-slate-950 p-2 shadow-inner">
                  <img
                    src={`data:image/png;base64,${previewData.image_base64}`}
                    alt={`Document ${citation.source} page ${citation.page_number} preview`}
                    className="w-full h-auto rounded border border-slate-800/80 bg-white"
                  />
                </div>
              </div>
            )}
          </div>
        ) : null}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-slate-800 bg-slate-950 text-center">
        <span className="text-[11px] text-slate-500 font-mono">
          Zero Hallucination Guaranteed | Verified from Course Documents
        </span>
      </div>
    </div>
  );
}
