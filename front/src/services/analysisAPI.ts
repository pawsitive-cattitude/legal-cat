import { AnalysisResponse, UploadResponse } from "@/types/analysis";

const API_BASE_URL = "http://localhost:8000";

export class AnalysisAPI {
  static async uploadAndAnalyze(files: FileList): Promise<UploadResponse> {
    const formData = new FormData();

    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }

    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Upload failed");
    }

    return response.json();
  }

  static async getAnalysis(analysisId: string): Promise<AnalysisResponse> {
    const response = await fetch(`${API_BASE_URL}/api/analysis/${analysisId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to get analysis");
    }

    return response.json();
  }

  static getPdfUrl(analysisId: string): string {
    return `${API_BASE_URL}/api/pdf/${analysisId}`;
  }

  // Upload with progress tracking
  static async uploadWithProgress(
    files: FileList,
    onProgress: (progress: number) => void
  ): Promise<UploadResponse> {
    return new Promise((resolve, reject) => {
      const formData = new FormData();

      for (let i = 0; i < files.length; i++) {
        formData.append("files", files[i]);
      }

      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener("progress", (e) => {
        if (e.lengthComputable) {
          const percentComplete = (e.loaded / e.total) * 100;
          onProgress(percentComplete);
        }
      });

      xhr.addEventListener("load", () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          resolve(response);
        } else {
          const error = JSON.parse(xhr.responseText);
          reject(new Error(error.detail || "Upload failed"));
        }
      });

      xhr.addEventListener("error", () => {
        reject(new Error("Upload failed"));
      });

      xhr.open("POST", `${API_BASE_URL}/api/analyze`);
      xhr.send(formData);
    });
  }
}
