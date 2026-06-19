export interface StoryResponse {
  title: string;
  characters: string | string[] | { name: string; description?: string }[];
  setting: string;
  story: string;
  moral: string;
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function isCharacter(value: unknown): value is string | { name: string; description?: string } {
  if (isNonEmptyString(value)) {
    return true;
  }

  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return false;
  }

  const character = value as Record<string, unknown>;
  return (
    isNonEmptyString(character.name) &&
    (character.description === undefined || typeof character.description === "string")
  );
}

export function isStoryResponse(value: unknown): value is StoryResponse {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return false;
  }

  const story = value as Record<string, unknown>;
  const characters = story.characters;
  const validCharacters =
    isNonEmptyString(characters) ||
    (Array.isArray(characters) && characters.length > 0 && characters.every(isCharacter));

  return (
    isNonEmptyString(story.title) &&
    validCharacters &&
    isNonEmptyString(story.setting) &&
    isNonEmptyString(story.story) &&
    isNonEmptyString(story.moral)
  );
}

export interface ApiError {
  error: string;
  details?: string;
}
