import { useState, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { BookOpen, ExternalLink, Lightbulb, AlertTriangle, AlertCircle, Loader2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import type { Topic } from "@shared/schema";

interface LessonContent {
  title: string;
  sections: Array<{ heading: string; content: string }>;
  commonMistakes: string[];
  tips?: string[];
  citations: string[];
  confidence: "High" | "Medium" | "Low";
}

export default function Learn() {
  const [selectedTopic, setSelectedTopic] = useState<string>("");
  const [lessonContent, setLessonContent] = useState<LessonContent | null>(null);

  const { data: topics = [], isLoading, error } = useQuery<Topic[]>({
    queryKey: ["/api/topics"],
  });

  const generateLessonMutation = useMutation({
    mutationFn: async (topicId: string) => {
      const response = await fetch('/api/learn/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ topicId })
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate lesson');
      }
      
      return response.json();
    },
    onSuccess: (data) => {
      setLessonContent(data);
    },
    onError: (error) => {
      console.error('Failed to generate lesson:', error);
      // Set fallback content
      const topic = topics.find(t => t.id === selectedTopic);
      if (topic) {
        setLessonContent({
          title: `Understanding ${topic.name}`,
          sections: [
            {
              heading: topic.name,
              content: topic.summary || "Content is being processed. Please check back later.",
            },
          ],
          commonMistakes: [],
          tips: ["Review the material regularly"],
          citations: [],
          confidence: "Medium",
        });
      }
    }
  });

  // Generate lesson when topic is selected
  useEffect(() => {
    if (selectedTopic) {
      setLessonContent(null); // Clear previous content
      generateLessonMutation.mutate(selectedTopic);
    }
  }, [selectedTopic]);

  const currentTopic = topics.find((t) => t.id === selectedTopic);

  if (error) {
    return (
      <div className="mx-auto max-w-4xl space-y-8">
        <div>
          <h1 className="text-4xl font-bold">Learn</h1>
          <p className="mt-2 text-muted-foreground">
            AI-generated micro-lessons with step-by-step explanations
          </p>
        </div>
        <Card>
          <CardContent className="py-12 text-center">
            <AlertCircle className="mx-auto h-12 w-12 text-destructive" />
            <h3 className="mt-4 text-lg font-medium">Error loading topics</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              {error?.message || "Failed to load data. Please try again."}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl space-y-8">
        <div>
          <h1 className="text-4xl font-bold">Learn</h1>
          <p className="mt-2 text-muted-foreground">
            AI-generated micro-lessons with step-by-step explanations
          </p>
        </div>
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-64" />
            <Skeleton className="h-4 w-48" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div>
        <h1 className="text-4xl font-bold">Learn</h1>
        <p className="mt-2 text-muted-foreground">
          AI-generated micro-lessons with step-by-step explanations
        </p>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex-1">
          <Select value={selectedTopic} onValueChange={setSelectedTopic}>
            <SelectTrigger data-testid="select-topic">
              <SelectValue placeholder="Select a topic to learn" />
            </SelectTrigger>
            <SelectContent>
              {topics.map((topic) => (
                <SelectItem key={topic.id} value={topic.id}>
                  {topic.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {currentTopic ? (
        <div className="space-y-6">
          {generateLessonMutation.isPending ? (
            <Card data-testid="card-lesson">
              <CardContent className="py-12 text-center">
                <Loader2 className="mx-auto h-12 w-12 animate-spin text-primary" />
                <p className="mt-4 text-sm text-muted-foreground">
                  Generating lesson content with AI...
                </p>
              </CardContent>
            </Card>
          ) : lessonContent ? (
            <Card data-testid="card-lesson">
              <CardHeader>
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1">
                    <CardTitle>{lessonContent.title}</CardTitle>
                    <CardDescription>Topic: {currentTopic.name}</CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={lessonContent.confidence === "High" ? "default" : "secondary"}>
                      {lessonContent.confidence} Confidence
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {lessonContent.sections.map((section, idx) => (
                  <div key={idx} className="space-y-3">
                    <h3 className="text-lg font-semibold">{section.heading}</h3>
                    <p className="leading-relaxed text-card-foreground whitespace-pre-wrap">
                      {section.content}
                    </p>
                    {idx < lessonContent.sections.length - 1 && <Separator className="mt-4" />}
                  </div>
                ))}

                {lessonContent.commonMistakes.length > 0 && (
                  <div className="mt-8 rounded-md bg-muted p-6">
                    <div className="flex items-start gap-3">
                      <AlertTriangle className="h-5 w-5 text-destructive" />
                      <div>
                        <h4 className="font-medium">Common Mistakes</h4>
                        <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                          {lessonContent.commonMistakes.map((mistake, idx) => (
                            <li key={idx}>• {mistake}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}

                {lessonContent.tips && lessonContent.tips.length > 0 && (
                  <div className="mt-6 rounded-md border p-4">
                    <div className="flex items-start gap-3">
                      <Lightbulb className="h-5 w-5 text-primary" />
                      <div>
                        <h4 className="text-sm font-medium">Pro Tips</h4>
                        <ul className="mt-1 space-y-1 text-sm text-muted-foreground">
                          {lessonContent.tips.map((tip, idx) => (
                            <li key={idx}>• {tip}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}

                {lessonContent.citations.length > 0 && (
                  <div className="mt-6">
                    <h4 className="mb-3 text-sm font-medium text-muted-foreground">
                      Sources
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {lessonContent.citations.map((citation, idx) => (
                        <Badge
                          key={idx}
                          variant="outline"
                          className="gap-1"
                        >
                          <ExternalLink className="h-3 w-3" />
                          {citation}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : null}

          <div className="flex gap-4">
            <Button variant="outline" className="flex-1" data-testid="button-practice">
              Practice This Topic
            </Button>
            <Button className="flex-1" data-testid="button-next-lesson">
              Next Lesson
            </Button>
          </div>
        </div>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <BookOpen className="mx-auto h-12 w-12 text-muted-foreground" />
            <h3 className="mt-4 text-lg font-medium">Select a topic</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Choose a topic from the dropdown to start learning
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
