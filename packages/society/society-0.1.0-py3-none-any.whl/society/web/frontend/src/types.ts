// Re-export generated types from Python models
export type { Person, Message, AgentEvent, CharacterOutput, Channel } from "./generated-types";

// Frontend-specific types (not from Python)

export interface RunSummary {
  name: string;
  task: string;
  people: string[];
}

export interface CharacterInfo {
  uuid: string;
  name: string;
  emoji: string;
  bio: string;
  role?: string;
  occupation?: string;
}

export interface RunDetail {
  name: string;
  task: string;
  characters: CharacterInfo[];
  people: Person[];
  channels: Channel[];
  messages: Message[];
  events: AgentEvent[];
  final_answer: string | null;
}

export type SimulationMode = "task" | "casual";

// Re-import for local use after re-exporting
import type { Person, Message, Channel, AgentEvent } from "./generated-types";
