import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Layers, RotateCcw, Calendar, TrendingUp, AlertCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { queryClient } from "@/lib/queryClient";
import type { Flashcard } from "@shared/schema";

export default function Flashcards() {
  const [flipped, setFlipped] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const { toast } = useToast();

  const { data: dueCards = [], isLoading, error } = useQuery<Flashcard[]>({
    queryKey: ["/api/flashcards/due"],
  });

  const reviewMutation = useMutation({
    mutationFn: (data: { cardId: string; quality: string }) =>
      api.flashcards.review(data.cardId, data.quality),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/flashcards/due"] });
      setFlipped(false);
      if (currentIndex < dueCards.length - 1) {
        setCurrentIndex((prev) => prev + 1);
      } else {
        toast({
          title: "Session complete!",
          description: "All due flashcards reviewed",
        });
        setCurrentIndex(0);
      }
    },
  });

  const handleReview = (quality: "Again" | "Hard" | "Good" | "Easy") => {
    if (!currentCard) return;
    reviewMutation.mutate({ cardId: currentCard.id, quality });
  };

  const currentCard = dueCards[currentIndex];

  const getNextReviewText = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffDays > 0) return `in ${diffDays} day${diffDays > 1 ? "s" : ""}`;
    if (diffHours > 0) return `in ${diffHours} hour${diffHours > 1 ? "s" : ""}`;
    return "soon";
  };

  if (error) {
    return (
      <div className="mx-auto max-w-2xl space-y-8">
        <div>
          <h1 className="text-4xl font-bold">Flashcards</h1>
          <p className="mt-2 text-muted-foreground">
            Spaced repetition learning with SM-2 algorithm
          </p>
        </div>
        <Card>
          <CardContent className="py-12 text-center">
            <AlertCircle className="mx-auto h-12 w-12 text-destructive" />
            <h3 className="mt-4 text-lg font-medium">Error loading flashcards</h3>
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
      <div className="mx-auto max-w-2xl space-y-8">
        <div>
          <h1 className="text-4xl font-bold">Flashcards</h1>
          <p className="mt-2 text-muted-foreground">
            Spaced repetition learning with SM-2 algorithm
          </p>
        </div>
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-32" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-64 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div>
        <h1 className="text-4xl font-bold">Flashcards</h1>
        <p className="mt-2 text-muted-foreground">
          Spaced repetition learning with SM-2 algorithm
        </p>
      </div>

      {dueCards.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Layers className="mx-auto h-12 w-12 text-muted-foreground" />
            <h3 className="mt-4 text-lg font-medium">No cards due</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Generate flashcards from your study materials to start reviewing
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Review Session</CardTitle>
                  <CardDescription>
                    {currentIndex + 1} of {dueCards.length} cards
                  </CardDescription>
                </div>
                <Badge variant="outline">
                  {dueCards.length - currentIndex} remaining
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <Progress
                value={((currentIndex + 1) / dueCards.length) * 100}
                className="h-2"
              />
            </CardContent>
          </Card>

          <div
            className="perspective-1000 cursor-pointer"
            onClick={() => setFlipped(!flipped)}
            data-testid="flashcard-container"
          >
            <div
              className={`relative h-[400px] w-full transition-transform duration-500 transform-style-3d ${
                flipped ? "rotate-y-180" : ""
              }`}
              style={{
                transformStyle: "preserve-3d",
                transform: flipped ? "rotateY(180deg)" : "rotateY(0deg)",
              }}
            >
              <Card
                className="absolute inset-0 backface-hidden"
                data-testid="card-front"
              >
                <CardContent className="flex h-full flex-col items-center justify-center p-12 text-center">
                  <p className="text-sm font-medium text-muted-foreground mb-4">
                    Question
                  </p>
                  <p className="text-2xl font-medium leading-relaxed">
                    {currentCard?.front}
                  </p>
                  <p className="mt-8 text-sm text-muted-foreground">
                    Click to reveal answer
                  </p>
                </CardContent>
              </Card>

              <Card
                className="absolute inset-0 backface-hidden"
                style={{ transform: "rotateY(180deg)" }}
                data-testid="card-back"
              >
                <CardContent className="flex h-full flex-col items-center justify-center p-12 text-center">
                  <p className="text-sm font-medium text-muted-foreground mb-4">
                    Answer
                  </p>
                  <p className="text-xl leading-relaxed">
                    {currentCard?.back}
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>

          {flipped && (
            <div className="space-y-4">
              <p className="text-center text-sm text-muted-foreground">
                How well did you remember this?
              </p>
              <div className="grid grid-cols-4 gap-4">
                <Button
                  variant="outline"
                  onClick={() => handleReview("Again")}
                  disabled={reviewMutation.isPending}
                  data-testid="button-again"
                  className="flex-col h-auto py-4"
                >
                  <span className="text-lg font-semibold">Again</span>
                  <span className="text-xs text-muted-foreground mt-1">&lt;1m</span>
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleReview("Hard")}
                  disabled={reviewMutation.isPending}
                  data-testid="button-hard"
                  className="flex-col h-auto py-4"
                >
                  <span className="text-lg font-semibold">Hard</span>
                  <span className="text-xs text-muted-foreground mt-1">6m</span>
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleReview("Good")}
                  disabled={reviewMutation.isPending}
                  data-testid="button-good"
                  className="flex-col h-auto py-4"
                >
                  <span className="text-lg font-semibold">Good</span>
                  <span className="text-xs text-muted-foreground mt-1">1d</span>
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleReview("Easy")}
                  disabled={reviewMutation.isPending}
                  data-testid="button-easy"
                  className="flex-col h-auto py-4"
                >
                  <span className="text-lg font-semibold">Easy</span>
                  <span className="text-xs text-muted-foreground mt-1">4d</span>
                </Button>
              </div>
            </div>
          )}

          {currentCard && (
            <Card>
              <CardContent className="py-4">
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Easiness Factor</p>
                    <p className="font-medium">{currentCard.easinessFactor.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Interval</p>
                    <p className="font-medium">{currentCard.interval} days</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Repetitions</p>
                    <p className="font-medium">{currentCard.repetitions}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
