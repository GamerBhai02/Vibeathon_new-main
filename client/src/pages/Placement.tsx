import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Briefcase, Play, Code, CheckCircle, XCircle, Loader2, AlertCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { queryClient } from "@/lib/queryClient";
import type { PlacementProfile, CodeResult } from "@shared/schema";

export default function Placement() {
  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [language, setLanguage] = useState("python");
  const [code, setCode] = useState(`def solution(arr):\n    # Write your solution here\n    pass`);
  const [stdin, setStdin] = useState("");
  const [result, setResult] = useState<CodeResult | null>(null);
  const { toast } = useToast();

  const { data: profiles = [], isLoading, error } = useQuery<PlacementProfile[]>({
    queryKey: ["/api/placement/list"],
  });

  const createProfileMutation = useMutation({
    mutationFn: (data: { company: string; role: string }) =>
      api.placement.createProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/placement/list"] });
      toast({
        title: "Profile created",
        description: "Company profile and prep materials ready",
      });
      setCompany("");
      setRole("");
    },
  });

  const executeCodeMutation = useMutation({
    mutationFn: (data: { language: string; sourceCode: string; stdin?: string }) =>
      api.code.execute(data),
    onSuccess: (data) => {
      setResult(data);
    },
  });

  const handleCreateProfile = (e: React.FormEvent) => {
    e.preventDefault();
    if (!company || !role) return;
    createProfileMutation.mutate({ company, role });
  };

  const handleRunCode = () => {
    executeCodeMutation.mutate({
      language,
      sourceCode: code,
      stdin,
    });
  };

  const currentProfile = profiles[0];

  if (error) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-4xl font-bold">Placement Preparation</h1>
          <p className="mt-2 text-muted-foreground">
            Company-specific interview prep with coding practice
          </p>
        </div>
        <Card>
          <CardContent className="py-12 text-center">
            <AlertCircle className="mx-auto h-12 w-12 text-destructive" />
            <h3 className="mt-4 text-lg font-medium">Error loading profiles</h3>
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
      <div className="space-y-8">
        <div>
          <h1 className="text-4xl font-bold">Placement Preparation</h1>
          <p className="mt-2 text-muted-foreground">
            Company-specific interview prep with coding practice
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
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold">Placement Preparation</h1>
        <p className="mt-2 text-muted-foreground">
          Company-specific interview prep with coding practice
        </p>
      </div>

      {!currentProfile && (
        <Card>
          <CardHeader>
            <CardTitle>Create Placement Profile</CardTitle>
            <CardDescription>
              Enter company and role to get tailored preparation materials
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCreateProfile} className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="company">Company</Label>
                  <Input
                    id="company"
                    placeholder="e.g. Google, Amazon"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    data-testid="input-company"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="role">Role</Label>
                  <Input
                    id="role"
                    placeholder="e.g. Software Engineer"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    data-testid="input-role"
                  />
                </div>
              </div>
              <Button
                type="submit"
                disabled={createProfileMutation.isPending}
                data-testid="button-create-profile"
              >
                {createProfileMutation.isPending ? "Creating..." : "Create Profile"}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {currentProfile && (
        <div className="space-y-6">
          <Card data-testid="card-profile">
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <CardTitle className="text-2xl">{currentProfile.company}</CardTitle>
                  <CardDescription className="text-base">{currentProfile.role}</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Badge
                    variant={currentProfile.mockMode ? "secondary" : "default"}
                  >
                    {currentProfile.mockMode ? "Mock Data" : "Live Data"}
                  </Badge>
                  <Badge variant="outline">{currentProfile.difficultyLevel}</Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="mb-2 font-medium">Required Skills</h4>
                <div className="flex flex-wrap gap-2">
                  {currentProfile.skills.map((skill) => (
                    <Badge key={skill} variant="secondary">
                      {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Interview Rounds</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="0" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  {currentProfile.rounds.map((round, idx) => (
                    <TabsTrigger key={idx} value={idx.toString()} data-testid={`tab-round-${idx}`}>
                      {round.name}
                    </TabsTrigger>
                  ))}
                </TabsList>
                {currentProfile.rounds.map((round, idx) => (
                  <TabsContent key={idx} value={idx.toString()} className="space-y-4">
                    <div>
                      <Badge>{round.type}</Badge>
                      <h3 className="mt-3 text-lg font-semibold">{round.name}</h3>
                      <div className="mt-4 space-y-2">
                        <h4 className="text-sm font-medium">Topics</h4>
                        <div className="flex flex-wrap gap-2">
                          {round.topics.map((topic) => (
                            <Badge key={topic} variant="outline">
                              {topic}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      {round.resources.length > 0 && (
                        <div className="mt-4 space-y-2">
                          <h4 className="text-sm font-medium">Resources</h4>
                          <div className="space-y-2">
                            {round.resources.map((resource, ridx) => (
                              <a
                                key={ridx}
                                href={resource.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block rounded-md border p-3 text-sm hover-elevate"
                                data-testid={`link-resource-${ridx}`}
                              >
                                {resource.title}
                              </a>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </TabsContent>
                ))}
              </Tabs>
            </CardContent>
          </Card>

          <Card data-testid="card-code-editor">
            <CardHeader>
              <CardTitle>Coding Practice</CardTitle>
              <CardDescription>
                Test your solutions with the code runner
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-4">
                <Select value={language} onValueChange={setLanguage}>
                  <SelectTrigger className="w-[150px]" data-testid="select-language">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="python">Python</SelectItem>
                    <SelectItem value="javascript">JavaScript</SelectItem>
                    <SelectItem value="java">Java</SelectItem>
                    <SelectItem value="cpp">C++</SelectItem>
                  </SelectContent>
                </Select>
                <Button
                  onClick={handleRunCode}
                  disabled={executeCodeMutation.isPending}
                  data-testid="button-run-code"
                >
                  {executeCodeMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Running...
                    </>
                  ) : (
                    <>
                      <Play className="mr-2 h-4 w-4" />
                      Run Code
                    </>
                  )}
                </Button>
              </div>

              <div className="grid gap-4 lg:grid-cols-2">
                <div className="space-y-2">
                  <Label>Code</Label>
                  <Textarea
                    className="min-h-[300px] font-mono text-sm"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    data-testid="textarea-code"
                  />
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Input (stdin)</Label>
                    <Textarea
                      className="min-h-[100px] font-mono text-sm"
                      placeholder="Enter input here..."
                      value={stdin}
                      onChange={(e) => setStdin(e.target.value)}
                      data-testid="textarea-stdin"
                    />
                  </div>

                  {result && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label>Output</Label>
                        {result.status === "Accepted" ? (
                          <Badge className="gap-1">
                            <CheckCircle className="h-3 w-3" />
                            Accepted
                          </Badge>
                        ) : (
                          <Badge variant="destructive" className="gap-1">
                            <XCircle className="h-3 w-3" />
                            {result.status}
                          </Badge>
                        )}
                      </div>
                      <div className="rounded-md bg-muted p-4 font-mono text-sm" data-testid="text-output">
                        {result.stdout && <div className="whitespace-pre-wrap">{result.stdout}</div>}
                        {result.stderr && (
                          <div className="text-destructive whitespace-pre-wrap">{result.stderr}</div>
                        )}
                        {result.time && (
                          <div className="mt-2 text-xs text-muted-foreground">
                            Time: {result.time} | Memory: {result.memory}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
