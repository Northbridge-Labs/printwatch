import api from "@/api/client";

export interface Summary {
  range: { start: string; end: string };
  total_jobs: number;
  total_pages: number;
  total_cost: string;
  by_type: { job_type: string; pages: number; cost: string; count: number }[];
}

export async function fetchSummary(start?: string, end?: string): Promise<Summary> {
  const { data } = await api.get<Summary>("/reporting/summary", {
    params: { start, end },
  });
  return data;
}

export async function fetchPagesByUser(start: string, end: string, type?: string) {
  const { data } = await api.get("/reporting/pages-by-user", {
    params: { start, end, type },
  });
  return data;
}

export async function fetchPagesByPrinter(start: string, end: string, type?: string) {
  const { data } = await api.get("/reporting/pages-by-printer", {
    params: { start, end, type },
  });
  return data;
}

export async function fetchJobsByType(start: string, end: string) {
  const { data } = await api.get("/reporting/jobs-by-type", {
    params: { start, end },
  });
  return data;
}

export async function fetchCostTrend(start: string, end: string, type?: string) {
  const { data } = await api.get("/reporting/cost-trend", {
    params: { start, end, type },
  });
  return data;
}