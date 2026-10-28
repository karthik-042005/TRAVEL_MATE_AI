import { motion } from 'framer-motion';
import { MapPin, Star, Clock, ExternalLink, Tag } from 'lucide-react';

const CATEGORY_COLORS = {
  'tourism': 'teal',
  'leisure': 'purple',
  'natural': 'green',
  'historic': 'amber',
  'entertainment': 'pink',
};

function getCategoryColor(cat) {
  if (!cat) return 'slate';
  for (const [key, color] of Object.entries(CATEGORY_COLORS)) {
    if (cat.includes(key)) return color;
  }
  return 'slate';
}

function AttractionChip({ label }) {
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-400 text-[10px] border border-teal-500/20">
      <Tag className="w-2.5 h-2.5" />
      {label.split('.').pop()}
    </span>
  );
}

export default function AttractionsList({ attractions }) {
  if (!attractions?.length) return null;

  return (
    <div>
      <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
        <MapPin className="w-4 h-4 text-teal-400" />
        Attractions & Places ({attractions.length})
      </h3>
      <div className="grid gap-2">
        {attractions.map((place, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.05 }}
            className="glass-card-hover p-3 flex items-start gap-3"
          >
            <div className="w-8 h-8 rounded-lg bg-teal-500/10 flex items-center justify-center flex-shrink-0">
              <MapPin className="w-4 h-4 text-teal-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{place.name}</p>
              {place.address && (
                <p className="text-xs text-slate-500 truncate mt-0.5">{place.address}</p>
              )}
              <div className="flex flex-wrap gap-1 mt-1.5">
                {place.category && <AttractionChip label={place.category} />}
                {place.opening_hours && (
                  <span className="inline-flex items-center gap-1 text-[10px] text-slate-500">
                    <Clock className="w-2.5 h-2.5" />
                    {place.opening_hours}
                  </span>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
