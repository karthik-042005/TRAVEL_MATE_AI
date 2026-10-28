import { motion } from 'framer-motion';
import {
  MapPin, Plus, Compass, Cloud, Shield, Wifi, WifiOff,
  Info, Zap, Navigation, Globe, ChevronRight
} from 'lucide-react';

const EXAMPLE_PROMPTS = [
  "Take me to Ooty on November 4 from Chennai by car",
  "Plan a weekend trip to Munnar from Bangalore",
  "I want to visit Coorg next Friday — best attractions and weather?",
  "Road conditions to Manali in December from Delhi",
  "3-day itinerary for Kodaikanal from Coimbatore",
];

export default function Sidebar({ onNewTrip, onPromptSelect, toolStatus, sessionId }) {
  const tools = toolStatus?.tools || {};
  const missing = toolStatus?.missing_keys || [];

  const toolItems = [
    { key: 'web_search', label: 'Web Search', icon: Globe, desc: 'Tavily API' },
    { key: 'weather', label: 'Weather', icon: Cloud, desc: 'OpenWeatherMap' },
    { key: 'maps', label: 'Maps & Routes', icon: Navigation, desc: 'Geoapify' },
    { key: 'safety_research', label: 'Safety Research', icon: Shield, desc: 'Tavily API' },
  ];

  return (
    <aside className="w-72 flex-shrink-0 bg-surface-900 border-r border-white/5 flex flex-col h-full overflow-hidden">
      {/* Logo */}
      <div className="p-6 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center shadow-lg">
            <Compass className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-white font-bold text-lg leading-none">TravelMate AI</h1>
            <p className="text-teal-400/80 text-xs mt-0.5">Explore smarter. Travel better.</p>
          </div>
        </div>
      </div>

      {/* New Trip Button */}
      <div className="p-4 border-b border-white/5">
        <button
          onClick={onNewTrip}
          className="btn-primary w-full justify-center text-sm py-2.5"
        >
          <Plus className="w-4 h-4" />
          New Trip
        </button>
      </div>

      {/* Example Prompts */}
      <div className="p-4 flex-1 overflow-y-auto">
        <p className="text-xs text-slate-500 uppercase tracking-wider mb-3 font-semibold">
          Try asking...
        </p>
        <div className="space-y-2">
          {EXAMPLE_PROMPTS.map((prompt, i) => (
            <motion.button
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => onPromptSelect(prompt)}
              className="w-full text-left glass-card-hover px-3 py-2.5 text-xs text-slate-300 hover:text-white
                         rounded-xl cursor-pointer group flex items-start gap-2"
            >
              <ChevronRight className="w-3 h-3 mt-0.5 text-teal-500/70 flex-shrink-0 group-hover:text-teal-400" />
              <span>{prompt}</span>
            </motion.button>
          ))}
        </div>

        {/* Tool Status */}
        <div className="mt-6">
          <p className="text-xs text-slate-500 uppercase tracking-wider mb-3 font-semibold">
            Integration Status
          </p>
          <div className="space-y-1.5">
            {toolItems.map(({ key, label, icon: Icon, desc }) => {
              const enabled = tools[key];
              return (
                <div
                  key={key}
                  className="flex items-center gap-2.5 px-2.5 py-2 rounded-lg"
                >
                  <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${enabled ? 'bg-teal-400' : 'bg-red-400/70'}`} />
                  <Icon className={`w-3.5 h-3.5 flex-shrink-0 ${enabled ? 'text-teal-400' : 'text-slate-500'}`} />
                  <div className="min-w-0">
                    <p className={`text-xs font-medium leading-none ${enabled ? 'text-slate-200' : 'text-slate-500'}`}>
                      {label}
                    </p>
                    <p className="text-[10px] text-slate-600 mt-0.5">{desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
          {missing.length > 0 && (
            <div className="mt-3 p-2.5 rounded-xl bg-amber-500/5 border border-amber-500/10">
              <p className="text-[10px] text-amber-400/80">
                {missing.length} key{missing.length > 1 ? 's' : ''} missing in backend/.env
              </p>
            </div>
          )}
        </div>

        {/* Session notice */}
        <div className="mt-4 p-3 rounded-xl bg-slate-500/5 border border-white/5">
          <div className="flex gap-2">
            <Info className="w-3.5 h-3.5 text-slate-500 flex-shrink-0 mt-0.5" />
            <p className="text-[10px] text-slate-500 leading-relaxed">
              Sessions are temporary. Conversation history is cleared when the backend restarts.
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-white/5">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-teal-400 rounded-full animate-pulse" />
          <span className="text-xs text-slate-500">Powered by Ollama · llama3.2:3b</span>
        </div>
      </div>
    </aside>
  );
}
