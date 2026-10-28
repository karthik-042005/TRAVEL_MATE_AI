import { motion } from 'framer-motion';
import { Compass, MapPin, Cloud, Shield, Navigation, ChevronRight } from 'lucide-react';

const FEATURES = [
  { icon: MapPin, label: 'Places & Attractions', desc: 'Discover top spots' },
  { icon: Cloud, label: 'Weather Forecast', desc: 'Real-time conditions' },
  { icon: Shield, label: 'Safety Advisories', desc: 'Road & landslide alerts' },
  { icon: Navigation, label: 'Route Planning', desc: 'Distance & duration' },
];

const EXAMPLE_TRIPS = [
  { emoji: '🏔️', text: 'Take me to Ooty on November 4 from Chennai' },
  { emoji: '🌿', text: 'Plan a weekend trip to Munnar from Bangalore' },
  { emoji: '❄️', text: 'Road conditions to Manali in December from Delhi' },
  { emoji: '🏖️', text: 'Best beaches in Goa for next weekend' },
];

export default function WelcomeScreen({ onPromptSelect }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-full py-12 px-4">
      {/* Hero */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12"
      >
        <div className="w-20 h-20 mx-auto mb-6 rounded-3xl bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center shadow-2xl"
          style={{ boxShadow: '0 0 40px rgba(0,188,212,0.3)' }}>
          <Compass className="w-10 h-10 text-white" />
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-3">
          Where do you want to{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-400 to-cyan-400">
            explore?
          </span>
        </h1>
        <p className="text-slate-400 text-lg max-w-xl">
          Describe your trip in natural language. TravelMate AI researches the web,
          checks the weather, calculates routes, and keeps you safe.
        </p>
      </motion.div>

      {/* Features */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-3 w-full max-w-3xl mb-10"
      >
        {FEATURES.map(({ icon: Icon, label, desc }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.08 }}
            className="glass-card p-4 text-center"
          >
            <div className="w-10 h-10 mx-auto mb-2 rounded-xl bg-teal-500/10 flex items-center justify-center">
              <Icon className="w-5 h-5 text-teal-400" />
            </div>
            <p className="text-xs font-medium text-white">{label}</p>
            <p className="text-[10px] text-slate-500 mt-0.5">{desc}</p>
          </motion.div>
        ))}
      </motion.div>

      {/* Example prompts */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="w-full max-w-2xl"
      >
        <p className="text-xs text-slate-500 text-center mb-4 uppercase tracking-wider font-semibold">
          Try one of these
        </p>
        <div className="grid gap-2">
          {EXAMPLE_TRIPS.map((trip, i) => (
            <motion.button
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 + i * 0.08 }}
              onClick={() => onPromptSelect(trip.text)}
              className="glass-card-hover w-full text-left flex items-center gap-3 px-4 py-3 group"
            >
              <span className="text-xl flex-shrink-0">{trip.emoji}</span>
              <span className="text-sm text-slate-300 group-hover:text-white transition-colors flex-1">
                {trip.text}
              </span>
              <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-teal-400 transition-colors flex-shrink-0" />
            </motion.button>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
