import { Navigation, Clock, Route, ExternalLink, MapPin, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export default function RouteCard({ route }) {
  if (!route) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-5"
    >
      <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
        <Route className="w-4 h-4 text-teal-400" />
        Route Summary
      </h3>

      <div className="flex items-center gap-3 mb-4">
        {route.origin && (
          <div className="flex items-center gap-1.5 text-sm text-slate-300">
            <div className="w-2 h-2 rounded-full bg-green-400" />
            {route.origin}
          </div>
        )}
        {route.origin && route.destination && (
          <div className="flex-1 h-px bg-gradient-to-r from-green-400/50 to-teal-400/50 relative">
            <div className="absolute inset-0 flex items-center justify-center">
              <Navigation className="w-3 h-3 text-teal-400" />
            </div>
          </div>
        )}
        {route.destination && (
          <div className="flex items-center gap-1.5 text-sm text-slate-300">
            <MapPin className="w-3.5 h-3.5 text-teal-400" />
            {route.destination}
          </div>
        )}
      </div>

      <div className="grid grid-cols-3 gap-3 mb-4">
        {route.distance_km != null && (
          <div className="text-center glass-card py-3">
            <p className="text-lg font-semibold text-white">{route.distance_km}</p>
            <p className="text-xs text-slate-500">km</p>
          </div>
        )}
        {route.duration_minutes != null && (
          <div className="text-center glass-card py-3">
            <p className="text-lg font-semibold text-white">
              {route.duration_minutes >= 60
                ? `${Math.floor(route.duration_minutes / 60)}h ${route.duration_minutes % 60}m`
                : `${route.duration_minutes}m`}
            </p>
            <p className="text-xs text-slate-500">drive time</p>
          </div>
        )}
        {route.mode && (
          <div className="text-center glass-card py-3">
            <p className="text-lg font-semibold text-white capitalize">{route.mode}</p>
            <p className="text-xs text-slate-500">mode</p>
          </div>
        )}
      </div>

      {route.external_nav_url && (
        <a
          href={route.external_nav_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 text-xs text-teal-400 hover:text-teal-300 transition-colors"
        >
          <ExternalLink className="w-3.5 h-3.5" />
          Open in OpenStreetMap
        </a>
      )}
    </motion.div>
  );
}
