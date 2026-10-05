import { useQuery } from "@tanstack/react-query";
import { DataGrid, GridColDef } from "@mui/x-data-grid";
import { listPrinters, Printer } from "@/api/printers";

const columns: GridColDef<Printer>[] = [
  { field: "id", headerName: "ID", width: 70 },
  { field: "name", headerName: "Name", width: 200 },
  { field: "model", headerName: "Model", width: 150 },
  { field: "host", headerName: "Host", width: 150 },
  { field: "status", headerName: "Status", width: 110 },
  { field: "cost_per_page_bw", headerName: "B/W cost", width: 110 },
  { field: "cost_per_page_color", headerName: "Color cost", width: 110 },
  { field: "scan_cost_per_page", headerName: "Scan cost", width: 110 },
];

export default function PrintersPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["printers"],
    queryFn: listPrinters,
  });

  return (
    <div style={{ height: 600, width: "100%" }}>
      <DataGrid rows={data ?? []} columns={columns} loading={isLoading} />
    </div>
  );
}