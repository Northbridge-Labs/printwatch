import { useQuery } from "@tanstack/react-query";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import { fetchSummary } from "@/api/reporting";

export default function DashboardPage() {
  const { data } = useQuery({
    queryKey: ["summary"],
    queryFn: () => fetchSummary(),
  });

  return (
    <>
      <Typography variant="h4" mb={3}>Dashboard</Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary">Total jobs</Typography>
              <Typography variant="h4">{data?.total_jobs ?? "-"}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary">Total pages</Typography>
              <Typography variant="h4">{data?.total_pages ?? "-"}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography color="text.secondary">Total cost</Typography>
              <Typography variant="h4">{data?.total_cost ?? "-"}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6">By job type</Typography>
              <pre>{JSON.stringify(data?.by_type ?? [], null, 2)}</pre>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </>
  );
}