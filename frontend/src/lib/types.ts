export interface Citation {
  document_title: string;
  page_number?: number | null;
  section?: string | null;
  chunk_id?: string | null;
  relevance_score?: number | null;
  excerpt?: string | null;
  embedding?: number[] | null;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  citations?: Citation[] | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  user_id?: string | null;
  title?: string | null;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface ChatResponse {
  user_message: Message;
  assistant_message: Message;
}

export interface SuggestedQuestion {
  id: string;
  question: string;
  category?: string | null;
  display_order: number;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

export interface PublicAskResponse {
  answer: string;
  citations: Citation[];
  model_used?: string | null;
  latency_ms: number;
}

export interface APCEstimateRequest {
  paper_type: string;
  num_pages: number;
  author_category: string;
}

export interface APCEstimateResponse {
  paper_type: string;
  num_pages: number;
  author_category: string;
  subtotal: string;
  discount_amount: string;
  total: string;
  currency: string;
  requires_waiver_approval: boolean;
  breakdown: string;
}
