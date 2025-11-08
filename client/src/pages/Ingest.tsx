import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Upload, FileText, Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { queryClient } from "@/lib/queryClient";
import type { Corpus, Topic } from "@shared/schema";

export default function Ingest() {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const { toast } = useToast();

  const { data: topics = [], isLoading, error } = useQuery<Topic[]>({
    queryKey: ["/api/topics"],
  });

  const uploadMutation = useMutation({
    mutationFn: async (files: FileList) => {
      const formData = new FormData();
      Array.from(files).forEach((file) => {
        formData.append("files", file);
      });
      return api.ingest.upload(formData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/topics"] });
      toast({
        title: "Upload complete",
        description: "Documents processed and topics extracted",
      });
      setUploading(false);
      setUploadProgress(0);
    },
    onError: () => {
      toast({
        title: "Upload failed",
        description: "Please try again",
        variant: "destructive",
      });
      setUploading(false);
      setUploadProgress(0);
    },
  });

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    setUploadProgress(0);

    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 90) {
          clearInterval(interval);
          return prev;
        }
        return prev + 10;
      });
    }, 200);

    uploadMutation.mutate(files);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length === 0) return;

    const input = document.createElement("input");
    input.type = "file";
    input.files = files;
    const event = new Event("change", { bubbles: true });
    Object.defineProperty(event, "target", { writable: false, value: input });
    handleFileSelect(event as any);
  };

  if (error) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-4xl font-bold">Document Ingestion</h1>
          <p className="mt-2 text-muted-foreground">
            Upload PYQs, teacher notes, and mock papers for AI-powered analysis
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

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold">Document Ingestion</h1>
        <p className="mt-2 text-muted-foreground">
          Upload PYQs, teacher notes, and mock papers for AI-powered analysis
        </p>
      </div>

      <Card data-testid="card-upload">
        <CardHeader>
          <CardTitle>Upload Documents</CardTitle>
          <CardDescription>
            Supports PDF and image files. OCR will extract text automatically.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            className="rounded-md border-2 border-dashed border-muted-foreground/25 p-12 text-center hover-elevate cursor-pointer transition-colors hover:border-primary/50"
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => document.getElementById("file-input")?.click()}
            data-testid="dropzone-upload"
          >
            <input
              id="file-input"
              type="file"
              multiple
              accept=".pdf,.png,.jpg,.jpeg"
              className="hidden"
              onChange={handleFileSelect}
              data-testid="input-file"
            />
            
            {uploading ? (
              <div className="space-y-4">
                <Loader2 className="mx-auto h-12 w-12 animate-spin text-primary" />
                <p className="text-sm font-medium">Processing documents...</p>
                <Progress value={uploadProgress} className="mx-auto w-64" />
              </div>
            ) : (
              <>
                <Upload className="mx-auto h-12 w-12 text-muted-foreground" />
                <p className="mt-4 text-sm font-medium">
                  Drop files here or click to browse
                </p>
                <p className="mt-2 text-sm text-muted-foreground">
                  PDF, PNG, JPG up to 10MB each
                </p>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {isLoading ? (
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-40" />
            <Skeleton className="h-4 w-64" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </CardContent>
        </Card>
      ) : topics.length > 0 && (
        <Card data-testid="card-topics">
          <CardHeader>
            <CardTitle>Extracted Topics</CardTitle>
            <CardDescription>
              Topics identified from your uploaded documents
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topics.map((topic) => (
                <div
                  key={topic.id}
                  className="flex items-center justify-between rounded-md border p-4"
                  data-testid={`topic-${topic.id}`}
                >
                  <div className="flex items-center gap-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 text-primary">
                      <FileText className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="font-medium">{topic.name}</p>
                      <div className="mt-1 flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">
                          Importance: {topic.importanceScore}/10
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          Mastery: {topic.masteryScore}%
                        </Badge>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {topic.masteryScore >= 70 ? (
                      <CheckCircle2 className="h-5 w-5 text-chart-2" />
                    ) : topic.masteryScore >= 40 ? (
                      <AlertCircle className="h-5 w-5 text-chart-3" />
                    ) : (
                      <AlertCircle className="h-5 w-5 text-destructive" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {topics.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <FileText className="mx-auto h-12 w-12 text-muted-foreground" />
            <h3 className="mt-4 text-lg font-medium">No topics yet</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Upload your first document to get started with AI-powered topic extraction
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
