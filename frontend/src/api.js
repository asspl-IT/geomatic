import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export async function uploadLayer(formData) {
  return axios.post(`${API_BASE}/upload/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  }).then(res => res.data);
}

export async function getLayerGeoJSON(layerId) {
  return axios.get(`${API_BASE}/layers/${layerId}/geojson/`)
              .then(res => res.data);
}
