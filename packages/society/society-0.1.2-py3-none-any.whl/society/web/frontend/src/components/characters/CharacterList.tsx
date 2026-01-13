import { useState, useEffect, useRef, useMemo } from "react";
import type { CharacterOutput } from "../../types";
import { splitCharacterPrompts, generateCharacter } from "../../api";
import { EmptyState } from "../EmptyState";

interface Props {
  characters: CharacterOutput[];
  onSelect: (uuid: string) => void;
  onCreate: (prompt: string) => Promise<void>;
  onReload: () => Promise<void>;
  onBulkDelete: (uuids: string[]) => void;
  initialFocusUuid?: string;
  checkedCharacters: Set<string>;
  onCheckedChange: (checked: Set<string>) => void;
}

export function CharacterList({
  characters,
  onSelect,
  onCreate,
  onReload,
  onBulkDelete,
  initialFocusUuid,
  checkedCharacters,
  onCheckedChange,
}: Props) {
  const [search, setSearch] = useState("");
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [creatingItems, setCreatingItems] = useState<{ prompt: string; status: "splitting" | "pending" | "generating" | "done" | "error" }[]>([]);
  const [focusIndex, setFocusIndex] = useState(0);
  const listRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  const filtered = useMemo(() => {
    if (!search.trim()) return characters;
    const q = search.toLowerCase();
    return characters.filter((c) => c.name.toLowerCase().includes(q));
  }, [characters, search]);

  // Sync focus index when returning from detail view
  useEffect(() => {
    if (!initialFocusUuid) return;
    const idx = filtered.findIndex((c) => c.uuid === initialFocusUuid);
    if (idx >= 0) setFocusIndex(idx);
  }, [initialFocusUuid, filtered]);

  // Reset focus when filter changes
  const prevFilterLength = useRef(filtered.length);
  useEffect(() => {
    if (filtered.length !== prevFilterLength.current) {
      prevFilterLength.current = filtered.length;
      if (!initialFocusUuid) setFocusIndex(0);
    }
  }, [filtered.length, initialFocusUuid]);

  // Keyboard navigation
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (document.activeElement === searchRef.current) {
        if (e.key === "Escape") {
          searchRef.current?.blur();
          listRef.current?.focus();
        }
        if (e.key === "Enter") {
          e.preventDefault();
          if (e.shiftKey && search.trim()) {
            handleGenerate();
          } else {
            listRef.current?.focus();
          }
        }
        if (e.key === "ArrowDown") {
          e.preventDefault();
          listRef.current?.focus();
        }
        return;
      }

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
        case "ArrowRight":
        case "Enter":
          e.preventDefault();
          if (filtered[focusIndex]) onSelect(filtered[focusIndex].uuid);
          break;
        case " ":
        case "x":
          e.preventDefault();
          if (filtered[focusIndex]) toggleSelect(filtered[focusIndex].uuid);
          break;
        case "/":
          e.preventDefault();
          searchRef.current?.focus();
          break;
        case "Escape":
          if (checkedCharacters.size > 0) {
            onCheckedChange(new Set());
            setConfirmDelete(false);
          }
          break;
        case "a":
          if (e.metaKey || e.ctrlKey) {
            e.preventDefault();
            if (checkedCharacters.size === filtered.length) {
              onCheckedChange(new Set());
            } else {
              onCheckedChange(new Set(filtered.map((c) => c.uuid)));
            }
          }
          break;
        case "d":
          e.preventDefault();
          if (checkedCharacters.size > 0) setConfirmDelete(true);
          break;
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [filtered, focusIndex, onSelect, checkedCharacters.size, onCheckedChange]);

  // Scroll focused item into view
  useEffect(() => {
    const item = listRef.current?.querySelector(`[data-index="${focusIndex}"]`);
    item?.scrollIntoView({ block: "nearest" });
  }, [focusIndex]);

  function toggleSelect(uuid: string) {
    const next = new Set(checkedCharacters);
    if (next.has(uuid)) next.delete(uuid);
    else next.add(uuid);
    onCheckedChange(next);
  }

  function handleBulkDelete() {
    if (confirmDelete) {
      onBulkDelete(Array.from(checkedCharacters));
      onCheckedChange(new Set());
      setConfirmDelete(false);
    } else {
      setConfirmDelete(true);
    }
  }

  const isCreating = creatingItems.some((item) =>
    item.status === "splitting" || item.status === "pending" || item.status === "generating"
  );

  async function handleGenerate() {
    if (!search.trim() || isCreating) return;
    const prompt = search.trim();
    setSearch("");

    // Immediately show placeholder with original prompt
    setCreatingItems([{ prompt, status: "splitting" }]);

    try {
      // Split the prompt into individual character prompts
      const prompts = await splitCharacterPrompts(prompt);

      // Replace with individual placeholder items
      setCreatingItems(prompts.map((p) => ({ prompt: p, status: "pending" as const })));

      // Generate each character in parallel
      await Promise.all(
        prompts.map(async (p, index) => {
          // Mark as generating
          setCreatingItems((items) =>
            items.map((item, i) => (i === index ? { ...item, status: "generating" as const } : item))
          );

          try {
            await generateCharacter(p);
            // Mark as done and reload to show the new character
            setCreatingItems((items) =>
              items.map((item, i) => (i === index ? { ...item, status: "done" as const } : item))
            );
            await onReload();
          } catch (err) {
            console.error(`Failed to generate character "${p}":`, err);
            setCreatingItems((items) =>
              items.map((item, i) => (i === index ? { ...item, status: "error" as const } : item))
            );
          }
        })
      );
    } catch (err) {
      console.error("Failed to split prompts:", err);
      // Fallback: just use the original prompt as a single item
      setCreatingItems([{ prompt, status: "generating" }]);
      try {
        await onCreate(prompt);
      } catch {
        // Error already handled
      }
    } finally {
      setCreatingItems([]);
    }
  }

  return (
    <div className="character-list-container">
      <div className="character-list-header">
        <div className="search-box">
          <input
            ref={searchRef}
            type="text"
            placeholder="Search or generate..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
          {search && (
            <button className="search-clear" onClick={() => setSearch("")}>
              ×
            </button>
          )}
        </div>
        <button
          className="generate-btn"
          onClick={handleGenerate}
          disabled={!search.trim() || isCreating}
        >
          ✨ Generate <span className="keyhint">⇧↵</span>
        </button>
      </div>

      {checkedCharacters.size > 0 && (
        <BulkActions
          count={checkedCharacters.size}
          confirmDelete={confirmDelete}
          onDelete={handleBulkDelete}
          onCancelDelete={() => setConfirmDelete(false)}
          onClearSelection={() => onCheckedChange(new Set())}
        />
      )}

      {filtered.length === 0 && creatingItems.length === 0 ? (
        <EmptyState>
          {characters.length === 0
            ? "Type a name to generate a character"
            : `No matches found. Shift+Enter to generate.`}
        </EmptyState>
      ) : (
        <div ref={listRef} className="character-list" tabIndex={0}>
          {creatingItems.filter((item) => item.status !== "done").map((item, i) => (
            <CreatingPlaceholder key={`creating-${i}`} name={item.prompt} status={item.status} />
          ))}
          {filtered.map((char, i) => (
            <CharacterListItem
              key={char.uuid}
              char={char}
              index={i}
              focused={i === focusIndex}
              selected={checkedCharacters.has(char.uuid)}
              onSelect={() => onSelect(char.uuid)}
              onToggle={() => toggleSelect(char.uuid)}
            />
          ))}
        </div>
      )}

      <div className="keyboard-hint-icon">
        <span className="hint-icon">⌨</span>
        <div className="hint-tooltip">
          <div>↑↓/jk navigate</div>
          <div>→/Enter open</div>
          <div>← back</div>
          <div>x select</div>
          <div>d delete</div>
          <div>⌘A select all</div>
          <div>/ search</div>
        </div>
      </div>
    </div>
  );
}

