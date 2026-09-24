// Base URL of the FastAPI backend. Override with VITE_API_BASE in a .env file
// if the backend isn't running on localhost:8080.
export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function parseJsonSafe(res) {
  const text = await res.text();
  try {
    return text ? JSON.parse(text) : {};
  } catch {
    return { detail: text };
  }
}

async function request(path, { method = "GET", token, body } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await parseJsonSafe(res);

  if (!res.ok) {
    const message = data.detail || `Request failed (${res.status})`;
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }

  return data;
}

// ---- Auth ----

export function login(email, password) {
  return request("/auth/login", {
    method: "POST",
    body: { email, password },
  });
}

export function registerStudent(payload) {
  return request("/auth/register/student", { method: "POST", body: payload });
}

export function registerTeacher(payload) {
  return request("/auth/register/teacher", { method: "POST", body: payload });
}

export function registerParent(payload) {
  return request("/auth/register/parent", { method: "POST", body: payload });
}

// ---- Profiles ----

const PROFILE_PATH = {
  student: "/students/profile",
  teacher: "/teachers/profile",
  parent: "/parents/profile",
};

export function getProfile(role, token) {
  const path = PROFILE_PATH[role];
  if (!path) return Promise.reject(new Error(`Unknown role: ${role}`));
  return request(path, { token });
}

// ---- Chat ----

export function getChatHistory(role, token) {
  return request(`/chatbot/chat/history/${role}`, { token });
}

// Streams tokens from POST /chat/stream/{role}, which returns
// Server-Sent-Events over a normal fetch body (not EventSource, since we
// need to send a POST body + an Authorization header).
export async function streamChat(role, message, token, { onToken, onDone, onError }) {
  try {
    const res = await fetch(`${API_BASE}/chatbot/chat/stream/${role}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ message }),
    });

    if (!res.ok || !res.body) {
      const data = await parseJsonSafe(res);
      throw new Error(data.detail || `Request failed (${res.status})`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop(); // keep any partial event for next chunk

      for (const rawEvent of events) {
        const line = rawEvent.trim();
        if (!line.startsWith("data:")) continue;

        const jsonStr = line.slice(5).trim();
        let payload;
        try {
          payload = JSON.parse(jsonStr);
        } catch {
          continue;
        }

        if (payload.token) onToken(payload.token);
        if (payload.error) onError(payload.error);
        if (payload.done) {
          onDone();
          return;
        }
      }
    }

    onDone();
  } catch (err) {
    onError(err.message || "Something went wrong while streaming the reply.");
    onDone();
  }
}
