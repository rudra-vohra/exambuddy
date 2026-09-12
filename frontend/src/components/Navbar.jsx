import React from 'react';
import { BookOpen, FileText, BarChart3 } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, health }) {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/20 to-indigo-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 shadow-sm shadow-blue-500/10">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <span className="font-display text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
              <span>The</span>
              <span className="bg-gradient-to-r from-blue-400 via-sky-300 to-indigo-300 bg-clip-text text-transparent">ExamBuddy</span>
            </span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 sm:space-x-2">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
              activeTab === 'chat'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Study Assistant</span>
          </button>

          <button
            onClick={() => setActiveTab('documents')}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
              activeTab === 'documents'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Course Materials</span>
          </button>

          <button
            onClick={() => setActiveTab('benchmark')}
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
              activeTab === 'benchmark'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            <span>Benchmark Evaluation</span>
          </button>
        </nav>
      </div>
    </header>
  );
}
