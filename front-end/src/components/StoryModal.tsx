"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import LoadingSpinner from "./LoadingSpinner";
import ErrorMessage from "./ErrorMessage";
import { StoryResponse, ApiError } from "@/types/story";

interface StoryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function StoryModal({ isOpen, onClose }: StoryModalProps) {
  const [prompt, setPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!prompt.trim()) {
      setError("Please enter a story prompt");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: prompt.trim() }),
      });

      const data = await response.json();

      if (!response.ok) {
        const apiError = data as ApiError;
        throw new Error(apiError.error || "Failed to generate story");
      }

      const storyData = data as StoryResponse;

      // Store the story data in localStorage to pass it to the story page
      localStorage.setItem("currentStory", JSON.stringify(storyData));

      // Navigate to the story page
      router.push("/story");

      // Close the modal
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      setPrompt("");
      setError(null);
      onClose();
    }
  };

  const handleRetry = () => {
    setError(null);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-900">
              Create Your Story
            </h2>
            {!isLoading && (
              <button
                onClick={handleClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            )}
          </div>

          {isLoading ? (
            <div className="py-8">
              <LoadingSpinner message="Creating your story..." />
            </div>
          ) : error ? (
            <div className="mb-4">
              <ErrorMessage message={error} onRetry={handleRetry} />
            </div>
          ) : null}

          {!isLoading && (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label
                  htmlFor="prompt"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  What would you like your story to be about?
                </label>
                <textarea
                  id="prompt"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="e.g., a brave little car, a magical forest adventure, a friendly dragon..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-black"
                  rows={4}
                  maxLength={200}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {prompt.length}/200 characters
                </p>
              </div>

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={handleClose}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!prompt.trim()}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  Generate Story
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
