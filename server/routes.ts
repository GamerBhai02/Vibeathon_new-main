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
      const { examType, duration, totalMarks, topics: topicIds } = req.body;
      
      // Fetch user topics
      const userTopics = await storage.getTopicsByUserId(req.user.id);
      
      // Filter selected topics or use all if none specified
      const selectedTopics = topicIds && topicIds.length > 0
        ? userTopics.filter(t => topicIds.includes(t.id))
        : userTopics;

      let questions: any[] = [];
      
      // Try to generate intelligent questions using Gemini
      try {
        const geminiApiKey = process.env.GEMINI_API_KEY;
        
        if (geminiApiKey && selectedTopics.length > 0) {
          const topicsContext = selectedTopics.map(t => 
            `Topic: ${t.name}\nContent: ${t.summary || 'No content'}`
          ).join('\n\n');

          const pythonScript = `
import sys
import json
import os

try:
    import google.generativeai as genai
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print(json.dumps({"error": "No API key"}))
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    exam_type = sys.argv[1]
    num_questions = int(sys.argv[2])
    topics_context = sys.argv[3]
    
    prompt = f"""
    Generate {num_questions} exam questions for a {exam_type} exam based on these topics:
    
    {topics_context}
    
    Create a mix of:
    - Multiple choice questions (40%)
    - Short answer questions (30%)
    - Problem-solving questions (30%)
    
    Vary difficulty levels: Easy (30%), Medium (50%), Hard (20%)
    
    Return ONLY a JSON array with this structure:
    [
        {{
            "id": "q1",
            "type": "mcq" | "short" | "problem",
            "difficulty": "easy" | "medium" | "hard",
            "question": "Question text",
            "options": ["A", "B", "C", "D"],  // only for mcq
            "marks": number,
            "topic": "topic name",
            "hint": "optional hint"
        }}
    ]
    """
    
    response = model.generate_content(prompt)
    response_text = response.text.strip()
    
    # Clean markdown formatting
    if response_text.startswith("\`\`\`json"):
        response_text = response_text[7:-3].strip()
    elif response_text.startswith("\`\`\`"):
        response_text = response_text[3:-3].strip()
    
    print(response_text)
    
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
`;

          const tmpFile = path.join('/tmp', `gemini_mock_${Date.now()}.py`);
          fs.writeFileSync(tmpFile, pythonScript);

          let pythonCmd = 'python3';
          try {
            require('child_process').execSync('python3 --version', { stdio: 'ignore' });
          } catch {
            pythonCmd = 'python';
          }

          // Calculate number of questions based on marks
          const numQuestions = Math.max(5, Math.floor(totalMarks / 10));

          const pythonProcess = spawn(pythonCmd, [tmpFile, examType, numQuestions.toString(), topicsContext.substring(0, 10000)], {
            env: {
              ...process.env,
              GEMINI_API_KEY: geminiApiKey
            }
          });

          let output = '';
          for await (const chunk of pythonProcess.stdout) {
            output += chunk;
          }

          const exitCode = await new Promise((resolve) => {
            pythonProcess.on('close', resolve);
          });

          // Clean up temp file
          try {
            fs.unlinkSync(tmpFile);
          } catch (e) {
            console.error('Failed to clean up temp file:', e);
          }

          if (exitCode === 0 && output.trim()) {
            try {
              const generatedQuestions = JSON.parse(output);
              
              if (Array.isArray(generatedQuestions) && generatedQuestions.length > 0) {
                questions = generatedQuestions.map((q, idx) => ({
                  id: `q${idx + 1}`,
                  type: q.type || 'short',
                  difficulty: q.difficulty || 'medium',
                  question: q.question,
                  options: q.options || [],
                  marks: q.marks || Math.ceil(totalMarks / generatedQuestions.length),
                  topic: q.topic,
                  hint: q.hint
                }));
              }
            } catch (parseError) {
              console.error('Failed to parse Gemini mock questions:', parseError);
            }
          }
        }
      } catch (geminiError) {
        console.error('Gemini mock generation error:', geminiError);
      }

      // Fallback: Generate basic questions if Gemini fails
      if (questions.length === 0) {
        const numQuestions = Math.max(5, Math.floor(totalMarks / 10));
        const marksPerQuestion = Math.floor(totalMarks / numQuestions);
        
        const questionTypes = ['mcq', 'short', 'problem'];
        const difficulties = ['easy', 'medium', 'hard'];
        
        questions = Array.from({ length: numQuestions }, (_, idx) => {
          const topic = selectedTopics[idx % selectedTopics.length];
          const type = questionTypes[idx % questionTypes.length];
          const difficulty = difficulties[Math.floor(Math.random() * 3)];
          
          const baseQuestions = {
            mcq: `Which of the following best describes ${topic?.name || 'the concept'}?`,
            short: `Explain the key concepts of ${topic?.name || 'this topic'} in 2-3 sentences.`,
            problem: `Solve a problem related to ${topic?.name || 'this topic'} showing all steps.`
          };
          
          return {
            id: `q${idx + 1}`,
            type,
            difficulty,
            question: baseQuestions[type as keyof typeof baseQuestions],
            options: type === 'mcq' ? [
              'Option A - First possibility',
              'Option B - Second possibility', 
              'Option C - Third possibility',
              'Option D - Fourth possibility'
            ] : [],
            marks: marksPerQuestion,
            topic: topic?.name || 'General',
            hint: `Review the material on ${topic?.name || 'this topic'}`
          };
        });
      }

      const mockExam = await storage.createMockExam({
        userId: req.user.id,
        type: examType,
        title: `${examType} Mock Exam - ${new Date().toLocaleDateString()}`,
        duration,
        totalMarks,
        questions,
        instructions: "Answer all questions within the time limit. Read each question carefully and show all working where applicable.",
      });

      res.json(mockExam);
    } catch (error) {
      console.error('Mock generation error:', error);
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

  // Generate lesson content using Gemini
  app.post("/api/learn/generate", authenticateToken, async (req: any, res) => {
    try {
      const { topicId } = req.body;
      
      if (!topicId) {
        return res.status(400).json({ error: "Topic ID is required" });
      }

      const topics = await storage.getTopicsByUserId(req.user.id);
      const topic = topics.find(t => t.id === topicId);
      
      if (!topic) {
        return res.status(404).json({ error: "Topic not found" });
      }

      // Try to generate enhanced lesson content with Gemini
      try {
        const geminiApiKey = process.env.GEMINI_API_KEY;
        
        if (!geminiApiKey) {
          throw new Error("GEMINI_API_KEY not configured");
        }

        const { spawn } = require('child_process');
        
        // Create a temporary Python script to call Gemini
        const pythonScript = `
import sys
import json
import os

try:
    import google.generativeai as genai
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print(json.dumps({"error": "No API key"}))
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    topic_name = sys.argv[1]
    topic_content = sys.argv[2]
    
    prompt = f"""
    Create a comprehensive educational lesson for the topic: "{topic_name}"
    
    Based on this content summary:
    {topic_content}
    
    Generate a detailed lesson with:
    1. Clear explanations of key concepts
    2. Step-by-step breakdown of important ideas
    3. 2-3 common mistakes students make
    4. Practical tips for understanding
    
    Return ONLY a JSON object with this structure:
    {{
        "title": "Understanding [Topic Name]",
        "sections": [
            {{"heading": "Section 1", "content": "Detailed explanation..."}},
            {{"heading": "Section 2", "content": "More details..."}}
        ],
        "commonMistakes": ["Mistake 1", "Mistake 2"],
        "tips": ["Tip 1", "Tip 2"]
    }}
    """
    
    response = model.generate_content(prompt)
    response_text = response.text.strip()
    
    # Clean markdown formatting
    if response_text.startswith("\`\`\`json"):
        response_text = response_text[7:-3].strip()
    elif response_text.startswith("\`\`\`"):
        response_text = response_text[3:-3].strip()
    
    print(response_text)
    
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
`;

        const tmpFile = path.join('/tmp', `gemini_lesson_${Date.now()}.py`);
        fs.writeFileSync(tmpFile, pythonScript);

        let pythonCmd = 'python3';
        try {
          require('child_process').execSync('python3 --version', { stdio: 'ignore' });
        } catch {
          pythonCmd = 'python';
        }

        const pythonProcess = spawn(pythonCmd, [tmpFile, topic.name, topic.summary || "No content available"], {
          env: {
            ...process.env,
            GEMINI_API_KEY: geminiApiKey
          }
        });

        let output = '';
        for await (const chunk of pythonProcess.stdout) {
          output += chunk;
        }

        let errorOutput = '';
        for await (const chunk of pythonProcess.stderr) {
          errorOutput += chunk;
        }

        const exitCode = await new Promise((resolve) => {
          pythonProcess.on('close', resolve);
        });

        // Clean up temp file
        try {
          fs.unlinkSync(tmpFile);
        } catch (e) {
          console.error('Failed to clean up temp file:', e);
        }

        if (exitCode === 0 && output.trim()) {
          try {
            const lessonData = JSON.parse(output);
            
            if (lessonData.error) {
              throw new Error(lessonData.error);
            }
            
            // Add confidence and citations
            lessonData.confidence = "High";
            lessonData.citations = [`Extracted from ${topic.name} content`];
            
            return res.json(lessonData);
          } catch (parseError) {
            console.error('Failed to parse Gemini response:', parseError);
            throw parseError;
          }
        } else {
          throw new Error(`Gemini generation failed: ${errorOutput}`);
        }
      } catch (geminiError) {
        console.error('Gemini generation error:', geminiError);
        
        // Fallback to structured content from topic summary
        const fallbackLesson = {
          title: `Understanding ${topic.name}`,
          sections: [
            {
              heading: topic.name,
              content: topic.summary || "Content is being processed. Please check back later."
            }
          ],
          commonMistakes: [],
          tips: ["Review the material regularly", "Practice with examples"],
          confidence: "Medium",
          citations: [`Based on uploaded content`]
        };
        
        return res.json(fallbackLesson);
      }
    } catch (error) {
      console.error('Learn generation endpoint error:', error);
      res.status(500).json({ error: "Failed to generate lesson content" });
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
        const errors = [];
        
        for (const file of req.files) {
            try {
                // Use system Python or python3 - find available Python interpreter
                let pythonExecutable = 'python3';
                
                // Try to find Python executable
                try {
                    const { execSync } = require('child_process');
                    execSync('python3 --version', { stdio: 'ignore' });
                } catch {
                    try {
                        const { execSync } = require('child_process');
                        execSync('python --version', { stdio: 'ignore' });
                        pythonExecutable = 'python';
                    } catch {
                        console.error('No Python interpreter found');
                        errors.push(`Could not process ${file.originalname}: Python not available`);
                        continue;
                    }
                }

                const scriptPath = path.resolve('pdfExtraction', 'extract_pdf.py');
                const pythonProcess = spawn(pythonExecutable, [scriptPath, file.path, '--mime_type', file.mimetype, '--enhance'], {
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
                if (pythonError) {
                    console.error('Python script stderr:', pythonError);
                }
                console.log('Python script exit code:', exitCode);

                let extractedTopics = [];
                
                if (exitCode !== 0 || !pythonOutput.trim()) {
                    console.error(`Python script exited with code ${exitCode}: ${pythonError}`);
                    // Failsafe: create a default topic
                    extractedTopics = [{
                        topic: `Content from ${file.originalname}`,
                        content: "This document was uploaded but could not be fully processed. Please ensure Python and pdfminer.six are installed."
                    }];
                } else {
                    try {
                        extractedTopics = JSON.parse(pythonOutput);
                    } catch (parseError) {
                        console.error('Failed to parse Python output:', parseError);
                        // Failsafe: create a default topic
                        extractedTopics = [{
                            topic: `Content from ${file.originalname}`,
                            content: "This document was processed but the output format was unexpected. Raw content may not be available."
                        }];
                    }
                }

                for (const topic of extractedTopics) {
                    const newTopic = await storage.createTopic({
                        userId: req.user.id,
                        name: topic.topic,
                        importanceScore: 5, // Default importance
                        masteryScore: 0, // Default mastery
                        summary: topic.content || "No content available",
                    });
                    topics.push(newTopic);
                }

            } catch (fileError) {
                console.error('Error processing file:', file.originalname, fileError);
                errors.push(`Failed to process ${file.originalname}`);
                
                // Failsafe: create a placeholder topic even on error
                try {
                    const fallbackTopic = await storage.createTopic({
                        userId: req.user.id,
                        name: `Document: ${file.originalname}`,
                        importanceScore: 5,
                        masteryScore: 0,
                        summary: "This document was uploaded but encountered processing errors. Please try re-uploading or check the file format.",
                    });
                    topics.push(fallbackTopic);
                } catch (fallbackError) {
                    console.error('Even fallback topic creation failed:', fallbackError);
                }
            } finally {
                // Always clean up the uploaded file
                try {
                    if (fs.existsSync(file.path)) {
                        fs.unlinkSync(file.path);
                    }
                } catch (cleanupError) {
                    console.error('Failed to clean up file:', cleanupError);
                }
            }
        }

        const response: any = { 
            success: true, 
            topicsExtracted: topics.length 
        };
        
        if (errors.length > 0) {
            response.warnings = errors;
        }

        res.json(response);
    } catch (error) {
        console.error('Ingest endpoint error:', error);
        res.status(500).json({ error: "Failed to process upload. Please try again." });
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
