import { Link, useNavigate } from "react-router-dom";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import Container from "@mui/material/Container";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import LogoutIcon from "@mui/icons-material/Logout";
import { useAuthStore } from "@/store/auth";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/printers", label: "Printers" },
  { to: "/jobs", label: "Jobs" },
  { to: "/quotas", label: "Quotas" },
  { to: "/alerts", label: "Alerts" },
  { to: "/developer-tokens", label: "Developer Tokens" },
];

export default function AppBarComponent() {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <MenuBookIcon sx={{ mr: 1 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 0, mr: 3 }}>
            PrintWatch
          </Typography>
          {links.map((l) => (
            <Button key={l.to} color="inherit" component={Link} to={l.to}>
              {l.label}
            </Button>
          ))}
          <Typography sx={{ flexGrow: 1 }} />
          <Button
            color="inherit"
            href="/api/docs/"
            target="_blank"
            rel="noopener noreferrer"
          >
            API Docs
          </Button>
          {user && (
            <Typography variant="body2" sx={{ mr: 2 }}>
              {user.email}
            </Typography>
          )}
          <IconButton
            color="inherit"
            onClick={() => {
              logout();
              navigate("/login");
            }}
          >
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ mt: 3 }} />
    </>
  );
}