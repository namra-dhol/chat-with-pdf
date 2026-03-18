/**
 * services/api.ts
 * ----------------
 * API service layer for communicating with the FastAPI backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface UploadResponse {
    message: string;
    chunks_count: number;
    filename: string;
}

export interface ChatResponse {
    answer: string;
}

/**
 * Upload a PDF file to the backend for processing.
 * Sends as multipart/form-data.
 */
export async function uploadPdf(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/upload-pdf`, {
        method: "POST",
        body: formData,
        // Don't set Content-Type manually — fetch sets it with the correct boundary
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Ask a question about the uploaded PDF.
 */
export async function askQuestion(question: string): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Chat request failed: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Check if the backend API is available.
 */
export async function checkHealth(): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return response.ok;
    } catch {
        return false;
    }
}
