import { useEffect, useState } from "react";
import API from "../api";

export default function LayerList({ projectId, onToggle }) {
  const [layers, setLayers] = useState([]);

  useEffect(() => {
    if (!projectId) return;

    API.get(`/api/projects/${projectId}/layers/`)
        .then(res => {
        console.log("Layers response:", res.data); // 🔍
        setLayers(res.data);
        })
        .catch(err => console.error("Layers load failed", err));
  }, [projectId]);

  return (
    <div>
      <h4>Layers</h4>
      {layers.map(l => (
        <div key={l.id}>
          <input
            type="checkbox"
            onChange={(e) => onToggle(l, e.target.checked)}
          />
          {l.name} ({l.type})
        </div>
      ))}
    </div>
  );
}
