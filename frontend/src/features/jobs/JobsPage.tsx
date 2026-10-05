import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import ToggleButton from "@mui/material/ToggleButton";
import { DataGrid, GridColDef } from "@mui/x-data-grid";
import { listJobs, Job } from "@/api/jobs";

const columns: GridColDef<Job>[] = [
  { field: "id", headerName: "ID", width: 70 },
  { field: "job_type", headerName: "Type", width: 90 },
  { field: "source", headerName: "Source", width: 110 },
  { field: "username", headerName: "User", width: 140 },
  { field: "printer_name", headerName: "Printer", width: 160 },
  { field: "document_name", headerName: "Document", width: 220 },
  { field: "pages", headerName: "Pages", width: 90 },
  { field: "copies", headerName: "Copies", width: 90 },
  { field: "color", headerName: "Color", width: 80, type: "boolean" },
  { field: "cost", headerName: "Cost", width: 100 },
  { field: "submitted_at", headerName: "Submitted", width: 180 },
];

export default function JobsPage() {
  const [type, setType] = useState<string>("all");
  const { data, isLoading } = useQuery({
    queryKey: ["jobs"],
    queryFn: listJobs,
  });

  const filtered = (data ?? []).filter((j) =>
    type === "all" ? true : j.job_type === type,
  );

  return (
    <>
      <ToggleButtonGroup
        size="small"
        value={type}
        onChange={(_, v) => v && setType(v)}
        sx={{ mb: 2 }}
      >
        <ToggleButton value="all">All</ToggleButton>
        <ToggleButton value="print">Print</ToggleButton>
        <ToggleButton value="scan">Scan</ToggleButton>
        <ToggleButton value="copy">Copy</ToggleButton>
      </ToggleButtonGroup>
      <div style={{ height: 600, width: "100%" }}>
        <DataGrid rows={filtered} columns={columns} loading={isLoading} />
      </div>
    </>
  );
}