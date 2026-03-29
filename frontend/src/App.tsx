import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/contexts/AuthContext";
import { SessionProvider } from "@/contexts/SessionContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import Login from "./pages/Login";
import Register from "./pages/Register";
import MapScreen from "./pages/MapScreen";
import ReadingScreen from "./pages/ReadingScreen";
import Dashboard from "./pages/Dashboard";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AuthProvider>
          <SessionProvider>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/" element={<ProtectedRoute><MapScreen /></ProtectedRoute>} />
              <Route path="/read/:node_id" element={<ProtectedRoute><ReadingScreen /></ProtectedRoute>} />
              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </SessionProvider>
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
