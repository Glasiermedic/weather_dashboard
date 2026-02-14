import apiClient from "./apiClient";

export async function fetchGraphData({ metric, stationId, period }) {
  const res = await apiClient.get("/api/graph_data", {
    params: {
      metric,
      station_id: stationId,
      period,
    },
  });
  return res.data;
}
