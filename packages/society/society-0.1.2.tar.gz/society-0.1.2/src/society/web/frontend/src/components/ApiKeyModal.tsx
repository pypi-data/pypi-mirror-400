import { useState } from "react";

interface Props {
  onSave: (key: string) => void;
}

function validateApiKey(key: string): string | null {
  const trimmed = key.trim();
  if (!trimmed.startsWith("AIza")) {
    return "Invalid key prefix ('AIza')";
  }
  if (trimmed.length !== 39) {
    return `Invalid key length`;
  }
  return null;
}

export function ApiKeyModal({ onSave }: Props) {
  const [key, setKey] = useState("");

  const validationError = key.trim() ? validateApiKey(key) : null;
  const isValid = key.trim() && !validationError;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (isValid) {
      onSave(key.trim());
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content api-key-modal">
        <h2>Enter your Gemini API Key</h2>
        <p className="modal-description">
          The key is stored locally in your browser and sent to Google's API per request. <br />
          Get one free at{" "}
          <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer">
            aistudio.google.com
          </a>
        </p>
        <form onSubmit={handleSubmit}>
          <input
            type="password"
            className="api-key-input"
            placeholder="AIza..."
            value={key}
            onChange={(e) => setKey(e.target.value)}
            autoFocus
          />
          {validationError && (
            <div className="api-key-error">{validationError}</div>
          )}
          <button type="submit" className="api-key-submit" disabled={!isValid}>
            Save
          </button>
        </form>
      </div>
    </div>
  );
}
