import type { RunSummary, RunDetail, CharacterOutput, SimulationMode } from "./types";

const API_BASE = "";

export async function fetchRuns(): Promise<RunSummary[]> {
  const res = await fetch(`${API_BASE}/api/runs`);
  if (!res.ok) throw new Error("Failed to fetch runs");
  return res.json();
}

export async function fetchRun(name: string): Promise<RunDetail> {
  const res = await fetch(`${API_BASE}/api/runs/${name}`);
  if (!res.ok) throw new Error("Run not found");
  return res.json();
}

export async function fetchCharacters(): Promise<CharacterOutput[]> {
  const res = await fetch(`${API_BASE}/api/characters`);
  if (!res.ok) throw new Error("Failed to fetch characters");
  return res.json();
}

export async function fetchCharacter(uuid: string): Promise<CharacterOutput> {
  const res = await fetch(`${API_BASE}/api/characters/${uuid}`);
  if (!res.ok) throw new Error("Character not found");
  return res.json();
}

export async function createCharacter(prompt: string): Promise<CharacterOutput[]> {
  const res = await fetch(`${API_BASE}/api/characters`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error("Failed to create character");
  return res.json();
}

export async function splitCharacterPrompts(prompt: string): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/characters/split`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error("Failed to split prompts");
  const data = await res.json();
  return data.prompts;
}

export async function generateCharacter(prompt: string): Promise<CharacterOutput> {
  const res = await fetch(`${API_BASE}/api/characters/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error("Failed to generate character");
  return res.json();
}

export async function deleteCharacter(uuid: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/characters/${uuid}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete character");
}

export async function startRun(
  characters: string[],
  mode: SimulationMode,
  task: string,
  votingStart: number = 120,
  duration: number | null = null,
): Promise<{ runName?: string }> {
  const res = await fetch(`${API_BASE}/api/runs/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ characters, mode, task, voting_start: votingStart, duration }),
  });
  if (!res.ok) throw new Error("Failed to start run");
  return res.json();
}

export async function stopRun(runName: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/runs/${runName}/stop`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to stop run");
}

export async function continueRun(runName: string, message: string, duration: number): Promise<void> {
  const res = await fetch(`${API_BASE}/api/runs/${runName}/continue`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, duration }),
  });
  if (!res.ok) throw new Error("Failed to continue run");
}

