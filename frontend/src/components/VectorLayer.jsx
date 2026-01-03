import { GeoJSON } from "react-leaflet";
import { useEffect, useState } from "react";
import API from "../api";

export default function VectorLayer({ layerId }) {
  const [geojson, setGeojson] = useState(null);

  useEffect(() => {
    API.get(`/api/layers/${layerId}/geojson/`)
      .then(res => setGeojson(res.data))
      .catch(err => console.error("GeoJSON load failed", err));
  }, [layerId]);

  if (!geojson) return null;

  return <GeoJSON data={geojson} />;
}
