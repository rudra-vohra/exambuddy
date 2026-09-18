import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ChatView from './components/ChatView';
import DocumentsView from './components/DocumentsView';
import BenchmarkView from './components/BenchmarkView';
import ContextDrawer from './components/ContextDrawer';

const API_BASE = 'http://localhost:8000';

const INITIAL_MESSAGES = [
  {
    id: 'init-1',
    sender: 'assistant',
    text: "The ExamBuddy is active. I provide strictly grounded answers directly from your course lecture notes, slides, markdown summaries, and handwritten scans. Every fact is cited with document title and page number.",
    refusal: false,
    citations: []
  }
];

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [selectedCitation, setSelectedCitation] = useState(null);
  const [health, setHealth] = useState(null);
  const [chatMessages, setChatMessages] = useState(INITIAL_MESSAGES);
  const [chatInput, setChatInput] = useState('');

  useEffect(() => {
    const checkHealth = () => {
      fetch(`${API_BASE}/api/health`)
        .then(res => res.json())
        .then(data => setHealth(data))
        .catch(err => console.error("Health check error:", err));
    };

    checkHealth();
    const timer = setInterval(checkHealth, 15000);
    return () => clearInterval(timer);
  }, []);

  const handleAskAboutDocument = (doc) => {
    const source = (doc?.source || '').trim();
    const ext = source.split('.').pop()?.toLowerCase();
    const format = (doc?.format || '').toLowerCase();

    let question = `What topics are covered in this document ${source}?`;
    if (format === 'pdf' || ext === 'pdf') {
      question = `What topics are covered in this pdf ${source}?`;
    } else if (format === 'slides' || ext === 'ppt' || ext === 'pptx') {
      question = `What topics are covered in these slides ${source}?`;
    } else if (
      format === 'handwritten_image' ||
      format === 'image' ||
      ['png', 'jpg', 'jpeg', 'webp'].includes(ext)
    ) {
      question = `What topics are covered in these notes ${source}?`;
    }

    setChatInput(question);
    setActiveTab('chat');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} health={health} />

      <main className="flex-1">
        <div className={activeTab === 'chat' ? 'block' : 'hidden'}>
          <ChatView
            messages={chatMessages}
            setMessages={setChatMessages}
            inputQuery={chatInput}
            setInputQuery={setChatInput}
            onSelectCitation={setSelectedCitation}
            apiBase={API_BASE}
          />
        </div>
        <div className={activeTab === 'documents' ? 'block' : 'hidden'}>
          <DocumentsView
            onSelectCitation={setSelectedCitation}
            onAskAboutDocument={handleAskAboutDocument}
            apiBase={API_BASE}
          />
        </div>
        <div className={activeTab === 'benchmark' ? 'block' : 'hidden'}>
          <BenchmarkView onSelectCitation={setSelectedCitation} apiBase={API_BASE} />
        </div>
      </main>

      <ContextDrawer
        citation={selectedCitation}
        onClose={() => setSelectedCitation(null)}
        apiBase={API_BASE}
      />
    </div>
  );
}
