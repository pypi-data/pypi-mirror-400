import type { RunSummary, RunDetail, CharacterOutput, SimulationMode } from "./types";

const API_BASE = "";
const API_KEY_STORAGE_KEY = "society_api_key";

export function getApiKey(): string | null {
  return localStorage.getItem(API_KEY_STORAGE_KEY);
}

export function setApiKey(key: string): void {
  localStorage.setItem(API_KEY_STORAGE_KEY, key);
}

export function clearApiKey(): void {
  localStorage.removeItem(API_KEY_STORAGE_KEY);
}

function authHeaders(): Record<string, string> {
  const key = getApiKey();
  return key ? { "X-Api-Key": key } : {};
}

export async function fetchConfig(): Promise<{ has_api_key: boolean }> {
  const res = await fetch(`${API_BASE}/api/config`);
  if (!res.ok) throw new Error("Failed to fetch config");
  return res.json();
}

export async function fetchRuns(): Promise<RunSummary[]> {
  const res = await fetch(`${API_BASE}/api/runs`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Failed to fetch runs");
  return res.json();
}

export async function fetchRun(name: string): Promise<RunDetail> {
  const res = await fetch(`${API_BASE}/api/runs/${name}`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Run not found");
  return res.json();
}

export async function fetchCharacters(): Promise<CharacterOutput[]> {
  const res = await fetch(`${API_BASE}/api/characters`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Failed to fetch characters");
  return res.json();
}

export async function fetchCharacter(uuid: string): Promise<CharacterOutput> {
  const res = await fetch(`${API_BASE}/api/characters/${uuid}`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Character not found");
  return res.json();
}

export async function createCharacter(prompt: string): Promise<CharacterOutput[]> {
  const res = await fetch(`${API_BASE}/api/characters`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error("Failed to create character");
  return res.json();
}

export async function splitCharacterPrompts(prompt: string): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/characters/split`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error("Failed to split prompts");
  const data = await res.json();
  return data.prompts;
}

export async function generateCharacter(prompt: string): Promise<CharacterOutput> {
  const res = await fetch(`${API_BASE}/api/characters/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error("Failed to generate character");
  return res.json();
}

export async function deleteCharacter(uuid: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/characters/${uuid}`, {
    method: "DELETE",
    headers: authHeaders(),
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
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ characters, mode, task, voting_start: votingStart, duration }),
  });
  if (!res.ok) throw new Error("Failed to start run");
  return res.json();
}

export async function stopRun(runName: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/runs/${runName}/stop`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error("Failed to stop run");
}

export async function continueRun(runName: string, message: string, duration: number): Promise<void> {
  const res = await fetch(`${API_BASE}/api/runs/${runName}/continue`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ message, duration }),
  });
  if (!res.ok) throw new Error("Failed to continue run");
}

