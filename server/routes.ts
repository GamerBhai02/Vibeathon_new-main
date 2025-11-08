import type { Express } from "express";
import { createServer, type Server } from "http";
import jwt from "jsonwebtoken";
import { storage } from "./storage";
import type { User } from "@shared/schema";
import multer from 'multer';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

const uploadDir = 'uploads';
fs.mkdirSync(uploadDir, { recursive: true });

const multerStorage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, uploadDir)
    },
    filename: function (req, file, cb) {
        cb(null, file.originalname)
    }
})

const upload = multer({ storage: multerStorage });

const JWT_SECRET = process.env.JWT_SECRET || "dev-secret-change-in-production";

// Middleware to verify JWT
function authenticateToken(req: any, res: any, next: any) {
  const authHeader = req.headers["authorization"];
  const token = authHeader && authHeader.split(" ")[1];

  if (!token) {
    return res.status(401).json({ error: "No token provided" });
  }

  jwt.verify(token, JWT_SECRET, (err: any, user: any) => {
    if (err) return res.status(403).json({ error: "Invalid token" });
    req.user = user;
    next();
  });
}

export async function registerRoutes(app: Express): Promise<Server> {
  // Health check endpoint
  app.get("/api/health", (req, res) => {
    res.json({
      status: "healthy",
      service: "vibeathon-nodejs-backend",
      version: "1.0.0",
      timestamp: new Date().toISOString()
    });
  });

  // Auth routes
  app.post("/api/auth/login", async (req, res) => {
    try {
      const { email } = req.body;
      
      let user = await storage.getUserByEmail(email);
      
      if (!user) {
        user = await storage.createUser({
          email,
          name: email.split("@")[0],
        });
      }

      const token = jwt.sign({ id: user.id, email: user.email }, JWT_SECRET, {
        expiresIn: "7d",
      });

      res.json({ token, user });
    } catch (error) {
      res.status(500).json({ error: "Failed to process magic link" });
    }
  });

  app.get("/api/auth/me", authenticateToken, async (req: any, res) => {
    try {
      const user = await storage.getUser(req.user.id);
      if (!user) {
        return res.status(404).json({ error: "User not found" });
      }
      res.json(user);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch user" });
    }
  });

  // Topics
  app.get("/api/topics", authenticateToken, async (req: any, res) => {
    try {
      const topics = await storage.getTopicsByUserId(req.user.id);
      res.json(topics);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch topics" });
    }
  });

  // Study Plan
  app.get("/api/plan", authenticateToken, async (req: any, res) => {
    try {
      const plan = await storage.getStudyPlanByUserId(req.user.id);
      res.json(plan || null);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch study plan" });
    }
  });

  app.post("/api/plan/generate", authenticateToken, async (req: any, res) => {
    try {
      const { examType, deadline, hoursPerDay } = req.body;
      
      // Mock plan generation for now
      const plan = await storage.createStudyPlan({
        userId: req.user.id,
        startDate: new Date().toISOString(),
        endDate: deadline,
        examType,
        blocks: [],
        weeklyGoal: `Study ${hoursPerDay * 7} hours per week`,
      });

      res.json(plan);
    } catch (error) {
      res.status(500).json({ error: "Failed to generate study plan" });
    }
  });

  // Mock Exams
  app.get("/api/mock/list", authenticateToken, async (req: any, res) => {
    try {
      const mocks = await storage.getMockExamsByUserId(req.user.id);
      res.json(mocks);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch mock exams" });
    }
  });

  // Flashcards
  app.get("/api/flashcards/due", authenticateToken, async (req: any, res) => {
    try {
      const cards = await storage.getDueFlashcards(req.user.id);
      res.json(cards);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch flashcards" });
    }
  });

  app.post("/api/flashcards/review", authenticateToken, async (req: any, res) => {
    try {
      const { cardId, quality } = req.body;
      
      // SM-2 algorithm implementation
      const card = await storage.getFlashcardsByUserId(req.user.id).then(cards => 
        cards.find(c => c.id === cardId)
      );
      
      if (!card) {
        return res.status(404).json({ error: "Card not found" });
      }

      let { easinessFactor, interval, repetitions } = card;
      
      // Quality mapping: Again=0, Hard=3, Good=4, Easy=5
      const qualityMap: Record<string, number> = {
        Again: 0,
        Hard: 3,
        Good: 4,
        Easy: 5,
      };
      
      const q = qualityMap[quality] || 4;
      
      if (q >= 3) {
        if (repetitions === 0) {
          interval = 1;
        } else if (repetitions === 1) {
          interval = 6;
        } else {
          interval = Math.round(interval * easinessFactor);
        }
        repetitions += 1;
      } else {
        repetitions = 0;
        interval = 1;
      }
      
      easinessFactor = Math.max(1.3, easinessFactor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)));
      
      const nextReviewAt = new Date();
      nextReviewAt.setDate(nextReviewAt.getDate() + interval);
      
      await storage.updateFlashcard(cardId, {
        easinessFactor,
        interval,
        repetitions,
        nextReviewAt: nextReviewAt.toISOString(),
      });

      res.json({ success: true });
    } catch (error) {
      res.status(500).json({ error: "Failed to review flashcard" });
    }
  });

  // Placement
  app.get("/api/placement/list", authenticateToken, async (req: any, res) => {
    try {
      const profiles = await storage.getPlacementProfilesByUserId(req.user.id);
      res.json(profiles);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch placement profiles" });
    }
  });

  app.post("/api/placement/profile", authenticateToken, async (req: any, res) => {
    try {
      const { company, role } = req.body;
      
      // Mock profile creation
      const profile = await storage.createPlacementProfile({
        userId: req.user.id,
        company,
        role,
        rounds: [
          {
            name: "Online Assessment",
            type: "coding",
            topics: ["Arrays", "Strings", "Dynamic Programming"],
            resources: [{ title: "LeetCode Practice", url: "https://leetcode.com" }],
          },
          {
            name: "Technical Round 1",
            type: "coding",
            topics: ["Data Structures", "Algorithms", "System Design Basics"],
            resources: [],
          },
          {
            name: "Technical Round 2",
            type: "system_design",
            topics: ["Scalability", "Database Design", "API Design"],
            resources: [],
          },
          {
            name: "HR Round",
            type: "behavioral",
            topics: ["Cultural Fit", "Past Experiences", "Career Goals"],
            resources: [],
          },
        ],
        skills: ["JavaScript", "Python", "React", "Node.js", "Algorithms"],
        difficultyLevel: "medium",
        mockMode: true,
      });

      res.json(profile);
    } catch (error) {
      res.status(500).json({ error: "Failed to create placement profile" });
    }
  });

  // Code execution
  app.post("/api/code/execute", authenticateToken, async (req: any, res) => {
    try {
      const { language, sourceCode, stdin } = req.body;
      
      // Mock code execution (will integrate Judge0 in backend implementation)
      res.json({
        stdout: "42\n",
        stderr: "",
        status: "Accepted",
        time: "0.123s",
        memory: "5.2MB",
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to execute code" });
    }
  });

  // Practice questions
  app.post("/api/practice/generate", authenticateToken, async (req: any, res) => {
    try {
      const { topicId, difficulty, count } = req.body;
      
      const questions = await storage.getPracticeQuestionsByTopic(topicId);
      res.json(questions.slice(0, count || 5));
    } catch (error) {
      res.status(500).json({ error: "Failed to generate practice questions" });
    }
  });

  app.get("/api/practice", authenticateToken, async (req: any, res) => {
    try {
      const questions = await storage.getPracticeQuestionsByUserId(req.user.id);
      res.json(questions);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch practice questions" });
    }
  });

  // Mock exam generation
  app.post("/api/mock/generate", authenticateToken, async (req: any, res) => {
    try {
      const { examType, duration, totalMarks, topics } = req.body;
      
      const mockExam = await storage.createMockExam({
        userId: req.user.id,
        type: examType,
        title: `${examType} Mock Exam`,
        duration,
        totalMarks,
        questions: [],
        instructions: "Answer all questions within the time limit.",
      });

      res.json(mockExam);
    } catch (error) {
      res.status(500).json({ error: "Failed to generate mock exam" });
    }
  });

  app.post("/api/mock/attempt/start", authenticateToken, async (req: any, res) => {
    try {
      const { mockId } = req.body;
      const exam = await storage.getMockExam(mockId);
      
      if (!exam) {
        return res.status(404).json({ error: "Mock exam not found" });
      }

      res.json(exam);
    } catch (error) {
      res.status(500).json({ error: "Failed to start attempt" });
    }
  });

  app.post("/api/mock/attempt/submit", authenticateToken, async (req: any, res) => {
    try {
      const { mockId, answers, timeTakenSec } = req.body;
      
      // Mock grading - calculate score
      const totalAnswered = answers.filter((a: any) => a.answer?.trim()).length;
      const score = Math.round((totalAnswered / answers.length) * 100);

      const attempt = await storage.createAttempt({
        userId: req.user.id,
        mockId,
        score,
        timeTakenSec,
        answers: answers.map((a: any) => ({
          questionId: a.questionId,
          answer: a.answer,
          marksAwarded: a.answer?.trim() ? 8 : 0,
          feedback: a.answer?.trim() ? "Good attempt" : "No answer provided",
        })),
        topicBreakdown: {},
      });

      res.json(attempt);
    } catch (error) {
      res.status(500).json({ error: "Failed to submit attempt" });
    }
  });

  // Flashcard generation
  app.post("/api/flashcards/generate", authenticateToken, async (req: any, res) => {
    try {
      const { sourceType, sourceId, count } = req.body;
      
      // Mock flashcard generation
      const flashcards = [];
      for (let i = 0; i < count; i++) {
        const nextReview = new Date();
        nextReview.setDate(nextReview.getDate() + 1);
        
        const card = await storage.createFlashcard({
          userId: req.user.id,
          topicId: sourceId,
          front: `Question ${i + 1}`,
          back: `Answer ${i + 1}`,
          nextReviewAt: nextReview.toISOString(),
          easinessFactor: 2.5,
          interval: 1,
          repetitions: 0,
        });
        flashcards.push(card);
      }

      res.json(flashcards);
    } catch (error) {
      res.status(500).json({ error: "Failed to generate flashcards" });
    }
  });

  // YouTube suggestions
  app.get("/api/youtube/suggest", authenticateToken, async (req: any, res) => {
    try {
      const topic = req.query.topic as string;
      
      // Mock YouTube suggestions
      res.json([
        {
          title: `${topic} Tutorial - Complete Guide`,
          url: `https://youtube.com/watch?v=mock1`,
          thumbnail: "https://via.placeholder.com/320x180",
          channel: "Tech Education",
        },
        {
          title: `${topic} Explained in 10 Minutes`,
          url: `https://youtube.com/watch?v=mock2`,
          thumbnail: "https://via.placeholder.com/320x180",
          channel: "Quick Learning",
        },
      ]);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch YouTube suggestions" });
    }
  });

  // Ingest (file upload)
  app.post("/api/ingest", authenticateToken, upload.array('files'), async (req: any, res) => {
    try {
        if (!req.files || req.files.length === 0) {
            return res.status(400).json({ error: "No files were uploaded." });
        }

        await storage.deleteTopicsByUserId(req.user.id);

        const topics = [];
        for (const file of req.files) {
            const pythonExecutable = process.platform === 'win32'
                ? path.resolve('pdfExtraction', '.venv', 'Scripts', 'python.exe')
                : path.resolve('pdfExtraction', '.venv', 'bin', 'python3');
            const pythonProcess = spawn(pythonExecutable, ['pdfExtraction/main.py', file.path, '--mime_type', file.mimetype], {
                env: {
                    ...process.env,
                    GEMINI_API_KEY: process.env.GEMINI_API_KEY || ''
                }
            });

            let pythonOutput = '';
            for await (const chunk of pythonProcess.stdout) {
                pythonOutput += chunk;
            }

            let pythonError = '';
            for await (const chunk of pythonProcess.stderr) {
                pythonError += chunk;
            }

            const exitCode = await new Promise((resolve) => {
                pythonProcess.on('close', resolve);
            });

            console.log('Python script output:', pythonOutput);
            console.error('Python script error:', pythonError);
            console.log('Python script exit code:', exitCode);

            if (exitCode !== 0) {
                console.error(`Python script exited with code ${exitCode}: ${pythonError}`);
                // continue to next file
                continue;
            }

            const extractedTopics = JSON.parse(pythonOutput);

            for (const topic of extractedTopics) {
                const newTopic = await storage.createTopic({
                    userId: req.user.id,
                    name: topic.topic,
                    importanceScore: 5, // Default importance
                    masteryScore: 0, // Default mastery
                    summary: topic.content,
                });
                topics.push(newTopic);
            }

            // Clean up the uploaded file
            fs.unlinkSync(file.path);
        }

        res.json({ success: true, topicsExtracted: topics.length });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: "Failed to process upload" });
    }
  });

  // Agent run (SSE endpoint)
  app.get("/api/agent/run", authenticateToken, async (req: any, res) => {
    try {
      const { goal } = req.query;
      
      res.setHeader("Content-Type", "text/event-stream");
      res.setHeader("Cache-Control", "no-cache");
      res.setHeader("Connection", "keep-alive");

      // Mock agent streaming
      const events = [
        { type: "plan", agent: "PlannerAgent", content: "Analyzing study requirements..." },
        { type: "action", agent: "PlannerAgent", content: "Creating personalized study schedule" },
        { type: "reflection", agent: "PlannerAgent", content: "Plan created successfully" },
        { type: "action", agent: "TeacherAgent", content: "Generating micro-lessons" },
        { type: "complete", status: "success" },
      ];

      for (const event of events) {
        res.write(`data: ${JSON.stringify(event)}\n\n`);
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }

      res.end();
    } catch (error) {
      res.status(500).json({ error: "Failed to run agent" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
