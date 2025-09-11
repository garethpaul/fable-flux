import React from "react";

interface StoryFormatterProps {
  content: string;
  className?: string;
}

export default function StoryFormatter({
  content,
  className = "",
}: StoryFormatterProps) {
  // Function to format the story content with proper paragraphs
  const formatStoryContent = (text: string) => {
    // Split by double newlines to create paragraphs
    let paragraphs = text.split(/\n\s*\n/);

    // If no double newlines, try splitting by single newlines for shorter paragraphs
    if (paragraphs.length === 1) {
      paragraphs = text.split(/\n/);
    }

    // Clean up each paragraph
    paragraphs = paragraphs
      .map((p) => p.trim())
      .filter((p) => p.length > 0)
      .map((p) => {
        // Remove excessive whitespace within paragraphs
        return p.replace(/\s+/g, " ");
      });

    return paragraphs;
  };

  const paragraphs = formatStoryContent(content);

  return (
    <div className={`prose prose-lg max-w-none ${className}`}>
      {paragraphs.map((paragraph, index) => (
        <p
          key={index}
          className="text-gray-700 leading-relaxed mb-4 text-justify"
        >
          {paragraph}
        </p>
      ))}
    </div>
  );
}
