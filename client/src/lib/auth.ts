export function setAuthToken(token: string) {
  console.log("[AUTH] Setting token:", token.substring(0, 50) + "...");
  localStorage.setItem("authToken", token);
  const saved = localStorage.getItem("authToken");
  console.log("[AUTH] Token saved successfully:", !!saved);
}

export function getAuthToken(): string | null {
  const token = localStorage.getItem("authToken");
  console.log("[AUTH] Getting token:", token ? token.substring(0, 50) + "..." : "null");
  return token;
}

export function clearAuthToken() {
  localStorage.removeItem("authToken");
}

export function isAuthenticated(): boolean {
  return !!getAuthToken();
}
