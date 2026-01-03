import { useEffect, useState } from "react";
import API from "../api";

export default function ProjectList({ onSelect }) {
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    API.get("/api/projects/")
      .then(res => setProjects(res.data))
      .catch(err => console.error("Projects load failed", err));
  }, []);

  return (
    <div style={{ padding: 10 }}>
      <h3>Projects</h3>
      <ul>
        {projects.map(p => (
          <li key={p.id}>
            <button onClick={() => onSelect(p)}>{p.name}</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
