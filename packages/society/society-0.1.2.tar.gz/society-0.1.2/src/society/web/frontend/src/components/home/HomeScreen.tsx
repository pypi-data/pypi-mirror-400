import type { RunSummary, CharacterOutput } from "../../types";
import { RunsList } from "./RunsList";
import { CharacterList } from "../characters/CharacterList";

export type HomeTab = "runs" | "characters";

interface Props {
  runs: RunSummary[];
  characters: CharacterOutput[];
  activeTab: HomeTab;
  onTabChange: (tab: HomeTab) => void;
  onSelectRun: (name: string) => void;
  onNewRun: () => void;
  onSelectCharacter: (uuid: string) => void;
  onCreateCharacter: (prompt: string) => Promise<void>;
  onReloadCharacters: () => Promise<void>;
  onBulkDelete: (uuids: string[]) => void;
  initialFocusUuid?: string;
  checkedCharacters: Set<string>;
  onCheckedChange: (checked: Set<string>) => void;
}

export function HomeScreen({
  runs,
  characters,
  activeTab,
  onTabChange,
  onSelectRun,
  onNewRun,
  onSelectCharacter,
  onCreateCharacter,
  onReloadCharacters,
  onBulkDelete,
  initialFocusUuid,
  checkedCharacters,
  onCheckedChange,
}: Props) {
  return (
    <div className="home-screen">
      <div className="home-tabs">
        <button
          className={`home-tab ${activeTab === "runs" ? "active" : ""}`}
          onClick={() => onTabChange("runs")}
        >
          Simulations
        </button>
        <button
          className={`home-tab ${activeTab === "characters" ? "active" : ""}`}
          onClick={() => onTabChange("characters")}
        >
          Characters
        </button>
      </div>

      {activeTab === "runs" ? (
        <RunsList runs={runs} onSelectRun={onSelectRun} onNewRun={onNewRun} />
      ) : (
        <CharacterList
          characters={characters}
          onSelect={onSelectCharacter}
          onCreate={onCreateCharacter}
          onReload={onReloadCharacters}
          onBulkDelete={onBulkDelete}
          initialFocusUuid={initialFocusUuid}
          checkedCharacters={checkedCharacters}
          onCheckedChange={onCheckedChange}
        />
      )}
    </div>
  );
}

