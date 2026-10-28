import { motion } from 'framer-motion';
import { Clock, MapPin, Utensils, Car, Bed, Star } from 'lucide-react';

const TYPE_ICONS = {
  activity: Star,
  travel: Car,
  meal: Utensils,
  accommodation: Bed,
};

const TYPE_COLORS = {
  activity: 'teal',
  travel: 'purple',
  meal: 'amber',
  accommodation: 'blue',
};

export default function ItineraryTimeline({ items }) {
  if (!items?.length) return null;

  return (
    <div>
      <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
        <Clock className="w-4 h-4 text-teal-400" />
        Day Itinerary
      </h3>
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-[18px] top-2 bottom-2 w-px bg-gradient-to-b from-teal-500/50 via-teal-500/20 to-transparent" />

        <div className="space-y-3">
          {items.map((item, i) => {
            const Icon = TYPE_ICONS[item.type] || Star;
            const color = TYPE_COLORS[item.type] || 'teal';
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -15 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.08 }}
                className="flex gap-4"
              >
                {/* Dot */}
                <div className={`w-9 h-9 rounded-full bg-${color}-500/10 border border-${color}-500/30 flex items-center justify-center flex-shrink-0 z-10`}>
                  <Icon className={`w-4 h-4 text-${color}-400`} />
                </div>
                {/* Content */}
                <div className="glass-card flex-1 p-3 pb-3">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="text-sm font-medium text-white">{item.title}</h4>
                    {item.time && (
                      <span className="text-[10px] text-slate-500 flex-shrink-0 bg-white/5 px-2 py-0.5 rounded-full">
                        {item.time}
                      </span>
                    )}
                  </div>
                  {item.description && (
                    <p className="text-xs text-slate-400 mt-1">{item.description}</p>
                  )}
                  {item.location && (
                    <p className="text-[10px] text-slate-500 mt-1.5 flex items-center gap-1">
                      <MapPin className="w-2.5 h-2.5" />
                      {item.location}
                    </p>
                  )}
                  {item.duration_minutes && (
                    <p className="text-[10px] text-slate-600 mt-1">~{item.duration_minutes} min</p>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
