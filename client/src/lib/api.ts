const API_BASE = "/api";

export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem("authToken");
  const headers = new Headers(options.headers);
  
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  } else {
    console.warn("No auth token found in localStorage for request:", url);
  }
  
  return fetch(url, {
    ...options,
    headers,
  });
}

export const api = {
  auth: {
    magicLink: async (email: string) => {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      if (!res.ok) throw new Error("Failed to login");
      return res.json();
    },
    
    getMe: async () => {
      const res = await fetchWithAuth(`${API_BASE}/auth/me`);
      if (!res.ok) throw new Error("Not authenticated");
      return res.json();
    },
  },
  
  ingest: {
    upload: async (formData: FormData) => {
      const res = await fetchWithAuth(`${API_BASE}/ingest`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Upload failed");
      return res.json();
    },
  },
  
  topics: {
    list: async () => {
      const res = await fetchWithAuth(`${API_BASE}/topics`);
      if (!res.ok) throw new Error("Failed to fetch topics");
      return res.json();
    },
  },
  
  plan: {
    generate: async (data: any) => {
      const res = await fetchWithAuth(`${API_BASE}/plan/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("Failed to generate plan");
      return res.json();
    },
    
    get: async () => {
      const res = await fetchWithAuth(`${API_BASE}/plan`);
      if (!res.ok) return null;
      return res.json();
    },
  },
  
  practice: {
    generate: async (data: any) => {
      const res = await fetchWithAuth(`${API_BASE}/practice/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("Failed to generate practice questions");
      return res.json();
    },
  },
  
  mock: {
    generate: async (data: any) => {
      const res = await fetchWithAuth(`${API_BASE}/mock/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("Failed to generate mock exam");
      return res.json();
    },
    
    list: async () => {
      const res = await fetchWithAuth(`${API_BASE}/mock/list`);
      if (!res.ok) throw new Error("Failed to fetch mocks");
      return res.json();
    },
    
    start: async (mockId: string) => {
      const res = await fetchWithAuth(`${API_BASE}/mock/attempt/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mockId }),
      });
      if (!res.ok) throw new Error("Failed to start attempt");
      return res.json();
    },
    
    submit: async (data: any) => {
      const res = await fetchWithAuth(`${API_BASE}/mock/attempt/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("Failed to submit attempt");
      return res.json();
    },
  },
  
  flashcards: {
    generate: async (data: any) => {
      const res = await fetchWithAuth(`${API_BASE}/flashcards/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("Failed to generate flashcards");
      return res.json();
    },
    
    due: async () => {
      const res = await fetchWithAuth(`${API_BASE}/flashcards/due`);
      if (!res.ok) throw new Error("Failed to fetch due flashcards");
      return res.json();
    },
    
    review: async (cardId: string, quality: string) => {
      const res = await fetchWithAuth(`${API_BASE}/flashcards/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cardId, quality }),
      });
      if (!res.ok) throw new Error("Failed to review flashcard");
      return res.json();
    },
  },
  
  placement: {
    createProfile: async (data: any) => {
      const res = await fetchWithAuth(`${API_BASE}/placement/profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("Failed to create placement profile");
      return res.json();
    },
    
    list: async () => {
      const res = await fetchWithAuth(`${API_BASE}/placement/list`);
      if (!res.ok) throw new Error("Failed to fetch placement profiles");
      return res.json();
    },
  },
  
  code: {
    execute: async (data: any) => {
      const res = await fetchWithAuth(`${API_BASE}/code/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("Failed to execute code");
      return res.json();
    },
  },
  
  youtube: {
    suggest: async (topic: string) => {
      const res = await fetchWithAuth(`${API_BASE}/youtube/suggest?topic=${encodeURIComponent(topic)}`);
      if (!res.ok) throw new Error("Failed to fetch YouTube suggestions");
      return res.json();
    },
  },
  
  agent: {
    run: async (goal: string) => {
      return new EventSource(`${API_BASE}/agent/run?goal=${encodeURIComponent(goal)}&token=${localStorage.getItem("authToken")}`);
    },
  },
};
