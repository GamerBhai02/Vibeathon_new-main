import { randomUUID } from "crypto";
import type {
  User,
  InsertUser,
  Corpus,
  InsertCorpus,
  Topic,
  InsertTopic,
  StudyPlan,
  InsertStudyPlan,
  PracticeQuestion,
  InsertPracticeQuestion,
  MockExam,
  InsertMockExam,
  Attempt,
  InsertAttempt,
  Flashcard,
  InsertFlashcard,
  PlacementProfile,
  InsertPlacementProfile,
  AgentRun,
  InsertAgentRun,
} from "@shared/schema";

export interface IStorage {
  // Users
  getUser(id: string): Promise<User | undefined>;
  getUserByEmail(email: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;

  // Corpus
  createCorpus(corpus: InsertCorpus): Promise<Corpus>;
  getCorpusByUserId(userId: string): Promise<Corpus[]>;

  // Topics
  createTopic(topic: InsertTopic): Promise<Topic>;
  getTopicsByUserId(userId: string): Promise<Topic[]>;
  deleteTopicsByUserId(userId: string): Promise<void>;
  updateTopicMastery(topicId: string, masteryScore: number): Promise<void>;

  // Study Plans
  createStudyPlan(plan: InsertStudyPlan): Promise<StudyPlan>;
  getStudyPlanByUserId(userId: string): Promise<StudyPlan | undefined>;
  updateStudyPlan(planId: string, plan: Partial<StudyPlan>): Promise<void>;

  // Practice Questions
  createPracticeQuestion(question: InsertPracticeQuestion): Promise<PracticeQuestion>;
  getPracticeQuestionsByUserId(userId: string): Promise<PracticeQuestion[]>;
  getPracticeQuestionsByTopic(topicId: string): Promise<PracticeQuestion[]>;

  // Mock Exams
  createMockExam(exam: InsertMockExam): Promise<MockExam>;
  getMockExamsByUserId(userId: string): Promise<MockExam[]>;
  getMockExam(examId: string): Promise<MockExam | undefined>;

  // Attempts
  createAttempt(attempt: InsertAttempt): Promise<Attempt>;
  getAttemptsByUserId(userId: string): Promise<Attempt[]>;
  getAttemptsByMockId(mockId: string): Promise<Attempt[]>;

  // Flashcards
  createFlashcard(card: InsertFlashcard): Promise<Flashcard>;
  getFlashcardsByUserId(userId: string): Promise<Flashcard[]>;
  getDueFlashcards(userId: string): Promise<Flashcard[]>;
  updateFlashcard(cardId: string, updates: Partial<Flashcard>): Promise<void>;

  // Placement Profiles
  createPlacementProfile(profile: InsertPlacementProfile): Promise<PlacementProfile>;
  getPlacementProfilesByUserId(userId: string): Promise<PlacementProfile[]>;

  // Agent Runs
  createAgentRun(run: InsertAgentRun): Promise<AgentRun>;
  getAgentRunsByUserId(userId: string): Promise<AgentRun[]>;
  updateAgentRun(runId: string, updates: Partial<AgentRun>): Promise<void>;
}

export class MemStorage implements IStorage {
  private users: Map<string, User>;
  private corpus: Map<string, Corpus>;
  private topics: Map<string, Topic>;
  private studyPlans: Map<string, StudyPlan>;
  private practiceQuestions: Map<string, PracticeQuestion>;
  private mockExams: Map<string, MockExam>;
  private attempts: Map<string, Attempt>;
  private flashcards: Map<string, Flashcard>;
  private placementProfiles: Map<string, PlacementProfile>;
  private agentRuns: Map<string, AgentRun>;

  constructor() {
    this.users = new Map();
    this.corpus = new Map();
    this.topics = new Map();
    this.studyPlans = new Map();
    this.practiceQuestions = new Map();
    this.mockExams = new Map();
    this.attempts = new Map();
    this.flashcards = new Map();
    this.placementProfiles = new Map();
    this.agentRuns = new Map();
  }

  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByEmail(email: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find((user) => user.email === email);
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = { ...insertUser, id, createdAt: new Date().toISOString() };
    this.users.set(id, user);
    return user;
  }

  async createCorpus(insertCorpus: InsertCorpus): Promise<Corpus> {
    const id = randomUUID();
    const corpus: Corpus = { ...insertCorpus, id, createdAt: new Date().toISOString() };
    this.corpus.set(id, corpus);
    return corpus;
  }

  async getCorpusByUserId(userId: string): Promise<Corpus[]> {
    return Array.from(this.corpus.values()).filter((c) => c.userId === userId);
  }

  async createTopic(insertTopic: InsertTopic): Promise<Topic> {
    const id = randomUUID();
    const topic: Topic = { ...insertTopic, id };
    this.topics.set(id, topic);
    return topic;
  }

  async getTopicsByUserId(userId: string): Promise<Topic[]> {
    return Array.from(this.topics.values()).filter((t) => t.userId === userId);
  }

