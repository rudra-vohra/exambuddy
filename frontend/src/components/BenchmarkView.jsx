import React, { useState, useEffect } from 'react';
import { Play, CheckCircle2, XCircle, ShieldAlert, BarChart3, Clock, Loader2, Filter, ChevronDown, ChevronUp } from 'lucide-react';

export default function BenchmarkView({ onSelectCitation, apiBase = 'http://localhost:8000' }) {
  const [evalResult, setEvalResult] = useState(null);
  const [running, setRunning] = useState(false);
  const [activeFilter, setActiveFilter] = useState('all');
  const [expandedRow, setExpandedRow] = useState(null);

  useEffect(() => {
    // Fetch latest run if available
    fetch(`${apiBase}/api/evaluate/latest`)
      .then(res => res.json())
      .then(data => {
        if (data && data.summary) {
          setEvalResult(data);
        }
      })
      .catch(err => console.error("Error loading benchmark history:", err));
  }, [apiBase]);

  const handleRunBenchmark = async (maxQuestions = null) => {
    setRunning(true);
    try {
      const url = maxQuestions
        ? `${apiBase}/api/evaluate/run?max_questions=${maxQuestions}`
        : `${apiBase}/api/evaluate/run`;
      const res = await fetch(url, { method: 'POST' });
      const data = await res.json();
      setEvalResult(data);
    } catch (err) {
      console.error("Benchmark error:", err);
    } finally {
      setRunning(false);
    }
  };

  const filteredDetails = evalResult?.details?.filter(item => {
    if (activeFilter === 'all') return true;
    return item.category === activeFilter;
  }) || [];

  return (
    <div className="max-w-6xl mx-auto px-4 py-6 sm:py-8 space-y-8">
      {/* Header & Run Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-slate-900 border border-slate-800 shadow-md">
        <div>
          <div className="flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-bold text-slate-100">Exam Evaluation Benchmark</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Automated verification against 20 target questions (10 single-source, 10 multi-source synthesis) and 10 syllabus-derived out-of-corpus refusal questions.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => handleRunBenchmark(5)}
            disabled={running}
            className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-300 text-xs font-mono font-medium transition-colors"
          >
            Quick Test (5 Qs)
          </button>
          <button
            onClick={() => handleRunBenchmark(null)}
            disabled={running}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-semibold shadow-md transition-all"
          >
            {running ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Running Evaluation...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                <span>Run 30-Question Benchmark</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Metrics Summary Cards */}
      {evalResult?.summary && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
            <span className="text-xs font-mono text-slate-400 block mb-1">Refusal Rate (Target 100%)</span>
            <div className="flex items-baseline space-x-2">
              <span className={`text-2xl font-bold font-mono ${evalResult.summary.refusal_rate === 100 ? 'text-emerald-400' : 'text-amber-400'}`}>
                {evalResult.summary.refusal_rate}%
              </span>
              <span className="text-xs text-slate-500">
                ({evalResult.summary.refusal_passed}/{evalResult.summary.refusal_questions})
              </span>
            </div>
          </div>

          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
            <span className="text-xs font-mono text-slate-400 block mb-1">Citation Accuracy</span>
            <div className="flex items-baseline space-x-2">
              <span className="text-2xl font-bold font-mono text-blue-400">
                {evalResult.summary.citation_accuracy}%
              </span>
              <span className="text-xs text-slate-500">
                ({evalResult.summary.target_passed}/{evalResult.summary.target_questions})
              </span>
            </div>
          </div>

          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
            <span className="text-xs font-mono text-slate-400 block mb-1">Overall Accuracy</span>
            <div className="flex items-baseline space-x-2">
              <span className="text-2xl font-bold font-mono text-slate-100">
                {evalResult.summary.overall_accuracy}%
              </span>
              <span className="text-xs text-slate-500">
                ({evalResult.summary.overall_passed}/{evalResult.summary.total_questions})
              </span>
            </div>
          </div>

          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
            <span className="text-xs font-mono text-slate-400 block mb-1">Benchmark Run ID</span>
            <div className="text-xs font-mono text-slate-300 truncate mt-2">
              {evalResult.run_id}
            </div>
            <span className="text-[10px] text-slate-500 font-mono block mt-1">
              {new Date(evalResult.timestamp).toLocaleString()}
            </span>
          </div>
        </div>
      )}

      {/* Filter Tabs & Test Table */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex space-x-2">
            {[
              { id: 'all', label: `All (${evalResult?.details?.length || 0})` },
              { id: 'single_source', label: 'Single-Source (10)' },
              { id: 'multi_source', label: 'Multi-Source (10)' },
              { id: 'refusal', label: 'Refusal Set (10)' },
            ].map(f => (
              <button
                key={f.id}
                onClick={() => setActiveFilter(f.id)}
                className={`text-xs px-3 py-1.5 rounded-lg border font-mono transition-colors ${
                  activeFilter === f.id
                    ? 'bg-blue-600 border-blue-500 text-white'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Results List */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden divide-y divide-slate-800">
          {filteredDetails.length === 0 ? (
            <div className="p-12 text-center text-slate-500 text-xs font-mono">
              No benchmark run executed yet. Click "Run 30-Question Benchmark" above to start.
            </div>
          ) : (
            filteredDetails.map((item) => {
              const isExpanded = expandedRow === item.id;
              return (
                <div key={item.id} className="p-4 hover:bg-slate-800/40 transition-colors">
                  <div
                    onClick={() => setExpandedRow(isExpanded ? null : item.id)}
                    className="flex items-start justify-between cursor-pointer gap-4"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="mt-0.5">
                        {item.passed ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                            PASS
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-rose-950 text-rose-400 border border-rose-800">
                            FAIL
                          </span>
                        )}
                      </div>
                      <div>
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="text-xs font-mono text-slate-400">Q{item.id}</span>
                          <span className="text-[10px] font-mono uppercase px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
                            {item.category.replace('_', ' ')}
                          </span>
                        </div>
                        <h4 className="text-sm font-medium text-slate-200 leading-snug">
                          {item.query}
                        </h4>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4 shrink-0">
                      <div className="text-right hidden sm:block font-mono text-xs">
                        {item.category === 'refusal' ? (
                          <span className="text-rose-400">Target: Refusal</span>
                        ) : (
                          <span className="text-slate-400">
                            GT: {item.ground_truth_pages.map(g => `${g.source} p.${g.page}`).join(', ')}
                          </span>
                        )}
                      </div>
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-slate-400" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-slate-400" />
                      )}
                    </div>
                  </div>

                  {/* Expanded Detail Panel */}
                  {isExpanded && (
                    <div className="mt-4 pt-4 border-t border-slate-800 space-y-3 text-xs">
                      <div>
                        <span className="font-mono text-slate-400 uppercase tracking-wider block mb-1">
                          System Predicted Answer:
                        </span>
                        <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 whitespace-pre-wrap font-mono leading-relaxed">
                          {item.predicted_answer}
                        </div>
                      </div>

                      {item.predicted_citations && item.predicted_citations.length > 0 && (
                        <div>
                          <span className="font-mono text-slate-400 uppercase tracking-wider block mb-1">
                            Retrieved & Verified Citations:
                          </span>
                          <div className="flex flex-wrap gap-2">
                            {item.predicted_citations.map((c, cIdx) => (
                              <button
                                key={cIdx}
                                onClick={() => onSelectCitation(c)}
                                className="px-2.5 py-1 rounded bg-blue-950 text-blue-300 border border-blue-900 font-mono hover:bg-blue-900 transition-colors"
                              >
                                {c.source} - Page {c.page_number}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
