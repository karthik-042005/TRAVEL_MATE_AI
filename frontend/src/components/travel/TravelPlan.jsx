import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, Calendar, Car, Info, AlertTriangle, CheckCircle, Wrench } from 'lucide-react';
import WeatherCard from './WeatherCard';
import AttractionsList from './AttractionsList';
import ItineraryTimeline from './ItineraryTimeline';
import RouteCard from './RouteCard';
import SafetyPanel from './SafetyPanel';
import SourceList from './SourceList';
import InteractiveMap from '../map/InteractiveMap';

export default function TravelPlan({ plan }) {
  if (!plan) return null;

  const {
    destination, origin, travel_date, travel_date_interpreted,
    transport_mode, summary, weather, attractions, itinerary,
    route, safety_advisories, sources, destination_coordinates,
    missing_information, data_warnings, tools_used, tools_unavailable,
    clarification_needed, message_type,
  } = plan;

  if (message_type === 'clarification' || clarification_needed) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-5 border border-teal-500/20"
      >
        <div className="flex items-start gap-3">
          <Info className="w-5 h-5 text-teal-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-white mb-1">Need a bit more info</p>
            <p className="text-sm text-slate-300">{clarification_needed || summary}</p>
          </div>
        </div>
      </motion.div>
    );
  }

  const hasMap = destination_coordinates || attractions?.some(a => a.coordinates);
  const hasHighAlerts = safety_advisories?.some(a => a.severity === 'high');

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-4"
    >
      {/* Destination Header */}
      <div className="glass-card p-5 border border-teal-500/20">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <MapPin className="w-5 h-5 text-teal-400" />
              <h2 className="text-xl font-bold text-white">{destination || 'Your Destination'}</h2>
              {hasHighAlerts && (
                <span className="flex items-center gap-1 text-[10px] px-2 py-0.5 bg-red-500/20 text-red-400 rounded-full border border-red-500/20">
                  <AlertTriangle className="w-2.5 h-2.5" />
                  High Alert
                </span>
              )}
            </div>
            <div className="flex flex-wrap gap-3 text-xs text-slate-400">
              {travel_date && (
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5 text-teal-400/70" />
                  {travel_date_interpreted || travel_date}
                </span>
              )}
              {origin && (
                <span className="flex items-center gap-1">
                  <Car className="w-3.5 h-3.5 text-teal-400/70" />
                  From {origin}
                </span>
              )}
              {transport_mode && (
                <span className="capitalize bg-white/5 px-2 py-0.5 rounded-full">
                  {transport_mode}
                </span>
              )}
            </div>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {tools_used?.map(t => (
              <span key={t} className="text-[10px] px-2 py-0.5 bg-teal-500/10 text-teal-400/80 rounded-full border border-teal-500/20 flex items-center gap-1">
                <CheckCircle className="w-2.5 h-2.5" />
                {t}
              </span>
            ))}
          </div>
        </div>

        {summary && (
          <p className="text-sm text-slate-300 mt-4 leading-relaxed border-t border-white/5 pt-4">
            {summary}
          </p>
        )}
      </div>

      {/* Missing info warnings */}
      {missing_information?.length > 0 && (
        <div className="glass-card p-4 border border-amber-500/20">
          <p className="text-xs font-semibold text-amber-400 mb-2 flex items-center gap-1">
            <Info className="w-3.5 h-3.5" />
            Information Gaps
          </p>
          <ul className="space-y-1">
            {missing_information.map((m, i) => (
              <li key={i} className="text-xs text-slate-400 flex items-start gap-2">
                <span className="text-amber-400/50 mt-0.5">•</span>
                {m}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 2-column grid for weather + route */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {weather && <WeatherCard weather={weather} destination={destination} />}
        {route && <RouteCard route={route} />}
      </div>

      {/* Map */}
      {hasMap && (
        <div className="glass-card p-5">
          <InteractiveMap
            destination={destination}
            coordinates={destination_coordinates}
            attractions={attractions}
            route={route}
          />
        </div>
      )}

      {/* Itinerary */}
      {itinerary?.length > 0 && (
        <div className="glass-card p-5">
          <ItineraryTimeline items={itinerary} />
        </div>
      )}

      {/* Attractions */}
      {attractions?.length > 0 && (
        <div className="glass-card p-5">
          <AttractionsList attractions={attractions} />
        </div>
      )}

      {/* Safety */}
      {(safety_advisories?.length > 0 || data_warnings?.length > 0) && (
        <div className="glass-card p-5">
          <SafetyPanel advisories={safety_advisories} warnings={data_warnings} />
        </div>
      )}

      {/* Sources */}
      {sources?.length > 0 && (
        <div className="glass-card p-5">
          <SourceList sources={sources} />
        </div>
      )}

      {/* Unavailable tools */}
      {tools_unavailable?.length > 0 && (
        <div className="p-3 rounded-xl bg-slate-500/5 border border-white/5">
          <p className="text-[10px] text-slate-500 flex items-center gap-1.5">
            <Wrench className="w-3 h-3" />
            Unavailable: {tools_unavailable.join(' · ')}
          </p>
        </div>
      )}
    </motion.div>
  );
}
