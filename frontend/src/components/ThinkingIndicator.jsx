import { motion } from 'framer-motion';

export default function ThinkingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-start gap-3 max-w-2xl"
    >
      {/* Avatar */}
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center text-white text-sm font-bold flex-shrink-0 mt-1 shadow-lg">
        T
      </div>
      {/* Bubble */}
      <div className="glass-card px-5 py-4">
        <div className="flex items-center gap-3">
          <div className="flex gap-1.5">
            <div className="thinking-dot w-2 h-2 bg-teal-400 rounded-full" />
            <div className="thinking-dot w-2 h-2 bg-teal-400 rounded-full" />
            <div className="thinking-dot w-2 h-2 bg-teal-400 rounded-full" />
          </div>
          <span className="text-sm text-slate-400 animate-pulse">Planning your trip...</span>
        </div>
        <div className="mt-3 space-y-1.5">
          {[
            'Parsing your travel request',
            'Searching for attractions & routes',
            'Checking weather & safety advisories',
          ].map((step, i) => (
            <motion.div
              key={step}
              initial={{ opacity: 0, x: -5 }}
              animate={{ opacity: [0, 1, 0.5] }}
              transition={{ delay: i * 0.8, duration: 1.5, repeat: Infinity }}
              className="flex items-center gap-2 text-xs text-slate-500"
            >
              <div className="w-1 h-1 bg-teal-500/60 rounded-full" />
              {step}
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
