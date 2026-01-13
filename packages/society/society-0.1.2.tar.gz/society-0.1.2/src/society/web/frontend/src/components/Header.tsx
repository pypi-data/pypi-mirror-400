import { useState, useRef, useEffect } from "react";

interface HeaderProps {
  onBack?: () => void;
  apiKeySource?: "local" | "server" | null;
  apiKeyPreview?: string;
  onClearApiKey?: () => void;
}

export function Header({ onBack, apiKeySource, apiKeyPreview, onClearApiKey }: HeaderProps) {
  const [showSettings, setShowSettings] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setShowSettings(false);
      }
    }
    if (showSettings) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [showSettings]);

  return (
    <header className="header">
      {onBack && (
        <button className="back-btn" onClick={onBack}>
          ← Back
        </button>
      )}
      <h1>🎭 society</h1>
      <div className="header-spacer" />
      {apiKeySource && (
        <div className="settings-menu" ref={menuRef}>
          <button
            className="settings-btn"
            onClick={() => setShowSettings(!showSettings)}
            title="Settings"
          >
            ⚙
          </button>
          {showSettings && (
            <div className="settings-dropdown">
              <div className="settings-item">
                <span className="settings-label">API Key</span>
                <span className="settings-value">{apiKeyPreview}</span>
              </div>
              <div className="settings-source">
                {apiKeySource === "server" ? "Set from local env" : "Stored in browser"}
              </div>
              {apiKeySource === "local" && onClearApiKey && (
                <button className="settings-clear" onClick={onClearApiKey}>
                  Clear
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </header>
  );
}

