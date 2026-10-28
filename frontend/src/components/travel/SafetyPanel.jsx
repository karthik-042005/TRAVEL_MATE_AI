import { motion, AnimatePresence } from 'framer-motion';
import { Shield, AlertTriangle, AlertCircle, Info, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

const SEVERITY_CONFIG = {
  high: { icon: AlertTriangle, color: 'red', label: 'High Alert', bg: 'bg-red-500/10 border-red-500/20' },
  medium: { icon: AlertCircle, color: 'amber', label: 'Warning', bg: 'bg-amber-500/10 border-amber-500/20' },
  low: { icon: Info, color: 'green', label: 'Advisory', bg: 'bg-green-500/10 border-green-500/20' },
  unknown: { icon: Info, color: 'slate', label: 'Note', bg: 'bg-slate-500/10 border-slate-500/20' },
};

const TYPE_LABELS = {
  road_closure: '🚧 Road Closure',
  landslide: '⛰️ Landslide',
  weather_warning: '🌧️ Weather Warning',
  general: '📋 Advisory',
};

function AdvisoryItem({ advisory, index }) {
  const [expanded, setExpanded] = useState(false);
  const cfg = SEVERITY_CONFIG[advisory.severity] || SEVERITY_CONFIG.unknown;
  const Icon = cfg.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className={`rounded-xl border p-3 ${cfg.bg}`}
    >
      <div className="flex items-start gap-2">
        <Icon className={`w-4 h-4 text-${cfg.color}-400 flex-shrink-0 mt-0.5`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded bg-${cfg.color}-500/20 text-${cfg.color}-300`}>
              {cfg.label}
            </span>
            <span className="text-[10px] text-slate-500">
              {TYPE_LABELS[advisory.type] || advisory.type}
            </span>
          </div>
          <p className={`text-xs mt-1.5 text-${cfg.color}-200 leading-relaxed ${!expanded && 'line-clamp-2'}`}>
            {advisory.summary}
          </p>
          {advisory.summary?.length > 100 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className={`text-[10px] text-${cfg.color}-400/60 hover:text-${cfg.color}-400 mt-1 flex items-center gap-0.5`}
            >
              {expanded ? <><ChevronUp className="w-3 h-3" /> Less</> : <><ChevronDown className="w-3 h-3" /> More</>}
            </button>
          )}
          {advisory.source_url && (
            <a
              href={advisory.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-[10px] text-slate-500 hover:text-teal-400 mt-1.5 transition-colors"
            >
              <ExternalLink className="w-2.5 h-2.5" />
              {advisory.source_title || 'Source'}
            </a>
          )}
          {!advisory.verified && (
            <p className="text-[10px] text-slate-600 mt-1">⚠ Unverified — check official sources before travel</p>
          )}
        </div>
      </div>
    </motion.div>
  );
}

export default function SafetyPanel({ advisories, warnings }) {
  const hasAdvisories = advisories?.length > 0;
  const hasWarnings = warnings?.length > 0;

  if (!hasAdvisories && !hasWarnings) return null;

  const highCount = advisories?.filter(a => a.severity === 'high').length || 0;

  return (
    <div>
      <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
        <Shield className="w-4 h-4 text-teal-400" />
        Safety & Advisories
        {highCount > 0 && (
          <span className="text-[10px] px-2 py-0.5 bg-red-500/20 text-red-400 rounded-full">
            {highCount} high alert{highCount > 1 ? 's' : ''}
          </span>
        )}
      </h3>

      {hasAdvisories && (
        <div className="space-y-2 mb-3">
          {advisories.map((adv, i) => (
            <AdvisoryItem key={i} advisory={adv} index={i} />
          ))}
        </div>
      )}

      {hasWarnings && (
        <div className="space-y-1.5">
          {warnings.map((w, i) => (
            <div key={i} className="flex items-start gap-2 px-3 py-2 rounded-lg bg-slate-500/5 border border-white/5">
              <Info className="w-3.5 h-3.5 text-slate-500 flex-shrink-0 mt-0.5" />
              <p className="text-xs text-slate-400">{w}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
