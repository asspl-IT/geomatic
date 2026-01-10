import { useEffect, useRef } from "react";

/* global Potree */

export default function PotreeView({ layer }) {
  const viewerRef = useRef(null);

  useEffect(() => {
    if (!layer) return;

    const container = document.getElementById("potree-container");
    if (!container) return;

    // Allow mouse events for Potree only when active
    container.style.pointerEvents = "auto";

    // Clear previous viewer
    container.innerHTML = "";

    // Create viewer
    const viewer = new Potree.Viewer(container);
    viewerRef.current = viewer;

    viewer.setEDLEnabled(true);
    viewer.setFOV(60);
    viewer.setPointBudget(1_500_000);
    viewer.setBackground("gradient");

    viewer.loadSettingsFromURL();

    const cloudUrl = `/media/potree/layer_${layer.id}/cloud.js`;

    Potree.loadPointCloud(cloudUrl, layer.name, e => {
      const pointcloud = e.pointcloud;

      viewer.scene.addPointCloud(pointcloud);

      pointcloud.material.pointSizeType = Potree.PointSizeType.ADAPTIVE;
      pointcloud.material.size = 1.5;
      pointcloud.material.activeAttributeName = "rgba";

      viewer.fitToScreen();
    });

    return () => {
      container.innerHTML = "";
      container.style.pointerEvents = "none";
    };
  }, [layer]);

  return null;
}
