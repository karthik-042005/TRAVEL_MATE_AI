import { useState, useEffect, useCallback, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import { travelApi } from './api/client';
import { Menu, X } from 'lucide-react';

// uuid is not always available — simple fallback
function generateId() {
  return 'xxxx-xxxx-xxxx'.replace(/x/g, () => Math.random().toString(36)[2]);
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => generateId());
  const [toolStatus, setToolStatus] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const lastMessage = useRef(null);

  // Load tool status on mount
  useEffect(() => {
    travelApi.toolStatus()
      .then(res => setToolStatus(res.data))
      .catch(() => {}); // non-critical
  }, []);

  const handleNewTrip = useCallback(() => {
    setMessages([]);
    setSessionId(generateId());
    setSidebarOpen(false);
  }, []);

  const handleSubmit = useCallback(async (message) => {
    if (!message.trim() || loading) return;
    lastMessage.current = message;
    setSidebarOpen(false);

    // Add user message
    const userMsg = { id: generateId(), role: 'user', content: message };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      // First message = new plan; subsequent = chat continue
      const isFirstMessage = messages.length === 0;
      const res = isFirstMessage
        ? await travelApi.planTrip(message, sessionId)
        : await travelApi.chat(message, sessionId);

      const plan = res.data;

      // Update session ID if backend assigned one
      if (plan.session_id) setSessionId(plan.session_id);

      const assistantMsg = {
        id: generateId(),
        role: 'assistant',
        plan,
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: generateId(),
          role: 'assistant',
          error: err.message || 'Failed to generate travel plan. Is the backend running?',
          originalMessage: message,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [loading, messages.length, sessionId]);

  const handleRetry = useCallback((originalMessage) => {
    if (originalMessage) handleSubmit(originalMessage);
  }, [handleSubmit]);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-20 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed md:relative z-30 md:z-auto h-full transition-transform duration-300 md:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
      `}>
        <Sidebar
          onNewTrip={handleNewTrip}
          onPromptSelect={(p) => { handleSubmit(p); setSidebarOpen(false); }}
          toolStatus={toolStatus}
          sessionId={sessionId}
        />
      </div>

      {/* Main area */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {/* Mobile header */}
        <div className="md:hidden flex items-center gap-3 px-4 py-3 border-b border-white/5 bg-surface-900">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-slate-400 hover:text-white transition-colors"
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          <span className="text-white font-semibold">TravelMate AI</span>
        </div>

        <ChatWindow
          messages={messages}
          loading={loading}
          onSubmit={handleSubmit}
          onRetry={handleRetry}
          sessionId={sessionId}
        />
      </main>
    </div>
  );
}
