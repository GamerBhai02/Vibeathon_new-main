import { z } from "zod";

// User schema
export const userSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  name: z.string(),
  createdAt: z.string(),
});

export const insertUserSchema = userSchema.omit({ id: true, createdAt: true });
export type User = z.infer<typeof userSchema>;
export type InsertUser = z.infer<typeof insertUserSchema>;

// Corpus (uploaded documents)
export const corpusTypeSchema = z.enum(["PYQ", "TEACHER_NOTE", "MOCK_PAPER"]);
export const corpusSchema = z.object({
  id: z.string(),
  userId: z.string(),
  title: z.string(),
  type: corpusTypeSchema,
  path: z.string(),
  createdAt: z.string(),
});

export const insertCorpusSchema = corpusSchema.omit({ id: true, createdAt: true });
export type Corpus = z.infer<typeof corpusSchema>;
export type InsertCorpus = z.infer<typeof insertCorpusSchema>;

// Topic
export const topicSchema = z.object({
  id: z.string(),
  userId: z.string(),
  name: z.string(),
  importanceScore: z.number().min(0).max(10),
  masteryScore: z.number().min(0).max(100),
  summary: z.string().optional(),
});

export const insertTopicSchema = topicSchema.omit({ id: true });
export type Topic = z.infer<typeof topicSchema>;
export type InsertTopic = z.infer<typeof insertTopicSchema>;

// Study Plan
export const studyBlockSchema = z.object({
  id: z.string(),
  topicId: z.string(),
  topicName: z.string(),
  activity: z.enum(["learn", "practice", "mock", "review"]),
  duration: z.number(),
  scheduledFor: z.string(),
  completed: z.boolean(),
});

export const studyPlanSchema = z.object({
  id: z.string(),
  userId: z.string(),
  startDate: z.string(),
  endDate: z.string(),
  examType: z.string(),
  blocks: z.array(studyBlockSchema),
  weeklyGoal: z.string(),
});

export const insertStudyPlanSchema = studyPlanSchema.omit({ id: true });
export type StudyPlan = z.infer<typeof studyPlanSchema>;
export type InsertStudyPlan = z.infer<typeof insertStudyPlanSchema>;
export type StudyBlock = z.infer<typeof studyBlockSchema>;

// Practice Question
export const difficultySchema = z.enum(["easy", "medium", "hard"]);
export const practiceQuestionSchema = z.object({
  id: z.string(),
  userId: z.string(),
  topicId: z.string(),
  question: z.string(),
  hint: z.string().optional(),
  steps: z.array(z.string()),
  fullSolution: z.string(),
  rubric: z.string(),
  difficulty: difficultySchema,
  citations: z.array(z.string()),
  confidence: z.enum(["Low", "Med", "High"]),
});

export const insertPracticeQuestionSchema = practiceQuestionSchema.omit({ id: true });
export type PracticeQuestion = z.infer<typeof practiceQuestionSchema>;
export type InsertPracticeQuestion = z.infer<typeof insertPracticeQuestionSchema>;

// Mock Exam
export const examTypeSchema = z.enum(["CIE", "SEE", "LAB", "PLACEMENT"]);
export const mockQuestionSchema = z.object({
  id: z.string(),
  question: z.string(),
  marks: z.number(),
  rubric: z.string(),
  topicId: z.string(),
});

export const mockExamSchema = z.object({
  id: z.string(),
  userId: z.string(),
  type: examTypeSchema,
  title: z.string(),
  duration: z.number(),
  totalMarks: z.number(),
  questions: z.array(mockQuestionSchema),
  instructions: z.string(),
});

export const insertMockExamSchema = mockExamSchema.omit({ id: true });
export type MockExam = z.infer<typeof mockExamSchema>;
export type InsertMockExam = z.infer<typeof insertMockExamSchema>;
export type MockQuestion = z.infer<typeof mockQuestionSchema>;

// Attempt
export const answerSchema = z.object({
  questionId: z.string(),
  answer: z.string(),
  marksAwarded: z.number(),
  feedback: z.string(),
  flagged: z.boolean().optional(),
});

export const attemptSchema = z.object({
  id: z.string(),
  userId: z.string(),
  mockId: z.string(),
  score: z.number(),
  timeTakenSec: z.number(),
  answers: z.array(answerSchema),
  topicBreakdown: z.record(z.object({ scored: z.number(), total: z.number() })),
  createdAt: z.string(),
});

export const insertAttemptSchema = attemptSchema.omit({ id: true, createdAt: true });
export type Attempt = z.infer<typeof attemptSchema>;
export type InsertAttempt = z.infer<typeof insertAttemptSchema>;
export type Answer = z.infer<typeof answerSchema>;

// Flashcard (SM-2 algorithm)
export const flashcardSchema = z.object({
  id: z.string(),
  userId: z.string(),
  front: z.string(),
  back: z.string(),
  topicId: z.string(),
  nextReviewAt: z.string(),
  easinessFactor: z.number(),
  interval: z.number(),
  repetitions: z.number(),
});

