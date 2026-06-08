"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { StoryResponse } from "@/types/story";
import LoadingSpinner from "@/components/LoadingSpinner";
import StoryFormatter from "@/components/StoryFormatter";

export default function StoryPageClient() {
  const [story, setStory] = useState<StoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Get story data from localStorage
    const storyData = localStorage.getItem("currentStory");

    if (storyData) {
      try {
        const parsedStory = JSON.parse(storyData) as StoryResponse;
        setStory(parsedStory);
      } catch (error) {
        console.error("Failed to parse story data:", error);
        router.push("/");
      }
    } else {
      // No story data found, redirect to home
      router.push("/");
    }

    setIsLoading(false);
  }, [router]);

  const handleCreateAnother = () => {
    // Clear the current story
    localStorage.removeItem("currentStory");
    router.push("/");
  };

  if (isLoading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: "#DFC1B6" }}
      >
        <LoadingSpinner message="Loading your story..." />
      </div>
    );
  }

  if (!story) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: "#DFC1B6" }}
      >
        <div className="text-center">
          <p className="text-gray-600 mb-4">No story found</p>
          <button
            onClick={() => router.push("/")}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#DFC1B6" }}>
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <button
              onClick={() => router.push("/")}
              className="inline-flex items-center text-gray-700 hover:text-gray-900 mb-4 transition-colors bg-white bg-opacity-50 px-4 py-2 rounded-lg"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
              Back to Home
            </button>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-2">
              Your Story
            </h1>
            <p className="text-gray-700">Generated with love by Fable Flux</p>
          </div>

          {/* Story Content */}
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            {/* Title */}
            <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-8 text-center">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                {story.title}
              </h2>
              <div className="flex flex-wrap justify-center gap-4 text-sm">
                <div className="bg-white bg-opacity-20 rounded-full px-4 py-2 text-black">
                  <span className="font-medium">Characters:</span>{" "}
                  {typeof story.characters === "string"
                    ? story.characters
                    : Array.isArray(story.characters)
                    ? story.characters
                        .map((char) =>
                          typeof char === "string"
                            ? char
                            : char.name || "Character"
                        )
                        .join(", ")
                    : "Characters"}
                </div>
                <div className="bg-white bg-opacity-20 rounded-full px-4 py-2 text-black">
                  <span className="font-medium">Setting:</span> {story.setting}
                </div>
              </div>
            </div>

            {/* Story Body */}
            <div className="p-8 md:p-12">
              <StoryFormatter content={story.story} className="mb-8" />

              {/* Moral */}
              <div className="bg-amber-50 border-l-4 border-amber-400 p-6 rounded-r-lg">
                <h3 className="text-xl font-semibold text-amber-800 mb-2 flex items-center">
                  <svg
                    className="w-6 h-6 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                    />
                  </svg>
                  Moral of the Story
                </h3>
                <p className="text-amber-700 italic">{story.moral}</p>
              </div>
            </div>

            {/* Actions */}
            <div className="bg-gray-50 p-6 text-center">
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={handleCreateAnother}
                  className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
                >
                  Create Another Story
                </button>
                <button
                  onClick={() => window.print()}
                  className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
                >
                  Print Story
                </button>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center mt-8 text-gray-500">
            <p>✨ Made with magic by Fable Flux AI ✨</p>
          </div>
        </div>
      </div>
    </div>
  );
}
