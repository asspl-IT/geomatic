import { GeoJSON, ImageOverlay, useMap } from "react-leaflet";
import { useEffect, useState } from "react";
import axios from "axios";
import L from "leaflet";

const API_BASE = "http://127.0.0.1:8000";

export default function LayerRenderer({ layer }) {
  const map = useMap();
  const [geojson, setGeojson] = useState(null);

  // -------- VECTOR (GeoJSON) --------
  useEffect(() => {
    if (layer.type === "vector" && layer.format === "geojson") {
      axios
        .get(`${API_BASE}${layer.full_path}`)
        .then((res) => {
          setGeojson(res.data);
        })
        .catch((err) => {
          console.error("Failed to load GeoJSON:", err);
        });
    }
  }, [layer]);

  useEffect(() => {
    if (geojson) {
      const bounds = L.geoJSON(geojson).getBounds();
      map.fitBounds(bounds);
    }
  }, [geojson, map]);

  if (geojson) {
    return (
      <GeoJSON
        data={geojson}
        style={{ color: "blue", weight: 2 }}
      />
    );
  }

  // -------- RASTER (ImageOverlay) --------
  if (layer.type === "raster" && layer.bounds) {
    const bounds = [
      [layer.bounds.ymin, layer.bounds.xmin],
      [layer.bounds.ymax, layer.bounds.xmax],
    ];

    return (
      <ImageOverlay
        url={`${API_BASE}${layer.full_path}`}
        bounds={bounds}
        opacity={0.7}
      />
    );
  }

  return null;
}
