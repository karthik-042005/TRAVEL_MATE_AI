import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, ZoomControl, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Map, AlertCircle } from 'lucide-react';

// Fix default Leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom teal marker
const tealIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

// Recenter map when center changes
function MapController({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center) map.setView(center, zoom, { animate: true });
  }, [center, zoom, map]);
  return null;
}

export default function InteractiveMap({ destination, coordinates, attractions, route }) {
  const [mapReady, setMapReady] = useState(false);

  const center = coordinates
    ? [coordinates.lat, coordinates.lon]
    : [20.5937, 78.9629]; // India center fallback

  const zoom = coordinates ? 12 : 5;

  const routePositions = route?.geometry || [];

  return (
    <div>
      <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
        <Map className="w-4 h-4 text-teal-400" />
        Interactive Map
        {!coordinates && (
          <span className="text-[10px] text-slate-500 font-normal">
            (Add GEOAPIFY_API_KEY for precise location)
          </span>
        )}
      </h3>

      <div className="rounded-2xl overflow-hidden border border-white/10" style={{ height: '380px' }}>
        <MapContainer
          center={center}
          zoom={zoom}
          zoomControl={false}
          style={{ height: '100%', width: '100%' }}
          whenReady={() => setMapReady(true)}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <ZoomControl position="bottomright" />
          <MapController center={center} zoom={zoom} />

          {/* Destination marker */}
          {coordinates && (
            <Marker position={[coordinates.lat, coordinates.lon]} icon={tealIcon}>
              <Popup>
                <strong>{destination || 'Destination'}</strong>
              </Popup>
            </Marker>
          )}

          {/* Attraction markers */}
          {attractions?.map((attr, i) => {
            if (!attr.coordinates) return null;
            return (
              <Marker
                key={i}
                position={[attr.coordinates.lat, attr.coordinates.lon]}
              >
                <Popup>
                  <strong>{attr.name}</strong>
                  {attr.address && <><br /><small>{attr.address}</small></>}
                  {attr.category && <><br /><em>{attr.category}</em></>}
                </Popup>
              </Marker>
            );
          })}

          {/* Route polyline */}
          {routePositions.length > 0 && (
            <Polyline
              positions={routePositions}
              color="#00bcd4"
              weight={4}
              opacity={0.8}
              dashArray={undefined}
            />
          )}
        </MapContainer>
      </div>

      <p className="text-[10px] text-slate-600 mt-2">
        Map data © OpenStreetMap contributors · Tiles © OpenStreetMap
      </p>
    </div>
  );
}