function BulkActions({
  count,
  confirmDelete,
  onDelete,
  onCancelDelete,
  onClearSelection,
}: {
  count: number;
  confirmDelete: boolean;
  onDelete: () => void;
  onCancelDelete: () => void;
  onClearSelection: () => void;
}) {
  return (
    <div className="bulk-actions">
      <span className="bulk-count">{count} selected</span>
      {confirmDelete ? (
        <>
          <span className="bulk-confirm-text">Delete {count} characters?</span>
          <button className="bulk-delete-confirm" onClick={onDelete}>
            Yes, delete
          </button>
          <button className="bulk-cancel" onClick={onCancelDelete}>
            Cancel
          </button>
        </>
      ) : (
        <>
          <button className="bulk-delete" onClick={onDelete}>
            🗑️ Delete
          </button>
          <button className="bulk-cancel" onClick={onClearSelection}>
            Clear selection
          </button>
        </>
      )}
    </div>
  );
}

function CreatingPlaceholder({ name, status }: { name: string; status: "splitting" | "pending" | "generating" | "done" | "error" }) {
  const statusText = {
    splitting: "Thinking...",
    pending: "Waiting...",
    generating: "Researching...",
    done: "Done!",
    error: "Failed to generate",
  }[status];

  return (
    <div className={`character-list-item creating-placeholder ${status}`}>
      <div className="char-checkbox-placeholder" />
      <span className="char-list-emoji">
        {status === "splitting" || status === "generating" ? (
          <div className="creating-spinner-small" />
        ) : status === "error" ? (
          "❌"
        ) : status === "done" ? (
          "✓"
        ) : (
          "⏳"
        )}
      </span>
      <div className="char-list-info">
        <div className="char-list-name">{name}</div>
        <div className={`char-list-bio creating-status ${status}`}>{statusText}</div>
      </div>
    </div>
  );
}

function CharacterListItem({
  char,
  index,
  focused,
  selected,
  onSelect,
  onToggle,
}: {
  char: CharacterOutput;
  index: number;
  focused: boolean;
  selected: boolean;
  onSelect: () => void;
  onToggle: () => void;
}) {
  return (
    <div
      data-index={index}
      className={`character-list-item ${focused ? "focused" : ""} ${selected ? "selected" : ""}`}
      onClick={onSelect}
    >
      <input
        type="checkbox"
        checked={selected}
        onChange={(e) => {
          e.stopPropagation();
          onToggle();
        }}
        onClick={(e) => e.stopPropagation()}
        className="char-checkbox"
      />
      <span className="char-list-emoji">{char.emoji}</span>
      <div className="char-list-info">
        <div className="char-list-name">{char.name}</div>
        <div className="char-list-bio">{char.bio}</div>
      </div>
    </div>
  );
}

