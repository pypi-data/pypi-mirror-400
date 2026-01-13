import { useState, useEffect, useRef, useMemo } from "react";
import type { CharacterOutput, SimulationMode } from "../types";
import { fetchCharacters } from "../api";
import { LoadingState } from "./LoadingState";
import { EmptyState } from "./EmptyState";

interface Props {
  onStart: (characters: string[], mode: SimulationMode, task: string, votingStart: number, duration: number | null) => void;
  onCancel: () => void;
}

export function NewRunForm({ onStart, onCancel }: Props) {
  const [characters, setCharacters] = useState<CharacterOutput[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [prompt, setPrompt] = useState("");
  const [votingEnabled, setVotingEnabled] = useState(false);
  const [votingStart, setVotingStart] = useState(120);
  const [duration, setDuration] = useState(300);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [focusIndex, setFocusIndex] = useState(0);
  const listRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchCharacters()
      .then(setCharacters)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    if (!search.trim()) return characters;
    const q = search.toLowerCase();
    return characters.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        c.bio.toLowerCase().includes(q) ||
        c.occupation.toLowerCase().includes(q),
    );
  }, [characters, search]);

  // Reset focus when filter changes
  const prevFilterLength = useRef(filtered.length);
  useEffect(() => {
    if (filtered.length !== prevFilterLength.current) {
      prevFilterLength.current = filtered.length;
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setFocusIndex(0);
    }
  }, [filtered.length]);

  function toggleCharacter(name: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  }

  // Keyboard navigation for character list
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      // Only handle when search or list is focused
      const isSearchFocused = document.activeElement === searchRef.current;
      const isListFocused = document.activeElement === listRef.current;

      if (!isSearchFocused && !isListFocused) return;

      if (isSearchFocused) {
        if (e.key === "Escape") {
          searchRef.current?.blur();
          listRef.current?.focus();
        }
        if (e.key === "ArrowDown") {
          e.preventDefault();
          listRef.current?.focus();
        }
        return;
      }

      // List navigation
      switch (e.key) {
        case "ArrowDown":
        case "j":
          e.preventDefault();
          setFocusIndex((i) => Math.min(i + 1, filtered.length - 1));
          break;
        case "ArrowUp":
        case "k":
          e.preventDefault();
          setFocusIndex((i) => Math.max(i - 1, 0));
          break;
        case " ":
        case "x":
        case "Enter":
          e.preventDefault();
          if (filtered[focusIndex]) toggleCharacter(filtered[focusIndex].name);
          break;
        case "/":
          e.preventDefault();
          searchRef.current?.focus();
          break;
        case "Escape":
          if (selected.size > 0) {
            setSelected(new Set());
          }
          break;
        case "a":
          if (e.metaKey || e.ctrlKey) {
            e.preventDefault();
            if (selected.size === filtered.length) {
              setSelected(new Set());
            } else {
              setSelected(new Set(filtered.map((c) => c.name)));
            }
          }
          break;
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [filtered, focusIndex, selected.size]);

  // Scroll focused item into view
  useEffect(() => {
    const item = listRef.current?.querySelector(`[data-index="${focusIndex}"]`);
    item?.scrollIntoView({ block: "nearest" });
  }, [focusIndex]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (selected.size === 0) return;
    // If voting is enabled, it's task mode; otherwise casual
    const mode: SimulationMode = votingEnabled ? "task" : "casual";
    const durationValue = votingEnabled ? null : duration;
    onStart(Array.from(selected), mode, prompt, votingStart, durationValue);
  }

  const canSubmit = selected.size > 0;

  if (loading) {
    return <LoadingState message="Loading characters..." />;
  }

  return (
    <div className="new-run-form">
      <form onSubmit={handleSubmit}>
        <div className="form-section">
          <label className="form-label">Characters</label>
          {characters.length === 0 ? (
            <EmptyState>
              No characters found. Generate some first.
            </EmptyState>
          ) : (
            <div className="character-select-container">
              <div className="search-box">
                <input
                  ref={searchRef}
                  type="text"
                  placeholder="Search..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="search-input"
                />
                {search && (
                  <button type="button" className="search-clear" onClick={() => setSearch("")}>
                    ×
                  </button>
                )}
              </div>
              {filtered.length === 0 ? (
                <div className="empty-state">No matches</div>
              ) : (
                <div ref={listRef} className="character-select-list" tabIndex={0}>
                  {filtered.map((char, i) => (
                    <div
                      key={char.uuid}
                      data-index={i}
                      className={`character-list-item ${i === focusIndex ? "focused" : ""} ${selected.has(char.name) ? "selected" : ""}`}
                      onClick={() => toggleCharacter(char.name)}
                    >
                      <input
                        type="checkbox"
                        checked={selected.has(char.name)}
                        onChange={(e) => {
                          e.stopPropagation();
                          toggleCharacter(char.name);
                        }}
                        onClick={(e) => e.stopPropagation()}
                        className="char-checkbox"
                      />
                      <span className="char-list-emoji">{char.emoji}</span>
                      <div className="char-list-info">
                        <div className="char-list-name">{char.name}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="form-section">
          <textarea
            className="task-input"
            placeholder="What should they talk about or do?"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={3}
          />
        </div>

        <div className="form-section">
          <div className="voting-row">
            <label className="voting-checkbox-label">
              <input
                type="checkbox"
                checked={votingEnabled}
                onChange={(e) => setVotingEnabled(e.target.checked)}
                className="voting-checkbox"
              />
              <span>Enable voting</span>
            </label>
            {votingEnabled && (
              <div className="voting-start-inline">
                <span className="voting-label">after</span>
                <input
                  type="number"
                  min={0}
                  max={3600}
                  value={votingStart}
                  onChange={(e) => setVotingStart(Math.max(0, parseInt(e.target.value) || 0))}
                  className="voting-input-small"
                />
                <span className="voting-label">seconds</span>
              </div>
            )}
            {!votingEnabled && (
              <div className="voting-start-inline">
                <span className="voting-label">run for</span>
                <input
                  type="number"
                  min={10}
                  max={3600}
                  value={duration}
                  onChange={(e) => setDuration(Math.max(10, parseInt(e.target.value) || 300))}
                  className="voting-input-small"
                />
                <span className="voting-label">seconds</span>
              </div>
            )}
          </div>
        </div>

        <div className="form-actions">
          <button type="button" className="cancel-btn" onClick={onCancel}>
            Cancel
          </button>
          <button type="submit" className="start-btn" disabled={!canSubmit}>
            Start
          </button>
        </div>
      </form>
    </div>
  );
}
