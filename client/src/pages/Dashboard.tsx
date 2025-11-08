import { useQuery } from "@tanstack/react-query";
import { Link } from "wouter";
import {
  BookOpen,
  Briefcase,
  FileText,
  Layers,
  SquareKanban,
  TrendingUp,
  Upload,
  Calendar,
  Target,
  Clock,
  AlertCircle,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import type { Topic, StudyPlan } from "@shared/schema";

export default function Dashboard() {
  const { data: topics = [], isLoading: topicsLoading, error: topicsError } = useQuery<Topic[]>({
    queryKey: ["/api/topics"],
  });

  const { data: plan, isLoading: planLoading, error: planError } = useQuery<StudyPlan | null>({
    queryKey: ["/api/plan"],
  });

  const overallMastery =
    topics.length > 0
      ? Math.round(topics.reduce((acc, t) => acc + t.masteryScore, 0) / topics.length)
      : 0;

  const todayBlocks = plan?.blocks.filter((b) => {
    const blockDate = new Date(b.scheduledFor).toDateString();
    return blockDate === new Date().toDateString();
  }) || [];

  const quickActions = [
    { title: "Upload Materials", icon: Upload, href: "/ingest", color: "bg-chart-1" },
    { title: "Start Learning", icon: BookOpen, href: "/learn", color: "bg-chart-2" },
    { title: "Practice Questions", icon: FileText, href: "/practice", color: "bg-chart-3" },
    { title: "Take Mock Test", icon: SquareKanban, href: "/mock", color: "bg-chart-4" },
    { title: "Placement Prep", icon: Briefcase, href: "/placement", color: "bg-chart-5" },
    { title: "Review Flashcards", icon: Layers, href: "/flashcards", color: "bg-primary" },
  ];

  if (topicsError || planError) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-4xl font-bold">Dashboard</h1>
          <p className="mt-2 text-muted-foreground">
            Track your progress and stay on top of your study goals
          </p>
        </div>
        <Card>
          <CardContent className="py-12 text-center">
            <AlertCircle className="mx-auto h-12 w-12 text-destructive" />
            <h3 className="mt-4 text-lg font-medium">Error loading dashboard</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              {topicsError?.message || planError?.message || "Failed to load data. Please try again."}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (topicsLoading || planLoading) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-4xl font-bold">Dashboard</h1>
          <p className="mt-2 text-muted-foreground">
            Track your progress and stay on top of your study goals
          </p>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader className="space-y-2">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-8 w-20" />
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="space-y-2">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-8 w-20" />
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="space-y-2">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-8 w-20" />
            </CardHeader>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold">Dashboard</h1>
        <p className="mt-2 text-muted-foreground">
          Track your progress and stay on top of your study goals
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card data-testid="card-mastery">
          <CardHeader className="flex flex-row items-center justify-between gap-4 space-y-0 pb-2">
            <CardTitle className="text-base font-medium">Overall Mastery</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">{overallMastery}%</div>
            <Progress value={overallMastery} className="mt-3" />
            <p className="mt-2 text-sm text-muted-foreground">
              {topics.length} topics tracked
            </p>
          </CardContent>
        </Card>

        <Card data-testid="card-today">
          <CardHeader className="flex flex-row items-center justify-between gap-4 space-y-0 pb-2">
            <CardTitle className="text-base font-medium">Today's Schedule</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">{todayBlocks.length}</div>
            <p className="mt-3 text-sm text-muted-foreground">
              {todayBlocks.filter((b) => b.completed).length} completed
            </p>
            <p className="text-sm text-muted-foreground">
              {todayBlocks.filter((b) => !b.completed).length} remaining
            </p>
          </CardContent>
        </Card>

        <Card data-testid="card-streak">
          <CardHeader className="flex flex-row items-center justify-between gap-4 space-y-0 pb-2">
            <CardTitle className="text-base font-medium">Study Streak</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">7 days</div>
            <p className="mt-3 text-sm text-muted-foreground">
              Keep it up!
            </p>
          </CardContent>
        </Card>
      </div>

      {plan && (
        <Card data-testid="card-study-plan">
          <CardHeader>
            <CardTitle>Study Plan</CardTitle>
            <CardDescription>
              {plan.examType} exam on {new Date(plan.endDate).toLocaleDateString()}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="font-medium">Weekly Goal</span>
                <span className="text-muted-foreground">{plan.weeklyGoal}</span>
              </div>
            </div>
            
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Today's Blocks</h4>
              {todayBlocks.length === 0 ? (
                <p className="text-sm text-muted-foreground">No blocks scheduled for today</p>
              ) : (
                <div className="space-y-2">
                  {todayBlocks.map((block) => (
                    <div
                      key={block.id}
                      className="flex items-center gap-4 rounded-md border p-4"
                    >
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <div className="flex-1">
                        <p className="text-sm font-medium">{block.topicName}</p>
                        <p className="text-sm text-muted-foreground capitalize">
                          {block.activity} • {block.duration} min
                        </p>
                      </div>
                      {block.completed && (
                        <Badge variant="outline">Completed</Badge>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      <div>
        <h2 className="mb-4 text-2xl font-semibold">Quick Actions</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {quickActions.map((action) => (
            <Link key={action.title} href={action.href} data-testid={`link-${action.href.replace("/", "")}`}>
              <Card className="hover-elevate cursor-pointer transition-all">
                <CardHeader className="flex flex-row items-center gap-4 space-y-0">
                  <div className={`flex h-12 w-12 items-center justify-center rounded-md ${action.color} text-white`}>
                    <action.icon className="h-6 w-6" />
                  </div>
                  <CardTitle className="text-base">{action.title}</CardTitle>
                </CardHeader>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {topics.length > 0 && (
        <Card data-testid="card-topic-heatmap">
          <CardHeader>
            <CardTitle>Topic Mastery Heatmap</CardTitle>
            <CardDescription>
              Focus on topics with lower mastery scores
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topics.slice(0, 10).map((topic) => (
                <div key={topic.id} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{topic.name}</span>
                      <Badge variant="outline" className="text-xs">
                        Importance: {topic.importanceScore}/10
                      </Badge>
                    </div>
                    <span className="text-muted-foreground">{topic.masteryScore}%</span>
                  </div>
                  <Progress value={topic.masteryScore} />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
