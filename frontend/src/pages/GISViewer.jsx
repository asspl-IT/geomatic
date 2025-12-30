import React, { useState } from "react";
import FileUpload from "../components/FileUpload";
import MapView from "../components/MapView";

export default function GISViewer() {
  const [project, setProject] = useState(null);

  return (
    <div style={{ padding: "10px" }}>
      <h2>GIS Viewer</h2>

      <FileUpload
        onLoaded={(data) => {
          console.log("PROJECT DATA RECEIVED:", data);
          setProject(data);
        }}
      />

      {project && project.layers && project.layers.length > 0 && (
        <MapView project={project} />
      )}
    </div>
  );
}
