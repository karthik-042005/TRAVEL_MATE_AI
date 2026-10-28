import { ExternalLink, Clock, BookOpen } from 'lucide-react';
import { motion } from 'framer-motion';

export default function SourceList({ sources }) {
  if (!sources?.length) return null;

  return (
    <div>
      <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
        <BookOpen className="w-4 h-4 text-teal-400" />
        Sources & References ({sources.length})
      </h3>
      <div className="space-y-2">
        {sources.map((src, i) => (
          <motion.a
            key={i}
            href={src.url}
            target="_blank"
            rel="noopener noreferrer"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: i * 0.04 }}
            className="flex items-start gap-2.5 p-3 rounded-xl glass-card-hover group"
          >
            <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-teal-400 flex-shrink-0 mt-0.5 transition-colors" />
            <div className="min-w-0 flex-1">
              <p className="text-xs font-medium text-slate-300 group-hover:text-white transition-colors line-clamp-1">
                {src.title}
              </p>
              {src.snippet && (
                <p className="text-[10px] text-slate-500 mt-0.5 line-clamp-2">{src.snippet}</p>
              )}
              <p className="text-[10px] text-slate-600 mt-1 truncate">{src.url}</p>
            </div>
          </motion.a>
        ))}
      </div>
    </div>
  );
}