export const insertFlashcardSchema = flashcardSchema.omit({ id: true });
export const reviewFlashcardSchema = z.object({
  cardId: z.string(),
  quality: z.enum(["Again", "Hard", "Good", "Easy"]),
});

export type Flashcard = z.infer<typeof flashcardSchema>;
export type InsertFlashcard = z.infer<typeof insertFlashcardSchema>;
export type ReviewFlashcard = z.infer<typeof reviewFlashcardSchema>;

// Placement Profile
export const interviewRoundSchema = z.object({
  name: z.string(),
  type: z.enum(["coding", "technical", "behavioral", "system_design"]),
  topics: z.array(z.string()),
  resources: z.array(z.object({ title: z.string(), url: z.string() })),
});

export const placementProfileSchema = z.object({
  id: z.string(),
  userId: z.string(),
  company: z.string(),
  role: z.string(),
  rounds: z.array(interviewRoundSchema),
  skills: z.array(z.string()),
  difficultyLevel: z.enum(["easy", "medium", "hard"]),
  mockMode: z.boolean(),
});

export const insertPlacementProfileSchema = placementProfileSchema.omit({ id: true });
export type PlacementProfile = z.infer<typeof placementProfileSchema>;
export type InsertPlacementProfile = z.infer<typeof insertPlacementProfileSchema>;
export type InterviewRound = z.infer<typeof interviewRoundSchema>;

// Agent Run
export const agentActionSchema = z.object({
  timestamp: z.string(),
  agent: z.string(),
  action: z.string(),
  tool: z.string().optional(),
  input: z.any().optional(),
  output: z.any().optional(),
});

export const agentReflectionSchema = z.object({
  timestamp: z.string(),
  agent: z.string(),
  reflection: z.string(),
  success: z.boolean(),
});

export const agentRunSchema = z.object({
  id: z.string(),
  userId: z.string(),
  goal: z.string(),
  plan: z.any(),
  actions: z.array(agentActionSchema),
  reflections: z.array(agentReflectionSchema),
  status: z.enum(["planning", "executing", "completed", "failed"]),
  createdAt: z.string(),
});

export const insertAgentRunSchema = agentRunSchema.omit({ id: true, createdAt: true });
export type AgentRun = z.infer<typeof agentRunSchema>;
export type InsertAgentRun = z.infer<typeof insertAgentRunSchema>;
export type AgentAction = z.infer<typeof agentActionSchema>;
export type AgentReflection = z.infer<typeof agentReflectionSchema>;

// Code execution (for placement mode)
export const codeExecutionSchema = z.object({
  language: z.string(),
  sourceCode: z.string(),
  stdin: z.string().optional(),
});

export const codeResultSchema = z.object({
  stdout: z.string().optional(),
  stderr: z.string().optional(),
  status: z.string(),
  time: z.string().optional(),
  memory: z.string().optional(),
});

export type CodeExecution = z.infer<typeof codeExecutionSchema>;
export type CodeResult = z.infer<typeof codeResultSchema>;

// API Request/Response types
export const magicLinkRequestSchema = z.object({
  email: z.string().email(),
});

export const generatePlanRequestSchema = z.object({
  examType: z.string(),
  deadline: z.string(),
  hoursPerDay: z.number().min(1).max(12),
});

export const generatePracticeRequestSchema = z.object({
  topicId: z.string(),
  difficulty: difficultySchema,
  count: z.number().min(1).max(10),
});

export const generateMockRequestSchema = z.object({
  examType: examTypeSchema,
  duration: z.number(),
  totalMarks: z.number(),
  topics: z.array(z.string()),
});

export const generateFlashcardsRequestSchema = z.object({
  sourceType: z.enum(["corpus", "topic"]),
  sourceId: z.string(),
  count: z.number().min(5).max(50),
});

export const startAttemptRequestSchema = z.object({
  mockId: z.string(),
});

export const submitAttemptRequestSchema = z.object({
  mockId: z.string(),
  answers: z.array(answerSchema),
  timeTakenSec: z.number(),
});

export const agentRunRequestSchema = z.object({
  goal: z.string(),
});

export type MagicLinkRequest = z.infer<typeof magicLinkRequestSchema>;
export type GeneratePlanRequest = z.infer<typeof generatePlanRequestSchema>;
export type GeneratePracticeRequest = z.infer<typeof generatePracticeRequestSchema>;
export type GenerateMockRequest = z.infer<typeof generateMockRequestSchema>;
export type GenerateFlashcardsRequest = z.infer<typeof generateFlashcardsRequestSchema>;
export type StartAttemptRequest = z.infer<typeof startAttemptRequestSchema>;
export type SubmitAttemptRequest = z.infer<typeof submitAttemptRequestSchema>;
export type AgentRunRequest = z.infer<typeof agentRunRequestSchema>;
