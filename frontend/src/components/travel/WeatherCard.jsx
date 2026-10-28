import { motion } from 'framer-motion';
import { Cloud, Thermometer, Wind, Droplets, Eye, AlertCircle } from 'lucide-react';

const WEATHER_ICONS = {
  '01d': '☀️', '01n': '🌙', '02d': '⛅', '02n': '🌤️',
  '03d': '☁️', '03n': '☁️', '04d': '☁️', '04n': '☁️',
  '09d': '🌧️', '09n': '🌧️', '10d': '🌦️', '10n': '🌧️',
  '11d': '⛈️', '11n': '⛈️', '13d': '❄️', '13n': '❄️',
  '50d': '🌫️', '50n': '🌫️',
};

export default function WeatherCard({ weather, destination }) {
  if (!weather) return null;

  if (weather.unavailable_reason) {
    return (
      <div className="glass-card p-4 border border-amber-500/20">
        <div className="flex items-center gap-2 text-amber-400 mb-2">
          <AlertCircle className="w-4 h-4" />
          <span className="text-sm font-medium">Weather Unavailable</span>
        </div>
        <p className="text-xs text-slate-400">{weather.unavailable_reason}</p>
      </div>
    );
  }

  const emoji = WEATHER_ICONS[weather.icon] || '🌤️';
  const label = weather.is_forecast ? `Forecast · ${weather.forecast_date || ''}` : 'Current conditions';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-5 border border-white/10"
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-xs text-slate-500 mb-1">{label}</p>
          <h3 className="text-white font-semibold">{destination || 'Weather'}</h3>
        </div>
        <span className="text-4xl">{emoji}</span>
      </div>

      <div className="flex items-end gap-2 mb-4">
        <span className="text-5xl font-light text-white">
          {weather.temperature_c ?? '—'}°
        </span>
        <span className="text-slate-400 text-sm mb-2">
          {weather.condition}
        </span>
      </div>

      {weather.description && (
        <p className="text-sm text-slate-300 mb-4 capitalize">{weather.description}</p>
      )}

      <div className="grid grid-cols-3 gap-3">
        {weather.feels_like_c != null && (
          <div className="text-center">
            <Thermometer className="w-4 h-4 text-teal-400 mx-auto mb-1" />
            <p className="text-xs text-slate-400">Feels like</p>
            <p className="text-sm text-white font-medium">{weather.feels_like_c}°C</p>
          </div>
        )}
        {weather.humidity_percent != null && (
          <div className="text-center">
            <Droplets className="w-4 h-4 text-blue-400 mx-auto mb-1" />
            <p className="text-xs text-slate-400">Humidity</p>
            <p className="text-sm text-white font-medium">{weather.humidity_percent}%</p>
          </div>
        )}
        {weather.wind_speed_kmh != null && (
          <div className="text-center">
            <Wind className="w-4 h-4 text-purple-400 mx-auto mb-1" />
            <p className="text-xs text-slate-400">Wind</p>
            <p className="text-sm text-white font-medium">{weather.wind_speed_kmh} km/h</p>
          </div>
        )}
      </div>

      {weather.retrieved_at && (
        <p className="text-[10px] text-slate-600 mt-3">
          Retrieved {new Date(weather.retrieved_at).toLocaleTimeString()}
        </p>
      )}
    </motion.div>
  );
}
