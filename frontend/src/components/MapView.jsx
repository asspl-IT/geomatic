import { MapContainer, TileLayer } from "react-leaflet";
import LayerRenderer from "./LayerRenderer";

export default function MapView({ project }) {
  return (
    <MapContainer
      center={[20.5937, 78.9629]}
      zoom={5}
      style={{ height: "80vh", width: "100%" }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {project?.layers?.map((layer, idx) => (
        <LayerRenderer key={idx} layer={layer} />
      ))}
    </MapContainer>
  );
}
