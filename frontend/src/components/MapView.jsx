import { MapContainer, TileLayer } from "react-leaflet";
import VectorLayer from "./VectorLayer";

export default function MapView({ activeLayers = [] }) {
  return (
    <MapContainer
      center={[20.5937, 78.9629]}
      zoom={5}
      style={{ height: "100vh", width: "100%" }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="© OpenStreetMap"
      />

      {Array.isArray(activeLayers) &&
        activeLayers.map(layer =>
          layer.type === "vector" ? (
            <VectorLayer key={layer.id} layerId={layer.id} />
          ) : null
        )}
    </MapContainer>
  );
}
