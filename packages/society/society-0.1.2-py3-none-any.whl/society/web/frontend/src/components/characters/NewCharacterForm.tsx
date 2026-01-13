import { useState } from "react";

interface Props {
  onCreate: (prompt: string) => void;
  onCancel: () => void;
}

export function NewCharacterForm({ onCreate, onCancel }: Props) {
  const [prompt, setPrompt] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!prompt.trim()) return;
    onCreate(prompt);
  }

  return (
    <div className="new-character-form">
      <h2>✨ Create New Character</h2>
      <p className="form-desc">
        Enter a name or description of a person (real or fictional). We'll research them and build a
        detailed profile for simulation.
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-section">
          <label className="form-label">Who should we research?</label>
          <textarea
            className="prompt-input"
            placeholder="e.g. Elon Musk, Ada Lovelace, Sherlock Holmes, a grumpy barista named Tony..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={4}
            autoFocus
          />
          <div className="prompt-hint">
            Real people work best — we'll search the web for interviews, writings, and context.
          </div>
        </div>

        <div className="form-actions">
          <button type="button" className="cancel-btn" onClick={onCancel}>
            Cancel
          </button>
          <button type="submit" className="start-btn" disabled={!prompt.trim()}>
            🔍 Research & Create
          </button>
        </div>
      </form>
    </div>
  );
}

