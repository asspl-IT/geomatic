import { useEffect, useState } from "react";
import { GeoJSON, useMap } from "react-leaflet";
import axios from "../api";
import L from "leaflet";

export default function VectorLayer({ layerId, projectCRS }) {
  const map = useMap();
  const [data, setData] = useState(null);

  useEffect(() => {
    axios
      .get(`/api/layers/${layerId}/geojson/`)
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, [layerId]);

  useEffect(() => {
    if (!data) return;

    const tempLayer = L.geoJSON(data);

    if (tempLayer.getBounds().isValid()) {
      map.fitBounds(tempLayer.getBounds(), {
        padding: [30, 30],
        maxZoom: 18,
      });
    }
  }, [data, map]);

  // Style like GIS
  const styleFeature = feature => ({
    color: feature.properties?.line_color
      ? `rgb(${feature.properties.line_color.replace("RGB", "").replace(/[()]/g, "")})`
      : "#ffcc00",
    weight: feature.properties?.line_width || 2,
    opacity: 0.9,
  });

  // Popup + Labels
  const onEachFeature = (feature, layer) => {
    let html = "<table>";
    for (const key in feature.properties) {
      html += `<tr><td><b>${key}</b></td><td>${feature.properties[key]}</td></tr>`;
    }
    html += "</table>";
    layer.bindPopup(html);

    if (feature.properties?.name) {
      layer.bindTooltip(feature.properties.name, {
        permanent: true,
        direction: "center",
        className: "gis-label",
      });
    }
  };

  if (!data) return null;

  return (
    <GeoJSON
      data={data}
      style={styleFeature}
      onEachFeature={onEachFeature}
    />
  );
}

