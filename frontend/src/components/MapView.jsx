import { MapContainer, TileLayer } from "react-leaflet";
import VectorLayer from "./VectorLayer";
import MapStatusBar from "./MapStatusBar";

export default function MapView({ activeLayers = [], projectCRS }) {
  return (
    <div style={{ position: "relative", height: "100vh", width: "100%" }}>
      {/* Leaflet Map */}
      <MapContainer
        center={[20.5937, 78.9629]}
        zoom={5}
        style={{ height: "100%", width: "100%", zIndex: 1 }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {Array.isArray(activeLayers) &&
          activeLayers.map(layer =>
            layer.type === "vector" ? (
              <VectorLayer
                key={layer.id}
                layerId={layer.id}
                projectCRS={projectCRS}
              />
            ) : null
          )}

        <MapStatusBar />
      </MapContainer>

      {/* 🔜 Potree will mount here later (no Leaflet changes) */}
      <div
        id="potree-container"
        style={{
          position: "absolute",
          inset: 0,
          zIndex: 2,
          pointerEvents: "none",
        }}
      />
    </div>
  );
}
