import { NextRequest, NextResponse } from "next/server";
import { isStoryResponse, ApiError } from "@/types/story";

const DEFAULT_MODAL_MODEL = "garethpaul/gpt-oss-20b-fableflux-mxfp4";
const MODAL_REQUEST_TIMEOUT_MS = 30_000;

function parseModalApiUrl(rawUrl: string | undefined): URL | null {
  if (!rawUrl) {
    return null;
  }

  try {
    const url = new URL(rawUrl.trim());
    return url.protocol === "https:" && url.hostname.length > 0 ? url : null;
  } catch {
    return null;
  }
}

function hasJsonContentType(value: string | null): boolean {
  if (!value) {
    return false;
  }

  const mediaType = value.split(";", 1)[0].trim().toLowerCase();
  return mediaType === "application/json";
}

export async function POST(request: NextRequest) {
  try {
    const { prompt } = await request.json();

    if (!prompt || typeof prompt !== "string") {
      return NextResponse.json(
        { error: "Prompt is required and must be a string" } as ApiError,
        { status: 400 }
      );
    }

    const trimmedPrompt = prompt.trim();
    if (trimmedPrompt.length === 0 || trimmedPrompt.length > 200) {
      return NextResponse.json(
        { error: "Prompt must be between 1 and 200 characters" } as ApiError,
        { status: 400 }
      );
    }

    const apiKey = process.env.MODAL_API_KEY?.trim();
    if (!apiKey) {
      console.error("MODAL_API_KEY environment variable is not set");
      return NextResponse.json(
        { error: "Server configuration error" } as ApiError,
        { status: 500 }
      );
    }

    const modalApiUrl = parseModalApiUrl(process.env.MODAL_API_URL);
    if (!modalApiUrl) {
      console.error("MODAL_API_URL must be set to an HTTPS URL with a hostname");
      return NextResponse.json(
        { error: "Server configuration error" } as ApiError,
        { status: 500 }
      );
    }

    const modalModel = (process.env.MODAL_MODEL || DEFAULT_MODAL_MODEL).trim();
    if (!modalModel) {
      console.error("MODAL_MODEL must not be empty");
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
        content: `Tell me a bedtime story about ${trimmedPrompt}.`,
      },
    ];

    const modalResponse = await fetch(modalApiUrl.toString(), {
      method: "POST",
      signal: AbortSignal.timeout(MODAL_REQUEST_TIMEOUT_MS),
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: modalModel,
        messages,
        temperature: 0.7,
        max_tokens: 2000,
      }),
    });

    if (!modalResponse.ok) {
      console.error("Modal API error:", modalResponse.status);
      return NextResponse.json(
        {
          error: "Failed to generate story",
          details: `API returned ${modalResponse.status}`,
        } as ApiError,
        { status: 500 }
      );
    }

    if (!hasJsonContentType(modalResponse.headers.get("content-type"))) {
      console.error("Modal API returned a non-JSON response");
      return NextResponse.json(
        { error: "Failed to generate story" } as ApiError,
        { status: 500 }
      );
    }

    const modalData = await modalResponse.json();

    // Extract the story content from Modal's response
    const storyContent = modalData.choices?.[0]?.message?.content;

    if (!storyContent) {
      console.error("No content in Modal response");
      return NextResponse.json(
        { error: "No story content received" } as ApiError,
        { status: 500 }
      );
    }

    // Parse the JSON response from the AI
    try {
      const storyData: unknown = JSON.parse(storyContent);

      if (!isStoryResponse(storyData)) {
        throw new Error("Invalid story response shape");
      }

      return NextResponse.json(storyData);
    } catch (parseError) {
      console.error("Failed to parse story JSON:", parseError);
      return NextResponse.json(
        {
          error: "Failed to parse story format",
          details: "The AI response was not in the expected format",
        } as ApiError,
        { status: 500 }
      );
    }
  } catch (error) {
    if (error instanceof Error && error.name === "TimeoutError") {
      console.error("Modal API request timed out");
      return NextResponse.json(
        { error: "Story generation timed out" } as ApiError,
        { status: 504 }
      );
    }

    console.error("Modal API request failed");
    return NextResponse.json(
      { error: "Internal server error" } as ApiError,
      { status: 500 }
    );
  }
}
