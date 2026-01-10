import { useState, useEffect } from "react";
import ProjectList from "../components/ProjectList";
import LayerList from "../components/LayerList";
import MapView from "../components/MapView";

export default function GISViewer() {
  const [project, setProject] = useState(null);
  const [projectCRS, setProjectCRS] = useState("EPSG:4326");

  // 🔹 Separate responsibilities
  const [activeVectorLayers, setActiveVectorLayers] = useState([]);
  const [activeLidarLayer, setActiveLidarLayer] = useState(null);

  // 🔹 Layer toggle handler (TYPE-AWARE)
  const toggleLayer = (layer, on) => {
    if (layer.type === "lidar") {
      setActiveLidarLayer(on ? layer : null);
      return;
    }

    // vector / raster layers
    setActiveVectorLayers(prev => {
      if (on) {
        if (prev.find(l => l.id === layer.id)) return prev;
        return [...prev, layer];
      }
      return prev.filter(l => l.id !== layer.id);
    });
  };

  // 🔹 Reset layers when project changes
  useEffect(() => {
    if (project) {
      setActiveVectorLayers([]);
      setActiveLidarLayer(null);
    }
  }, [project]);

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* LEFT SIDEBAR */}
      <div style={{ width: 300, padding: 10, borderRight: "1px solid #ccc" }}>
        <ProjectList
          onSelect={(p) => {
            setProject(p);
            setProjectCRS(p.crs || "EPSG:4326");
          }}
        />

        {project && (
          <LayerList
            projectId={project.id}
            onToggle={toggleLayer}
            activeLayers={[...activeVectorLayers, activeLidarLayer].filter(Boolean)}
          />
        )}
      </div>

      {/* MAP AREA */}
      <div style={{ flex: 1 }}>
        <MapView
          activeLayers={activeVectorLayers}
          projectCRS={projectCRS}
        />
      </div>
    </div>
  );
}
