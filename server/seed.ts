import { storage } from "./storage";

export async function seedDatabase(userId: string) {
  console.log("Seeding database with sample data...");

  // Create sample topics
  const topics = [
    { name: "Database Normalization", importanceScore: 9, masteryScore: 45 },
    { name: "SQL Joins", importanceScore: 8, masteryScore: 60 },
    { name: "Transaction Management", importanceScore: 7, masteryScore: 30 },
    { name: "Indexing and Performance", importanceScore: 8, masteryScore: 55 },
    { name: "NoSQL Databases", importanceScore: 6, masteryScore: 70 },
    { name: "Data Structures - Arrays", importanceScore: 9, masteryScore: 80 },
    { name: "Data Structures - Trees", importanceScore: 8, masteryScore: 50 },
    { name: "Algorithms - Sorting", importanceScore: 9, masteryScore: 65 },
    { name: "Dynamic Programming", importanceScore: 10, masteryScore: 35 },
    { name: "System Design Basics", importanceScore: 7, masteryScore: 40 },
  ];

  for (const topicData of topics) {
    await storage.createTopic({
      userId,
      ...topicData,
    });
  }

  // Create a study plan
  const allTopics = await storage.getTopicsByUserId(userId);
  const examDate = new Date();
  examDate.setDate(examDate.getDate() + 60); // 60 days from now

  await storage.createStudyPlan({
    userId,
    startDate: new Date().toISOString(),
    endDate: examDate.toISOString(),
    examType: "SEE (Semester End Exam)",
    blocks: [
      {
        id: "block-1",
        topicId: allTopics[0].id,
        topicName: allTopics[0].name,
        activity: "learn",
        duration: 60,
        scheduledFor: new Date().toISOString(),
        completed: false,
      },
      {
        id: "block-2",
        topicId: allTopics[1].id,
        topicName: allTopics[1].name,
        activity: "practice",
        duration: 45,
        scheduledFor: new Date().toISOString(),
        completed: false,
      },
    ],
    weeklyGoal: "Study 20 hours per week with focus on weak topics",
  });

  // Create sample practice questions
  await storage.createPracticeQuestion({
    userId,
    topicId: allTopics[0].id,
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
    rubric: "5 points for explaining each command, 5 points for examples, 5 points for use cases",
    difficulty: "medium",
    citations: ["Database Systems Textbook - Chapter 7", "SQL Documentation"],
    confidence: "High",
  });

  // Create a mock exam
  await storage.createMockExam({
    userId,
    type: "SEE",
    title: "Database Management Systems - Mock Exam 1",
    duration: 120,
    totalMarks: 100,
    questions: [
      {
        id: "q1",
        question: "Define database normalization and explain its importance.",
        marks: 10,
        rubric: "Definition: 5 marks, Importance: 5 marks",
        topicId: allTopics[0].id,
      },
      {
        id: "q2",
        question: "Write SQL queries to demonstrate INNER JOIN, LEFT JOIN, and RIGHT JOIN.",
        marks: 15,
        rubric: "Each query: 5 marks",
        topicId: allTopics[1].id,
      },
      {
        id: "q3",
        question: "Explain ACID properties with examples.",
        marks: 10,
        rubric: "Each property with example: 2.5 marks",
        topicId: allTopics[2].id,
      },
      {
        id: "q4",
        question: "Compare B-tree and Hash indexing. When would you use each?",
        marks: 10,
        rubric: "Comparison: 5 marks, Use cases: 5 marks",
        topicId: allTopics[3].id,
      },
      {
        id: "q5",
        question: "Design a database schema for an e-commerce application.",
        marks: 15,
        rubric: "Tables: 5 marks, Relationships: 5 marks, Normalization: 5 marks",
        topicId: allTopics[0].id,
      },
    ],
    instructions:
      "Answer all questions. Show your work for full credit. Time limit: 2 hours.",
  });

  // Create sample flashcards
  const flashcardData = [
    {
      front: "What is normalization?",
      back: "The process of organizing data to minimize redundancy and improve data integrity by dividing large tables into smaller ones and defining relationships.",
    },
    {
      front: "What does ACID stand for?",
      back: "Atomicity, Consistency, Isolation, Durability - the four key properties of database transactions.",
    },
    {
      front: "Difference between INNER JOIN and OUTER JOIN?",
      back: "INNER JOIN returns only matching rows from both tables. OUTER JOIN returns all rows from one or both tables, with NULLs for non-matching rows.",
    },
  ];

  for (const card of flashcardData) {
    const nextReview = new Date();
    nextReview.setDate(nextReview.getDate() + 1);
    
    await storage.createFlashcard({
      userId,
      topicId: allTopics[0].id,
      front: card.front,
      back: card.back,
      nextReviewAt: nextReview.toISOString(),
      easinessFactor: 2.5,
      interval: 1,
      repetitions: 0,
    });
  }

  console.log("✓ Database seeded successfully!");
  console.log(`  - ${topics.length} topics created`);
  console.log("  - 1 study plan created");
  console.log("  - 1 practice question created");
  console.log("  - 1 mock exam created");
  console.log(`  - ${flashcardData.length} flashcards created`);
}
