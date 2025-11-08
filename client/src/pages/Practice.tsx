import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { FileText, ChevronDown, ChevronUp, Lightbulb, CheckCircle, AlertCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import type { Topic } from "@shared/schema";

export default function Practice() {
  const [selectedTopic, setSelectedTopic] = useState<string>("");
  const [difficulty, setDifficulty] = useState<string>("medium");
  const [showHint, setShowHint] = useState(false);
  const [showSteps, setShowSteps] = useState(false);
  const [showSolution, setShowSolution] = useState(false);
  const [userAnswer, setUserAnswer] = useState("");

  const { data: topics = [], isLoading, error } = useQuery<Topic[]>({
    queryKey: ["/api/topics"],
  });

  const question = {
    id: "1",
    question:
      "Explain the difference between DELETE, TRUNCATE, and DROP commands in SQL. Provide examples and discuss when each should be used.",
    hint: "Think about what each command does to the table structure and data",
    steps: [
      "DELETE removes rows from a table based on a condition",
      "TRUNCATE removes all rows from a table but keeps the structure",
      "DROP removes the entire table including structure and data",
      "DELETE can be rolled back, TRUNCATE cannot in most databases",
      "DROP is irreversible and removes the table completely",
    ],
    fullSolution:
      "DELETE is a DML command that removes specific rows based on a WHERE clause and can be rolled back. TRUNCATE is a DDL command that removes all rows but preserves the table structure, is faster than DELETE, and cannot be rolled back. DROP is a DDL command that removes the entire table including its structure, data, and associated objects like indexes, and is irreversible. Use DELETE for selective row removal, TRUNCATE for quick table cleanup, and DROP when you want to remove the table entirely.",
    difficulty: "medium" as const,
    confidence: "High" as const,
  };

  if (error) {
    return (
      <div className="mx-auto max-w-4xl space-y-8">
        <div>
          <h1 className="text-4xl font-bold">Practice</h1>
          <p className="mt-2 text-muted-foreground">
            Answer questions with progressive hints and step-by-step solutions
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
          <h1 className="text-4xl font-bold">Practice</h1>
          <p className="mt-2 text-muted-foreground">
            Answer questions with progressive hints and step-by-step solutions
          </p>
        </div>
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-64" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-10 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div>
        <h1 className="text-4xl font-bold">Practice</h1>
        <p className="mt-2 text-muted-foreground">
          Answer questions with progressive hints and step-by-step solutions
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-4">
        <div className="flex-1 min-w-[200px]">
          <Select value={selectedTopic} onValueChange={setSelectedTopic}>
            <SelectTrigger data-testid="select-topic">
              <SelectValue placeholder="Select topic" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Topics</SelectItem>
              {topics.map((topic) => (
                <SelectItem key={topic.id} value={topic.id}>
                  {topic.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <Select value={difficulty} onValueChange={setDifficulty}>
          <SelectTrigger className="w-[150px]" data-testid="select-difficulty">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="easy">Easy</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="hard">Hard</SelectItem>
          </SelectContent>
        </Select>

        <Button variant="outline" data-testid="button-new-question">
          New Question
        </Button>
      </div>

      <Card data-testid="card-question">
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-1 flex-1">
              <div className="flex items-center gap-2">
                <Badge variant={question.difficulty === "hard" ? "destructive" : "default"}>
                  {question.difficulty}
                </Badge>
                <Badge variant={question.confidence === "High" ? "default" : "secondary"}>
                  {question.confidence} Confidence
                </Badge>
              </div>
              <CardTitle className="mt-3">{question.question}</CardTitle>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <label className="text-sm font-medium">Your Answer</label>
            <Textarea
              placeholder="Type your answer here..."
              className="mt-2 min-h-[150px]"
              value={userAnswer}
              onChange={(e) => setUserAnswer(e.target.value)}
              data-testid="textarea-answer"
            />
            <p className="mt-2 text-sm text-muted-foreground">
              {userAnswer.length} characters
            </p>
          </div>

          <div className="space-y-3">
            <Collapsible open={showHint} onOpenChange={setShowHint}>
              <CollapsibleTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full justify-between"
                  data-testid="button-hint"
                >
                  <span className="flex items-center gap-2">
                    <Lightbulb className="h-4 w-4" />
                    Show Hint
                  </span>
                  {showHint ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-3">
                <div className="rounded-md bg-muted p-4">
                  <p className="text-sm">{question.hint}</p>
                </div>
              </CollapsibleContent>
            </Collapsible>

            <Collapsible open={showSteps} onOpenChange={setShowSteps}>
              <CollapsibleTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full justify-between"
                  data-testid="button-steps"
                >
                  <span className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    Show Steps
                  </span>
                  {showSteps ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-3">
                <div className="space-y-2 rounded-md bg-muted p-4">
                  {question.steps.map((step, idx) => (
                    <div key={idx} className="flex gap-3">
                      <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground">
                        {idx + 1}
                      </div>
                      <p className="text-sm flex-1">{step}</p>
                    </div>
                  ))}
                </div>
              </CollapsibleContent>
            </Collapsible>

            <Collapsible open={showSolution} onOpenChange={setShowSolution}>
              <CollapsibleTrigger asChild>
                <Button
                  variant="outline"
                  className="w-full justify-between"
                  data-testid="button-solution"
                >
                  <span className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4" />
                    Show Full Solution
                  </span>
                  {showSolution ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="mt-3">
                <div className="rounded-md bg-muted p-4">
                  <p className="text-sm leading-relaxed">{question.fullSolution}</p>
                </div>
              </CollapsibleContent>
            </Collapsible>
          </div>

          <div className="flex gap-4">
            <Button variant="outline" className="flex-1" data-testid="button-skip">
              Skip Question
            </Button>
            <Button className="flex-1" data-testid="button-submit">
              Submit Answer
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
