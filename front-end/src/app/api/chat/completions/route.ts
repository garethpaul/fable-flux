import { NextRequest, NextResponse } from "next/server";
import { StoryResponse, ApiError } from "@/types/story";

export async function POST(request: NextRequest) {
  try {
    const { prompt } = await request.json();

    if (!prompt || typeof prompt !== "string") {
      return NextResponse.json(
        { error: "Prompt is required and must be a string" } as ApiError,
        { status: 400 }
      );
    }

    // Check for Modal_API_KEY in environment variables (system env takes precedence over .env.local)
    const apiKey = process.env.Modal_API_KEY;
    if (!apiKey) {
      console.error("Modal_API_KEY environment variable is not set");
      console.error(
        "Please set Modal_API_KEY in your system environment or .env.local file"
      );
      return NextResponse.json(
        { error: "Server configuration error" } as ApiError,
        { status: 500 }
      );
    }

    // Prepare the messages for Modal API
    const messages = [
      {
        role: "system",
        content:
          "You are Fable Flux. You must provide an age appropriate story for 3-5 year olds that they will understand and can learn from. Respond ONLY in JSON with keys: title, characters, setting, story, moral.",
      },
      {
        role: "user",
        content: `Tell me a bedtime story about ${prompt}.`,
      },
    ];

    // Modal URL
    const ModalResponse = await fetch(
      " https://garethpaul--fableflux-gpt-oss-lora-serve-dev.modal.run:8000/v1/chat/completions",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "GPT-5-Mini",
          messages,
          temperature: 0.7,
          max_tokens: 2000,
        }),
      }
    );

    if (!ModalResponse.ok) {
      const errorText = await ModalResponse.text();
      console.error("Modal API error:", ModalResponse.status, errorText);
      return NextResponse.json(
        {
          error: "Failed to generate story",
          details: `API returned ${ModalResponse.status}`,
        } as ApiError,
        { status: 500 }
      );
    }

    const ModalData = await ModalResponse.json();

    // Extract the story content from Modal's response
    const storyContent = ModalData.choices?.[0]?.message?.content;

    if (!storyContent) {
      console.error("No content in Modal response:", ModalData);
      return NextResponse.json(
        { error: "No story content received" } as ApiError,
        { status: 500 }
      );
    }

    // Parse the JSON response from the AI
    try {
      const storyData: StoryResponse = JSON.parse(storyContent);

      // Validate that all required fields are present
      if (
        !storyData.title ||
        !storyData.characters ||
        !storyData.setting ||
        !storyData.story ||
        !storyData.moral
      ) {
        throw new Error("Missing required story fields");
      }

      return NextResponse.json(storyData);
    } catch (parseError) {
      console.error("Failed to parse story JSON:", parseError, storyContent);
      return NextResponse.json(
        {
          error: "Failed to parse story format",
          details: "The AI response was not in the expected format",
        } as ApiError,
        { status: 500 }
      );
    }
  } catch (error) {
    console.error("API route error:", error);
    return NextResponse.json(
      {
        error: "Internal server error",
        details: error instanceof Error ? error.message : "Unknown error",
      } as ApiError,
      { status: 500 }
    );
  }
}
