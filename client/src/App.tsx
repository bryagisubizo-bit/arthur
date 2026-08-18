/**
 * Orbital Command Atelier: app shell stays dark, composed, and permission-forward.
 */
import { Toaster } from "@/components/ui/sonner";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";

export default function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="dark">
        <Home />
        <Toaster richColors position="bottom-right" />
      </ThemeProvider>
    </ErrorBoundary>
  );
}
