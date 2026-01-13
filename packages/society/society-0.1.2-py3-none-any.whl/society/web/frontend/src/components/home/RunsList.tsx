import type { RunSummary } from "../../types";
import { EmptyState } from "../EmptyState";

interface Props {
  runs: RunSummary[];
  onSelectRun: (name: string) => void;
  onNewRun: () => void;
}

export function RunsList({ runs, onSelectRun, onNewRun }: Props) {
  return (
    <div className="home-screen-content">
      <div className="home-header">
        <button className="new-run-btn" onClick={onNewRun}>
          + New
        </button>
      </div>
      {runs.length === 0 ? (
        <EmptyState>No runs yet. Click "New Run" to start a simulation.</EmptyState>
      ) : (
        <div className="runs-list">
          {runs.map((run) => (
            <button key={run.name} className="run-item" onClick={() => onSelectRun(run.name)}>
              <div className="run-task">{run.task || run.name}</div>
              {run.people.length > 0 && <div className="run-meta">{run.people.join(", ")}</div>}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

