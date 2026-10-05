import api from "@/api/client";

export interface Job {
  id: number;
  uuid: string;
  job_type: string;
  source: string;
  user: number | null;
  user_email: string | null;
  username: string;
  printer: number | null;
  printer_name: string;
  document_name: string;
  pages: number;
  copies: number;
  color: boolean;
  duplex: boolean;
  submitted_at: string;
  captured_at: string;
  cost: string;
  flags: string[];
}

export async function listJobs(): Promise<Job[]> {
  const { data } = await api.get<Job[]>("/jobs");
  return data;
}