import type { ChatResponse, FeatureCollection, RailFeature, SearchResult } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function fetchFeatures(): Promise<FeatureCollection> {
  return request<FeatureCollection>("/api/features");
}

export async function searchFeatures(query: string): Promise<SearchResult[]> {
  const payload = await request<{ results: SearchResult[] }>(`/api/search?q=${encodeURIComponent(query)}`);
  return payload.results;
}

export async function askQuestion(question: string, selectedFeatureId: string | null): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      question,
      selected_feature_id: selectedFeatureId,
      include_sources: true,
    }),
  });
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}
