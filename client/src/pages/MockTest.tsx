import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Clock, FileQuestion, ChevronLeft, ChevronRight, Flag, AlertCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import type { MockExam } from "@shared/schema";

export default function MockTest() {
  const [inExam, setInExam] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [flaggedQuestions, setFlaggedQuestions] = useState<Set<number>>(new Set());
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);
  const [timeLeft, setTimeLeft] = useState(7200);

  const { data: mocks = [], isLoading, error } = useQuery<MockExam[]>({
    queryKey: ["/api/mock/list"],
  });

  const currentMock = mocks[0];

  const formatTime = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hrs.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const handleStartExam = () => {
    setInExam(true);
    setCurrentQuestionIndex(0);
    setAnswers({});
    setFlaggedQuestions(new Set());
  };

  const handleAnswerChange = (questionId: string, answer: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: answer }));
  };

  const toggleFlag = (index: number) => {
    setFlaggedQuestions((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  const answeredCount = Object.keys(answers).filter((k) => answers[k]?.trim()).length;

  if (!inExam) {
    if (error) {
      return (
        <div className="mx-auto max-w-4xl space-y-8">
          <div>
            <h1 className="text-4xl font-bold">Mock Tests</h1>
            <p className="mt-2 text-muted-foreground">
              Full-length exam simulations with timer and grading
            </p>
          </div>
          <Card>
            <CardContent className="py-12 text-center">
              <AlertCircle className="mx-auto h-12 w-12 text-destructive" />
              <h3 className="mt-4 text-lg font-medium">Error loading mock tests</h3>
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
            <h1 className="text-4xl font-bold">Mock Tests</h1>
            <p className="mt-2 text-muted-foreground">
              Full-length exam simulations with timer and grading
            </p>
          </div>
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-32" />
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-20 w-full" />
            </CardContent>
          </Card>
        </div>
      );
    }

    return (
      <div className="mx-auto max-w-4xl space-y-8">
        <div>
          <h1 className="text-4xl font-bold">Mock Tests</h1>
          <p className="mt-2 text-muted-foreground">
            Full-length exam simulations with timer and grading
          </p>
        </div>

        <div className="grid gap-6">
          {mocks.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <FileQuestion className="mx-auto h-12 w-12 text-muted-foreground" />
                <h3 className="mt-4 text-lg font-medium">No mock tests yet</h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  Generate a mock test from the dashboard to get started
                </p>
              </CardContent>
            </Card>
          ) : (
            mocks.map((mock) => (
              <Card key={mock.id} data-testid={`mock-${mock.id}`}>
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <CardTitle>{mock.title}</CardTitle>
                      <CardDescription>{mock.type} Exam</CardDescription>
                    </div>
                    <Badge>{mock.type}</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Duration</p>
                      <p className="font-medium">{mock.duration} minutes</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Questions</p>
                      <p className="font-medium">{mock.questions.length}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Total Marks</p>
                      <p className="font-medium">{mock.totalMarks}</p>
                    </div>
                  </div>
                  <Button
                    className="w-full"
                    onClick={handleStartExam}
                    data-testid="button-start-exam"
                  >
                    Start Exam
                  </Button>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    );
  }

  if (!currentMock) return null;

  const currentQuestion = currentMock.questions[currentQuestionIndex];

  return (
    <div className="fixed inset-0 bg-background">
      <div className="flex h-full flex-col">
        <div className="flex items-center justify-between border-b px-6 py-4">
          <div>
            <h2 className="text-lg font-semibold">{currentMock.title}</h2>
            <p className="text-sm text-muted-foreground">
              Question {currentQuestionIndex + 1} of {currentMock.questions.length}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-2xl font-mono font-semibold" data-testid="text-timer">
              <Clock className="h-5 w-5" />
              {formatTime(timeLeft)}
            </div>
            <Button
              variant="outline"
              onClick={() => setShowSubmitDialog(true)}
              data-testid="button-submit-exam"
            >
              Submit Exam
            </Button>
          </div>
        </div>

        <div className="flex-1 overflow-auto p-6">
          <div className="mx-auto max-w-3xl space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between gap-4">
                  <CardTitle className="text-xl">
                    Question {currentQuestionIndex + 1}
                  </CardTitle>
                  <Badge variant="outline">{currentQuestion.marks} marks</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                <p className="leading-relaxed">{currentQuestion.question}</p>
                
                <div>
                  <label className="text-sm font-medium">Your Answer</label>
                  <Textarea
                    className="mt-2 min-h-[200px]"
                    placeholder="Type your answer here..."
                    value={answers[currentQuestion.id] || ""}
                    onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
                    data-testid="textarea-exam-answer"
                  />
                </div>

                <div className="flex items-center gap-4">
                  <Button
                    variant="outline"
                    onClick={() => toggleFlag(currentQuestionIndex)}
                    data-testid="button-flag"
                  >
                    <Flag
                      className={`h-4 w-4 ${flaggedQuestions.has(currentQuestionIndex) ? "fill-current" : ""}`}
                    />
                    {flaggedQuestions.has(currentQuestionIndex) ? "Flagged" : "Flag for Review"}
                  </Button>
                </div>
              </CardContent>
            </Card>

            <div className="flex items-center justify-between">
              <Button
                variant="outline"
                onClick={() => setCurrentQuestionIndex((prev) => Math.max(0, prev - 1))}
                disabled={currentQuestionIndex === 0}
                data-testid="button-prev"
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>

              <div className="text-sm text-muted-foreground">
                {answeredCount} of {currentMock.questions.length} answered
              </div>

              <Button
                variant="outline"
                onClick={() =>
                  setCurrentQuestionIndex((prev) =>
                    Math.min(currentMock.questions.length - 1, prev + 1)
                  )
                }
                disabled={currentQuestionIndex === currentMock.questions.length - 1}
                data-testid="button-next"
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>

            <div className="grid grid-cols-10 gap-2">
              {currentMock.questions.map((q, idx) => (
                <button
                  key={q.id}
                  onClick={() => setCurrentQuestionIndex(idx)}
                  className={`h-10 rounded-md border text-sm font-medium transition-colors ${
                    idx === currentQuestionIndex
                      ? "border-primary bg-primary text-primary-foreground"
                      : answers[q.id]?.trim()
                      ? "border-chart-2 bg-chart-2/10 text-chart-2"
                      : flaggedQuestions.has(idx)
                      ? "border-destructive bg-destructive/10 text-destructive"
                      : "hover-elevate"
                  }`}
                  data-testid={`question-nav-${idx}`}
                >
                  {idx + 1}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      <Dialog open={showSubmitDialog} onOpenChange={setShowSubmitDialog}>
        <DialogContent data-testid="dialog-submit">
          <DialogHeader>
            <DialogTitle>Submit Exam?</DialogTitle>
            <DialogDescription>
              You have answered {answeredCount} out of {currentMock.questions.length} questions.
              {flaggedQuestions.size > 0 && ` ${flaggedQuestions.size} questions are flagged for review.`}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Progress
              value={(answeredCount / currentMock.questions.length) * 100}
              className="h-2"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSubmitDialog(false)} data-testid="button-keep-working">
              Keep Working
            </Button>
            <Button data-testid="button-confirm-submit">Submit Now</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
