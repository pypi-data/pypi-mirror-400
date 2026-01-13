import { useState, useEffect } from "react";
import type { CharacterOutput } from "../../types";

interface Props {
  character: CharacterOutput;
  onDelete: () => void;
  onBack: () => void;
}

export function CharacterDetailView({ character, onDelete, onBack }: Props) {
  const [showFullContext, setShowFullContext] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  // Keyboard navigation
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      // Don't handle if user is typing in an input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      if (confirmDelete) {
        if (e.key === "Enter" || e.key === "d") {
          e.preventDefault();
          onDelete();
        } else if (e.key === "Escape") {
          e.preventDefault();
          setConfirmDelete(false);
        }
      } else {
        if (e.key === "ArrowLeft" || e.key === "Escape") {
          e.preventDefault();
          onBack();
        } else if (e.key === "d") {
          e.preventDefault();
          setConfirmDelete(true);
        }
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onBack, onDelete, confirmDelete]);

  return (
    <div className="character-detail">
      <div className="char-detail-header">
        <span className="char-detail-emoji">{character.emoji}</span>
        <div className="char-detail-info">
          <h2>{character.name}</h2>
          <div className="char-detail-meta">
            <span>{character.occupation}</span>
            <span className="meta-sep">•</span>
            <span>{character.location}</span>
            {character.birth_year && (
              <>
                <span className="meta-sep">•</span>
                <span>Born {character.birth_year}</span>
              </>
            )}
          </div>
        </div>
        <ConfidenceBadge confidence={character.confidence} />
      </div>

      <div className="char-detail-sections">
        <Section title="📝 Bio">{character.bio}</Section>
        <Section title="🧠 Personality">{character.personality}</Section>
        <Section title="📚 Research Context">
          <div className={`context-content ${showFullContext ? "expanded" : ""}`}>
            <p>{character.context}</p>
          </div>
          {character.context.length > 500 && (
            <button className="context-toggle" onClick={() => setShowFullContext(!showFullContext)}>
              {showFullContext ? "Show less" : "Show more"}
            </button>
          )}
        </Section>
      </div>

      <div className="char-detail-actions">
        {confirmDelete ? (
          <div className="delete-confirm">
            <span>Delete {character.name}?</span>
            <button className="confirm-yes" onClick={onDelete}>
              Yes, delete
            </button>
            <button className="confirm-no" onClick={() => setConfirmDelete(false)}>
              Cancel
            </button>
          </div>
        ) : (
          <button className="delete-btn" onClick={() => setConfirmDelete(true)}>
            🗑️ Delete Character
          </button>
        )}
      </div>
    </div>
  );
}

function ConfidenceBadge({ confidence }: { confidence: number }) {
  return (
    <div className="char-detail-confidence">
      <div className="confidence-label">Research Confidence</div>
      <div className="confidence-bar">
        <div className="confidence-fill" style={{ width: `${confidence}%` }} />
      </div>
      <div className="confidence-value">{confidence}%</div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="char-section">
      <h3>{title}</h3>
      {typeof children === "string" ? <p>{children}</p> : children}
    </div>
  );
}