  async deleteTopicsByUserId(userId: string): Promise<void> {
    const topicsToDelete = Array.from(this.topics.values()).filter((t) => t.userId === userId);
    for (const topic of topicsToDelete) {
      this.topics.delete(topic.id);
    }
  }

  async updateTopicMastery(topicId: string, masteryScore: number): Promise<void> {
    const topic = this.topics.get(topicId);
    if (topic) {
      topic.masteryScore = masteryScore;
      this.topics.set(topicId, topic);
    }
  }

  async createStudyPlan(insertPlan: InsertStudyPlan): Promise<StudyPlan> {
    const id = randomUUID();
    const plan: StudyPlan = { ...insertPlan, id };
    this.studyPlans.set(id, plan);
    return plan;
  }

  async getStudyPlanByUserId(userId: string): Promise<StudyPlan | undefined> {
    return Array.from(this.studyPlans.values()).find((p) => p.userId === userId);
  }

  async updateStudyPlan(planId: string, updates: Partial<StudyPlan>): Promise<void> {
    const plan = this.studyPlans.get(planId);
    if (plan) {
      Object.assign(plan, updates);
      this.studyPlans.set(planId, plan);
    }
  }

  async createPracticeQuestion(insertQuestion: InsertPracticeQuestion): Promise<PracticeQuestion> {
    const id = randomUUID();
    const question: PracticeQuestion = { ...insertQuestion, id };
    this.practiceQuestions.set(id, question);
    return question;
  }

  async getPracticeQuestionsByUserId(userId: string): Promise<PracticeQuestion[]> {
    return Array.from(this.practiceQuestions.values()).filter((q) => q.userId === userId);
  }

  async getPracticeQuestionsByTopic(topicId: string): Promise<PracticeQuestion[]> {
    return Array.from(this.practiceQuestions.values()).filter((q) => q.topicId === topicId);
  }

  async createMockExam(insertExam: InsertMockExam): Promise<MockExam> {
    const id = randomUUID();
    const exam: MockExam = { ...insertExam, id };
    this.mockExams.set(id, exam);
    return exam;
  }

  async getMockExamsByUserId(userId: string): Promise<MockExam[]> {
    return Array.from(this.mockExams.values()).filter((e) => e.userId === userId);
  }

  async getMockExam(examId: string): Promise<MockExam | undefined> {
    return this.mockExams.get(examId);
  }

  async createAttempt(insertAttempt: InsertAttempt): Promise<Attempt> {
    const id = randomUUID();
    const attempt: Attempt = { ...insertAttempt, id, createdAt: new Date().toISOString() };
    this.attempts.set(id, attempt);
    return attempt;
  }

  async getAttemptsByUserId(userId: string): Promise<Attempt[]> {
    return Array.from(this.attempts.values()).filter((a) => a.userId === userId);
  }

  async getAttemptsByMockId(mockId: string): Promise<Attempt[]> {
    return Array.from(this.attempts.values()).filter((a) => a.mockId === mockId);
  }

  async createFlashcard(insertCard: InsertFlashcard): Promise<Flashcard> {
    const id = randomUUID();
    const card: Flashcard = { ...insertCard, id };
    this.flashcards.set(id, card);
    return card;
  }

  async getFlashcardsByUserId(userId: string): Promise<Flashcard[]> {
    return Array.from(this.flashcards.values()).filter((c) => c.userId === userId);
  }

  async getDueFlashcards(userId: string): Promise<Flashcard[]> {
    const now = new Date();
    return Array.from(this.flashcards.values()).filter(
      (c) => c.userId === userId && new Date(c.nextReviewAt) <= now
    );
  }

  async updateFlashcard(cardId: string, updates: Partial<Flashcard>): Promise<void> {
    const card = this.flashcards.get(cardId);
    if (card) {
      Object.assign(card, updates);
      this.flashcards.set(cardId, card);
    }
  }

  async createPlacementProfile(insertProfile: InsertPlacementProfile): Promise<PlacementProfile> {
    const id = randomUUID();
    const profile: PlacementProfile = { ...insertProfile, id };
    this.placementProfiles.set(id, profile);
    return profile;
  }

  async getPlacementProfilesByUserId(userId: string): Promise<PlacementProfile[]> {
    return Array.from(this.placementProfiles.values()).filter((p) => p.userId === userId);
  }

  async createAgentRun(insertRun: InsertAgentRun): Promise<AgentRun> {
    const id = randomUUID();
    const run: AgentRun = { ...insertRun, id, createdAt: new Date().toISOString() };
    this.agentRuns.set(id, run);
    return run;
  }

  async getAgentRunsByUserId(userId: string): Promise<AgentRun[]> {
    return Array.from(this.agentRuns.values()).filter((r) => r.userId === userId);
  }

  async updateAgentRun(runId: string, updates: Partial<AgentRun>): Promise<void> {
    const run = this.agentRuns.get(runId);
    if (run) {
      Object.assign(run, updates);
      this.agentRuns.set(runId, run);
    }
  }
}

export const storage = new MemStorage();
