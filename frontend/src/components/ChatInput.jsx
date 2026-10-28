import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2 } from 'lucide-react';

export default function ChatInput({ onSubmit, loading, disabled }) {
  const [value, setValue] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 160) + 'px';
    }
  }, [value]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || loading) return;
    onSubmit(trimmed);
    setValue('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="glass-card p-1 flex items-end gap-2 focus-within:border-teal-500/30 transition-colors">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Where do you want to explore? (Shift+Enter for new line)"
          rows={1}
          disabled={disabled || loading}
          className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 outline-none resize-none
                     px-4 py-3 text-sm leading-relaxed max-h-40 overflow-y-auto"
        />
        <motion.button
          type="submit"
          disabled={!value.trim() || loading || disabled}
          whileTap={{ scale: 0.95 }}
          className="flex-shrink-0 w-10 h-10 mb-1 mr-1 rounded-xl bg-teal-500 hover:bg-teal-400
                     disabled:opacity-30 disabled:cursor-not-allowed
                     flex items-center justify-center transition-colors shadow-lg"
          style={{ boxShadow: value.trim() ? '0 4px 20px rgba(0,188,212,0.3)' : 'none' }}
        >
          {loading
            ? <Loader2 className="w-4 h-4 text-white animate-spin" />
            : <Send className="w-4 h-4 text-white" />
          }
        </motion.button>
      </div>
      <p className="text-[10px] text-slate-600 mt-2 text-center">
        Press Enter to send · Shift+Enter for new line · Responses may take 30–60 seconds
      </p>
    </form>
  );
}
