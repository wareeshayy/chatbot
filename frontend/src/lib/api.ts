import type {
  APCEstimateRequest,
  APCEstimateResponse,
  ChatResponse,
  Conversation,
  PublicAskResponse,
  SuggestedQuestion,
  TokenResponse,
  User,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  let res: Response;
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 90000);
    res = await fetch(`${API_URL}${path}`, { ...options, headers, signal: controller.signal });
    clearTimeout(timeout);
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      throw new ApiError("Request timed out after 90s. Is the backend running? Add GEMINI_API_KEY for faster answers.", 0);
    }
    throw new ApiError(
      `Cannot reach backend at ${API_URL}. Run: cd backend && uvicorn app.main:app --reload --port 8000`,
      0,
    );
  }

  if (!res.ok) {
    let detail: any = res.statusText;
    try {
      const body = await res.json();
      if (body.detail) {
        if (typeof body.detail === "string") {
          detail = body.detail;
        } else if (Array.isArray(body.detail)) {
          detail = body.detail
            .map((err: any) => {
              const loc = err.loc ? err.loc.join(" -> ") : "";
              return `${loc ? loc + ": " : ""}${err.msg || JSON.stringify(err)}`;
            })
            .join("; ");
        } else if (typeof body.detail === "object") {
          detail = body.detail.message || JSON.stringify(body.detail);
        } else {
          detail = String(body.detail);
        }
      }
    } catch {
      /* ignore */
    }
    throw new ApiError(String(detail), res.status);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  login: (email: string, password: string) =>
    request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  register: (email: string, password: string, full_name: string) =>
    request<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name }),
    }),

  getMe: (token: string) => request<User>("/auth/me", {}, token),

  getSuggestedQuestions: () =>
    request<SuggestedQuestion[]>("/chat/suggested-questions"),

  /** Primary chatbot endpoint — no login required */
  askPublic: (
    content: string,
    history: { role: string; content: string }[] = [],
  ) =>
    request<PublicAskResponse>("/chat/ask", {
      method: "POST",
      body: JSON.stringify({ content, history }),
    }),

  createConversation: (token: string, title?: string) =>
    request<Conversation>(
      "/chat/conversations",
      {
        method: "POST",
        body: JSON.stringify(title ? { title } : {}),
      },
      token,
    ),

  getConversation: (token: string, id: string) =>
    request<Conversation>(`/chat/conversations/${id}`, {}, token),

  sendMessage: (token: string, conversationId: string, content: string) =>
    request<ChatResponse>(
      `/chat/conversations/${conversationId}/messages`,
      { method: "POST", body: JSON.stringify({ content }) },
      token,
    ),

  estimateAPC: (data: APCEstimateRequest) =>
    request<APCEstimateResponse>("/apc/estimate", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  health: () => request<{ status: string }>("/health"),
};

export { ApiError };
