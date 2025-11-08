import { useEffect } from "react";
import { Switch, Route, Redirect, useLocation } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { ThemeProvider } from "@/components/theme-provider";
import { ThemeToggle } from "@/components/theme-toggle";
import { AppSidebar } from "@/components/app-sidebar";
import { isAuthenticated } from "@/lib/auth";
import { useKeyboardShortcuts } from "@/lib/keyboard";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import Ingest from "@/pages/Ingest";
import Learn from "@/pages/Learn";
import Practice from "@/pages/Practice";
import MockTest from "@/pages/MockTest";
import Placement from "@/pages/Placement";
import Flashcards from "@/pages/Flashcards";
import NotFound from "@/pages/not-found";

function ProtectedRoute({ component: Component }: { component: React.ComponentType }) {
  const isAuth = isAuthenticated();
  
  if (!isAuth) {
    return <Redirect to="/login" />;
  }
  
  return <Component />;
}

function AppLayout({ children }: { children: React.ReactNode }) {
  useKeyboardShortcuts();
  
  return (
    <div className="flex h-screen w-full">
      <AppSidebar />
      <div className="flex flex-1 flex-col">
        <header className="flex h-14 items-center justify-between border-b px-6">
          <SidebarTrigger data-testid="button-sidebar-toggle" />
          <div className="flex items-center gap-2">
            <ThemeToggle />
          </div>
        </header>
        <main className="flex-1 overflow-auto p-6">
          <div className="mx-auto max-w-7xl">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

function Router() {
  const [location] = useLocation();
  const isAuth = isAuthenticated();

  if (location === "/" && !isAuth) {
    return <Redirect to="/login" />;
  }

  return (
    <Switch>
      <Route path="/login" component={Login} />
      <Route path="/">
        <ProtectedRoute component={Dashboard} />
      </Route>
      <Route path="/ingest">
        <ProtectedRoute component={Ingest} />
      </Route>
      <Route path="/learn">
        <ProtectedRoute component={Learn} />
      </Route>
      <Route path="/practice">
        <ProtectedRoute component={Practice} />
      </Route>
      <Route path="/mock">
        <ProtectedRoute component={MockTest} />
      </Route>
      <Route path="/placement">
        <ProtectedRoute component={Placement} />
      </Route>
      <Route path="/flashcards">
        <ProtectedRoute component={Flashcards} />
      </Route>
      <Route component={NotFound} />
    </Switch>
  );
}

export default function App() {
  const [location] = useLocation();
  const isLoginPage = location === "/login";

  const sidebarStyle = {
    "--sidebar-width": "16rem",
    "--sidebar-width-icon": "3rem",
  } as React.CSSProperties;

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="light">
        <TooltipProvider>
          {isLoginPage ? (
            <Router />
          ) : (
            <SidebarProvider style={sidebarStyle}>
              <AppLayout>
                <Router />
              </AppLayout>
            </SidebarProvider>
          )}
          <Toaster />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
