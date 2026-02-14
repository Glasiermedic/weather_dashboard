import axios from "axios";

const baseURL =
  (import.meta.env.VITE_API_BASE_URL || "").replace(/\/+$/, "");

const apiClient = axios.create({
  baseURL, // "" => same-origin
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

export default apiClient;

