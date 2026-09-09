/**
 * Centralizes every call to the backend API. Every component imports
 * functions from here instead of writing raw fetch() calls directly --
 * so when the backend URL changes later (e.g. after deployment to
 * Render), it only needs to change in this one place.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function ingestFile(file) {
  // File uploads must be sent as FormData, not JSON -- this matches
  // what FastAPI's UploadFile expects on the backend.
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/ingest`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Upload failed (status ${response.status})`);
  }

  return response.json();
}

export async function askQuestion(question, topK = 4) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, top_k: topK }),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Chat request failed (status ${response.status})`);
  }

  return response.json();
}

export async function runEvaluation(topK = 4) {
  const response = await fetch(`${API_BASE_URL}/evaluate?top_k=${topK}`, {
    method: "POST",
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Evaluation failed (status ${response.status})`);
  }

  return response.json();
}

export async function resetKnowledgeBase() {
  const response = await fetch(`${API_BASE_URL}/reset`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Reset failed (status ${response.status})`);
  }

  return response.json();
}
export async function runLiveEvaluation(qaPairs) {
  const response = await fetch(`${API_BASE_URL}/evaluate/live`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ qa_pairs: qaPairs }),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Live evaluation failed (status ${response.status})`);
  }

  return response.json();
}