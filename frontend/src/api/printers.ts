import api from "@/api/client";

export interface Printer {
  id: number;
  name: string;
  host: string;
  model: string;
  status: string;
  department: number | null;
  cost_per_page_bw: string;
  cost_per_page_color: string;
  scan_cost_per_page: string;
}

export async function listPrinters(): Promise<Printer[]> {
  const { data } = await api.get<Printer[]>("/printers");
  return data;
}

export async function createPrinter(p: Partial<Printer>): Promise<Printer> {
  const { data } = await api.post<Printer>("/printers", p);
  return data;
}

export async function updatePrinter(id: number, p: Partial<Printer>): Promise<Printer> {
  const { data } = await api.patch<Printer>(`/printers/${id}`, p);
  return data;
}

export async function deletePrinter(id: number): Promise<void> {
  await api.delete(`/printers/${id}`);
}