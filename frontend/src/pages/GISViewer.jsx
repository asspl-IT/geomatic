import { useState } from "react";
import ProjectList from "../components/ProjectList";
import LayerList from "../components/LayerList";
import MapView from "../components/MapView";

export default function GISViewer() {
  const [project, setProject] = useState(null);
  const [activeLayers, setActiveLayers] = useState([]);

  const toggleLayer = (layer, on) => {
    setActiveLayers(prev =>
      on ? [...prev, layer] : prev.filter(l => l.id !== layer.id)
    );
  };

  return (
    <div style={{ display: "flex" }}>
      <div style={{ width: 300, padding: 10, borderRight: "1px solid #ccc" }}>
        <ProjectList onSelect={setProject} />
        {project && (
          <LayerList projectId={project.id} onToggle={toggleLayer} />
        )}
      </div>

      <div style={{ flex: 1 }}>
        <MapView activeLayers={activeLayers} />
      </div>
    </div>
  );
}
