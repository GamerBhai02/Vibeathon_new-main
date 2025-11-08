import {
  BookOpen,
  Brain,
  Briefcase,
  FileText,
  Home,
  Layers,
  SquareKanban,
  Upload,
} from "lucide-react";
import { Link, useLocation } from "wouter";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
} from "@/components/ui/sidebar";

const navigation = [
  {
    title: "Dashboard",
    url: "/",
    icon: Home,
    shortcut: "g d",
  },
  {
    title: "Ingest",
    url: "/ingest",
    icon: Upload,
    shortcut: "g i",
  },
  {
    title: "Learn",
    url: "/learn",
    icon: BookOpen,
    shortcut: "g l",
  },
  {
    title: "Practice",
    url: "/practice",
    icon: FileText,
    shortcut: "g p",
  },
  {
    title: "Mock Test",
    url: "/mock",
    icon: SquareKanban,
    shortcut: "g m",
  },
  {
    title: "Placement",
    url: "/placement",
    icon: Briefcase,
    shortcut: "g c",
  },
  {
    title: "Flashcards",
    url: "/flashcards",
    icon: Layers,
    shortcut: "g f",
  },
];

export function AppSidebar() {
  const [location] = useLocation();

  return (
    <Sidebar data-testid="sidebar-main">
      <SidebarHeader className="border-b border-sidebar-border p-6">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <Brain className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">Agentverse</h2>
            <p className="text-xs text-muted-foreground">Study Buddy</p>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigation.map((item) => {
                const isActive = location === item.url;
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton asChild isActive={isActive}>
                      <Link href={item.url} data-testid={`link-${item.title.toLowerCase()}`}>
                        <item.icon className="h-4 w-4" />
                        <span>{item.title}</span>
                        <span className="ml-auto text-xs text-muted-foreground opacity-60">
                          {item.shortcut}
                        </span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
