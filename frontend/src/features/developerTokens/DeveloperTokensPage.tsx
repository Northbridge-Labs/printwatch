import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import Alert from "@mui/material/Alert";
import { listTokens, mintToken, revokeToken } from "@/api/developerTokens";

export default function DeveloperTokensPage() {
  const { data } = useQuery({
    queryKey: ["dev-tokens"],
    queryFn: listTokens,
  });
  const qc = useQueryClient();
  const [name, setName] = useState("");
  const [scopes, setScopes] = useState("");
  const [minted, setMinted] = useState<string | null>(null);

  const mintMut = useMutation({
    mutationFn: () => mintToken(name, scopes ? scopes.split(",") : []),
    onSuccess: (t) => {
      setMinted(t.token);
      setName("");
      setScopes("");
      qc.invalidateQueries({ queryKey: ["dev-tokens"] });
    },
  });

  const revokeMut = useMutation({
    mutationFn: (id: number) => revokeToken(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["dev-tokens"] }),
  });

  return (
    <>
      <Typography variant="h4" mb={2}>Developer tokens</Typography>
      <TextField
        label="Token name" value={name}
        onChange={(e) => setName(e.target.value)} sx={{ mr: 2 }}
      />
      <TextField
        label="Scopes (comma-separated)" value={scopes}
        onChange={(e) => setScopes(e.target.value)} sx={{ mr: 2 }}
      />
      <Button
        variant="contained"
        onClick={() => mintMut.mutate()}
        disabled={!name}
      >
        Mint
      </Button>
      {minted && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          Copy this token now — it won't be shown again:
          <pre>{minted}</pre>
        </Alert>
      )}
      <TableContainer component={Paper} sx={{ mt: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>JTI</TableCell>
              <TableCell>Scopes</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Revoked</TableCell>
              <TableCell></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(data ?? []).map((t) => (
              <TableRow key={t.id}>
                <TableCell>{t.id}</TableCell>
                <TableCell>{t.name}</TableCell>
                <TableCell>{t.jti}</TableCell>
                <TableCell>{t.scopes.join(", ")}</TableCell>
                <TableCell>{t.created_at}</TableCell>
                <TableCell>{t.revoked_at ?? "-"}</TableCell>
                <TableCell>
                  {!t.revoked_at && (
                    <Button
                      color="error"
                      size="small"
                      onClick={() => revokeMut.mutate(t.id)}
                    >
                      Revoke
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
}