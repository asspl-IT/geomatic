import { useEffect, useState } from "react";
import { useMap } from "react-leaflet";
import { toDMS } from "../utils/coordUtils";
import { lonLatToUTM } from "../utils/projections"; // ✅ NEW

export default function MapStatusBar() {
  const map = useMap();
  const [latlng, setLatLng] = useState(null);
  const [scale, setScale] = useState("1:—");

  useEffect(() => {
    const updateScale = () => {
      const zoom = map.getZoom();
      const dpi = 96;
      const metersPerPixel =
        40075016.686 / Math.pow(2, zoom + 8);
      const scaleValue = Math.round(
        (metersPerPixel * dpi) / 0.0254
      );
      setScale(`1:${scaleValue.toLocaleString()}`);
    };

    const onMove = (e) => {
      setLatLng(e.latlng);
    };

    map.on("mousemove", onMove);
    map.on("zoomend", updateScale);

    updateScale();

    return () => {
      map.off("mousemove", onMove);
      map.off("zoomend", updateScale);
    };
  }, [map]);

  // ✅ Project coordinates (only when cursor exists)
  let utm = null;
  if (latlng) {
    utm = lonLatToUTM(latlng.lng, latlng.lat);
  }

  return (
    <div className="map-status-bar">
      <span>{scale}</span>

      {latlng && (
        <span>
          {toDMS(latlng.lat, true)} | {toDMS(latlng.lng, false)}
        </span>
      )}

      <span>
        X: {utm ? utm[0].toFixed(2) : "—"} |
        Y: {utm ? utm[1].toFixed(2) : "—"}
      </span>

      <span>WGS 84 / UTM Zone 44N (EPSG:32644)</span>

      <span className="status-right">
        © Developed by ASSPL.
      </span>
    </div>
  );
}
