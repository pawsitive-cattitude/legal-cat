"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Navbar from "../../components/Navbar";
import { AnalysisAPI } from "../../services/analysisAPI";

const UploadPage = () => {
  const router = useRouter();
  const [files, setFiles] = useState<FileList | null>(null);
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");
  const [dragOver, setDragOver] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiles(e.target.files);
    setMessage(""); // Clear any previous messages
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    setFiles(e.dataTransfer.files);
    setMessage(""); // Clear any previous messages
  };

  const handleUpload = async () => {
    if (!files || files.length === 0) {
      setMessage("Please select at least one PDF file.");
      return;
    }

    // Validate file types
    for (let i = 0; i < files.length; i++) {
      if (!files[i].name.toLowerCase().endsWith(".pdf")) {
        setMessage("Please select only PDF files.");
        return;
      }
    }

    setUploading(true);
    setProgress(0);
    setMessage("");

    try {
      const response = await AnalysisAPI.uploadWithProgress(
        files,
        (progressPercent) => {
          setProgress(progressPercent);
        }
      );

      setMessage("Upload and analysis completed!");

      // Redirect to view page with analysis ID
      setTimeout(() => {
        router.push(`/analyze/view?id=${response.analysis_id}`);
      }, 1000);
    } catch (error) {
      console.error("Upload failed:", error);
      setMessage(
        error instanceof Error
          ? error.message
          : "Upload failed. Please try again."
      );
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <div className="flex-1 flex items-center justify-center px-16 pt-24">
        <div className="text-center">
          <h1 className="text-4xl font-serif text-gray-800 mb-8">
            Analyze Legal Documents
          </h1>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            Upload your PDF documents for AI-powered legal analysis. We'll
            identify risks, compliance issues, and provide insights.
          </p>
          <div className="max-w-lg w-full">
            <div
              className={`border-4 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
                dragOver
                  ? "border-gray-600 bg-[#FAF7F0]"
                  : "border-gray-400 bg-[#F9F6EF]"
              }`}
              onClick={() =>
                !uploading && document.getElementById("file-input")?.click()
              }
              onDragOver={(e) => {
                e.preventDefault();
                if (!uploading) setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
            >
              <div className="mb-4">
                {uploading ? (
                  <img
                    src="/cat.gif"
                    alt="Analyzing..."
                    className="mx-auto h-24 w-24"
                  />
                ) : (
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                )}
              </div>
              <p className="text-gray-700 text-lg">
                {uploading
                  ? "Analyzing document..."
                  : "Drag and drop PDF files here or click to select"}
              </p>
              {files && files.length > 0 && !uploading && (
                <p className="text-sm text-gray-600 mt-4">
                  {files.length} file(s) selected:{" "}
                  {Array.from(files)
                    .map((f) => f.name)
                    .join(", ")}
                </p>
              )}
            </div>
            <input
              id="file-input"
              type="file"
              multiple
              accept=".pdf"
              onChange={handleFileChange}
              className="hidden"
              disabled={uploading}
            />
            <button
              onClick={handleUpload}
              disabled={uploading || !files || files.length === 0}
              className="mt-6 w-full bg-gray-800 text-white px-6 py-3 rounded hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {uploading ? "Analyzing..." : "Upload & Analyze"}
            </button>
            {uploading && (
              <div className="mt-6">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gray-800 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  {Math.round(progress)}% -{" "}
                  {progress < 50 ? "Uploading..." : "Analyzing with AI..."}
                </p>
              </div>
            )}
            {message && (
              <div
                className={`mt-6 p-3 rounded ${
                  message.includes("completed") ||
                  message.includes("successful")
                    ? "bg-green-50 text-green-800 border border-green-200"
                    : message.includes("failed") || message.includes("error")
                    ? "bg-red-50 text-red-800 border border-red-200"
                    : "bg-gray-50 text-gray-800 border border-gray-200"
                }`}
              >
                <p>{message}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
