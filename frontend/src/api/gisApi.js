import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export const uploadGISFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await axios.post(
    `${API_BASE}/api/upload-geo-project/`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );

  return response.data;
};

export const getMediaUrl = (path) => {
  return `${API_BASE}${path}`;
};
