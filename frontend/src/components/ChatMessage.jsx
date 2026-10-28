import { motion } from 'framer-motion';
import { User, Compass, AlertCircle, RefreshCw } from 'lucide-react';
import TravelPlan from './travel/TravelPlan';

export default function ChatMessage({ message, onRetry }) {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-start gap-3 justify-end"
      >
        <div className="max-w-xl bg-teal-600/20 border border-teal-500/20 rounded-2xl rounded-tr-sm px-4 py-3">
          <p className="text-sm text-slate-100 leading-relaxed">{message.content}</p>
        </div>
        <div className="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center flex-shrink-0 mt-1">
          <User className="w-4 h-4 text-slate-300" />
        </div>
      </motion.div>
    );
  }

  // Error state
  if (message.error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-start gap-3"
      >
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center flex-shrink-0 mt-1">
          <Compass className="w-4 h-4 text-white" />
        </div>
        <div className="glass-card border-red-500/20 p-4 max-w-2xl">
          <div className="flex items-start gap-2 mb-2">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm font-medium text-red-400">Something went wrong</p>
          </div>
          <p className="text-xs text-slate-400 mb-3">{message.error}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="flex items-center gap-2 text-xs text-teal-400 hover:text-teal-300 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Try again
            </button>
          )}
        </div>
      </motion.div>
    );
  }

  // Assistant travel plan response
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-start gap-3"
    >
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center flex-shrink-0 mt-1 shadow-lg">
        <Compass className="w-4 h-4 text-white" />
      </div>
      <div className="flex-1 min-w-0">
        <TravelPlan plan={message.plan} />
      </div>
    </motion.div>
  );
}
