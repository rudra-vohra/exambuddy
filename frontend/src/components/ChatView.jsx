import React, { useState, useRef, useEffect } from 'react';
import { Send, BookOpen, AlertCircle, ShieldAlert, CheckCircle2, Loader2 } from 'lucide-react';

const cleanAnswerText = (text) => {
  if (!text) return '';
  return text
    .replace(/\[Source:[^\]]*\]/gi, '')
    .replace(/\(Source:[^\)]*\)/gi, '')
    .replace(/\[p\.\s*\d+\]/gi, '')
    .replace(/\s+([.,;:!?])/g, '$1')
    .replace(/  +/g, ' ')
    .trim();
};

const DEFAULT_INIT_MESSAGES = [
  {
    id: 'init-1',
    sender: 'assistant',
    text: "The ExamBuddy is active. I provide strictly grounded answers directly from your course lecture notes, slides, markdown summaries, and handwritten scans. Every fact is cited with document title and page number.",
    refusal: false,
    citations: []
  }
];

export default function ChatView({
  onSelectCitation,
  apiBase = 'http://localhost:8000',
  messages: externalMessages,
  setMessages: externalSetMessages,
  inputQuery: externalInputQuery,
  setInputQuery: externalSetInputQuery
}) {
  const [internalMessages, setInternalMessages] = useState(DEFAULT_INIT_MESSAGES);
  const [internalInputQuery, setInternalInputQuery] = useState('');

  const messages = externalMessages !== undefined ? externalMessages : internalMessages;
  const setMessages = externalSetMessages !== undefined ? externalSetMessages : setInternalMessages;
  const inputQuery = externalInputQuery !== undefined ? externalInputQuery : internalInputQuery;
  const setInputQuery = externalSetInputQuery !== undefined ? externalSetInputQuery : setInternalInputQuery;

  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const sessionIdRef = useRef('session-' + Date.now());

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = async (queryText) => {
    const q = (queryText || inputQuery).trim();
    if (!q || loading) return;

    const userMsgId = 'user-' + Date.now();
    setMessages(prev => [
      ...prev,
      { id: userMsgId, sender: 'user', text: q }
    ]);
    setInputQuery('');
    setLoading(true);

    // Prepare conversation history payload for multi-turn conversational reasoning
    const historyPayload = messages
      .filter(m => (m.sender === 'user' || m.sender === 'assistant') && m.id !== 'init-1' && !m.refusal)
      .slice(-6)
      .map(m => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text
      }));

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 90000);

    try {
      const response = await fetch(`${apiBase}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: q,
          session_id: sessionIdRef.current,
          history: historyPayload
        }),
        signal: controller.signal
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
        throw new Error(errData.detail || `HTTP Error: ${response.status}`);
      }

      const data = await response.json();
      if (data.session_id) {
        sessionIdRef.current = data.session_id;
      }
      setMessages(prev => [
        ...prev,
        {
          id: 'asst-' + Date.now(),
          sender: 'assistant',
          text: cleanAnswerText(data.answer),
          refusal: Boolean(data.refusal),
          citations: data.citations || []
        }
      ]);
    } catch (err) {
      const isTimeout = err.name === 'AbortError';
      const msg = isTimeout
        ? "Request timed out: retrieval took too long. Please verify the backend is running and try again."
        : `System error: ${err.message || "unable to contact RAG backend server."}`;
      setMessages(prev => [
        ...prev,
        {
          id: 'err-' + Date.now(),
          sender: 'assistant',
          text: msg,
          refusal: true,
          citations: []
        }
      ]);
    } finally {
      clearTimeout(timeoutId);
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-5xl mx-auto px-4 py-4 sm:py-6">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto pr-1 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.sender === 'user' ? (
              <div className="max-w-2xl bg-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 text-sm shadow-md leading-relaxed">
                {msg.text}
              </div>
            ) : (
              <div className="max-w-3xl w-full bg-slate-900/90 border border-slate-800/90 rounded-2xl rounded-tl-sm p-4 sm:p-5 shadow-lg space-y-3">
                {/* Status Header */}
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
                  <div className="flex items-center space-x-2">
                    {msg.refusal ? (
                      <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-950/60 text-rose-400 border border-rose-800/50">
                        <ShieldAlert className="w-3.5 h-3.5" />
                        <span>OUT-OF-CORPUS REFUSAL</span>
                      </span>
                    ) : (
                      <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-800/50">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>STRICT COURSE GROUNDING</span>
                      </span>
                    )}
                  </div>
                  <span className="text-[11px] font-mono text-slate-500">Gemini 3.5 Flash Lite</span>
                </div>

                {/* Answer Text */}
                <div className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">
                  {msg.sender === 'assistant' && !msg.refusal ? cleanAnswerText(msg.text) : msg.text}
                </div>

                {/* Citations Badges */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="pt-2 border-t border-slate-800/70">
                    <div className="text-xs font-medium text-slate-400 mb-1.5 font-mono">
                      Verified Page Citations (Click to inspect excerpt):
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {msg.citations.map((cit, cIdx) => (
                        <button
                          key={cIdx}
                          onClick={() => onSelectCitation(cit)}
                          className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-md text-xs font-mono bg-blue-950/50 hover:bg-blue-900/60 text-blue-300 border border-blue-800/60 hover:border-blue-700 transition-colors shadow-sm"
                        >
                          <BookOpen className="w-3 h-3 text-blue-400" />
                          <span>{cit.source}</span>
                          <span className="bg-blue-900/80 px-1.5 py-0.2 rounded text-blue-200 font-bold">
                            p.{cit.page_number}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl rounded-tl-sm p-4 flex items-center space-x-3 text-slate-400 text-sm">
              <Loader2 className="w-4 h-4 animate-spin text-blue-400" />
              <span className="font-mono text-xs">Retrieving vectors across course documents and synthesizing strictly grounded response...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="mt-4 pt-3 border-t border-slate-800/80">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
          className="relative flex items-center"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask an exam question (strictly answered with exact document page citations)..."
            disabled={loading}
            className="w-full bg-slate-900 border border-slate-800 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-xl px-4 py-3 pr-12 text-sm text-slate-100 placeholder-slate-500 transition-all outline-none"
          />
          <button
            type="submit"
            disabled={loading || !inputQuery.trim()}
            className="absolute right-2 p-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:hover:bg-blue-600 text-white transition-all shadow-md"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <p className="mt-1.5 text-[11px] text-center text-slate-500 font-mono">
          Out-of-corpus questions are strictly refused. Zero parametric hallucination policy.
        </p>
      </div>
    </div>
  );
}
