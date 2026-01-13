import { useState } from "react";
import type { RunDetail, CharacterInfo } from "../../types";
import { Sidebar } from "./Sidebar";
import { ContentView } from "./ContentView";
import { FinalResult } from "./FinalResult";

/** Convert name to slug matching Python ChatClient.slugify */
function slugify(name: string): string {
  return name.replace(/[^a-zA-Z0-9\s]/g, "").toLowerCase().replace(/ /g, "-");
}

interface Props {
  run: RunDetail;
  activeView: string;
  setActiveView: (view: string) => void;
  onStop?: () => void;
  onContinue?: (message: string, duration: number) => Promise<void>;
  onExport?: () => void;
}

export function SimulationView({ run, activeView, setActiveView, onStop, onContinue, onExport }: Props) {
  const isLive = !run.final_answer;
  const [continueMessage, setContinueMessage] = useState("");
  const [continueDuration, setContinueDuration] = useState(60);
  const [isContinuing, setIsContinuing] = useState(false);

  const showContinueForm = !isLive && activeView === "chan-general" && onContinue;

  async function handleContinue() {
    if (!continueMessage.trim() || !onContinue) return;
    setIsContinuing(true);
    try {
      await onContinue(continueMessage, continueDuration);
      setContinueMessage("");
    } finally {
      setIsContinuing(false);
    }
  }

  return (
    <div className="sim-container">
      <Sidebar
        channels={run.channels}
        characters={run.characters}
        activeView={activeView}
        setActiveView={setActiveView}
      />
      <div className="main-content">
        <div className="content-header">
          <span className="content-title">{getViewTitle(activeView, run.characters)}</span>
          <div className="header-actions">
            {onExport && (
              <button className="export-btn" onClick={onExport}>
                Export
              </button>
            )}
            {isLive && onStop && (
              <button className="stop-btn" onClick={onStop}>
                ■ Stop
              </button>
            )}
            <span className={`sim-status ${isLive ? "live" : "complete"}`}>
              {isLive ? "Live" : "Complete"}
            </span>
          </div>
        </div>
        <div className="content-body">
          <ContentView run={run} activeView={activeView} />
          {run.final_answer && activeView.startsWith("chan-") && (
            <FinalResult answer={run.final_answer} />
          )}
          {showContinueForm && (
            <div className="continue-form">
              <div className="continue-input-row">
                <input
                  type="text"
                  className="continue-message-input"
                  placeholder="Type a message to continue the conversation..."
                  value={continueMessage}
                  onChange={(e) => setContinueMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleContinue();
                    }
                  }}
                  disabled={isContinuing}
                />
                <div className="continue-duration">
                  <input
                    type="number"
                    className="continue-duration-input"
                    value={continueDuration}
                    onChange={(e) => setContinueDuration(Math.max(1, parseInt(e.target.value) || 60))}
                    min={1}
                    disabled={isContinuing}
                  />
                  <span className="continue-duration-label">sec</span>
                </div>
                <button
                  className="continue-btn"
                  onClick={handleContinue}
                  disabled={!continueMessage.trim() || isContinuing}
                >
                  {isContinuing ? "..." : "Continue"}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function getViewTitle(activeView: string, characters: CharacterInfo[]): string {
  if (activeView === "events") return "📋 Events";
  if (activeView.startsWith("chan-")) {
    const channel = activeView.slice(5);
    return `# ${channel}`;
  }
  if (activeView.startsWith("person-")) {
    const slug = activeView.slice(7);
    if (slug === "ceo") return "👤 CEO";
    const char = characters.find((c) => slugify(c.name) === slug);
    return char ? `👤 ${char.name}` : `👤 ${slug}`;
  }
  return activeView;
}

