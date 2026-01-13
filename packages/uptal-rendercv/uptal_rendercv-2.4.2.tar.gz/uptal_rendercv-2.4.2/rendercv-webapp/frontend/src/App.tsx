import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { Alert, Collapse } from "@mui/material";
import { Toaster } from "react-hot-toast";
import { CVProvider } from "./components/CVProvider";
import Header from "./components/Layout/Header";
import SplitView from "./components/Layout/SplitView";
import { useCV } from "./hooks/useCV";

const theme = createTheme({
  palette: {
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#dc004e",
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function AppContent() {
  const { appError, setAppError } = useCV();

  return (
    <div className="app">
      <Collapse in={!!appError}>
        {appError && (
          <Alert
            severity="error"
            onClose={() => setAppError(null)}
            sx={{ m: 2, whiteSpace: "pre-wrap" }}
          >
            {appError}
          </Alert>
        )}
      </Collapse>
      <Header />
      <SplitView />
      <Toaster position="top-right" />
    </div>
  );
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <CVProvider>
        <AppContent />
      </CVProvider>
    </ThemeProvider>
  );
}

export default App;
