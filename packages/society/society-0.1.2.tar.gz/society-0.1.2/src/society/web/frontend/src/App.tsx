import { useState, useEffect, useCallback } from "react";
import "./App.css";
import type { RunSummary, RunDetail, CharacterOutput, SimulationMode } from "./types";
import * as api from "./api";
import { getApiKey, setApiKey, clearApiKey, fetchConfig } from "./api";
import {
  Header,
  LoadingState,
  HomeScreen,
  NewRunForm,
  CharacterDetailView,
  NewCharacterForm,
  SimulationView,
  ApiKeyModal,
  type HomeTab,
} from "./components";

type AppView = "home" | "run" | "newRun" | "character" | "newCharacter";

function App() {
  // undefined = still checking, null = no key, "local"/"server" = has key
  const [apiKeySource, setApiKeySource] = useState<"local" | "server" | null | undefined>(
    () => getApiKey() ? "local" : undefined
  );
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [characters, setCharacters] = useState<CharacterOutput[]>([]);
  const [selectedRun, setSelectedRun] = useState<RunDetail | null>(null);
  const [selectedRunName, setSelectedRunName] = useState<string | null>(null);
  const [selectedCharacter, setSelectedCharacter] = useState<CharacterOutput | null>(null);
  const [lastFocusedCharUuid, setLastFocusedCharUuid] = useState<string | null>(null);
  const [checkedCharacters, setCheckedCharacters] = useState<Set<string>>(new Set());
  const [activeView, setActiveView] = useState<string>("events");
  const [appView, setAppView] = useState<AppView>("home");
  const [homeTab, setHomeTab] = useState<HomeTab>("runs");
  const [loading, setLoading] = useState(true);

  // Check if API key is available from server env (only if not in localStorage)
  useEffect(() => {
    if (apiKeySource === undefined) {
      fetchConfig().then((config) => {
        setApiKeySource(config.has_api_key ? "server" : null);
      });
    }
  }, [apiKeySource]);

  function handleSaveApiKey(key: string) {
    setApiKey(key);
    setApiKeySource("local");
  }

  function handleClearApiKey() {
    clearApiKey();
    setApiKeySource(null);
  }

  // Get masked preview of API key
  const localKey = getApiKey();
  const apiKeyPreview = localKey ? `${localKey.slice(0, 8)}...` : "Server env";

  const loadRuns = useCallback(async () => {
    try {
      setRuns(await api.fetchRuns());
    } catch (err) {
      console.error("Failed to fetch runs:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadCharacters = useCallback(async () => {
    try {
      setCharacters(await api.fetchCharacters());
    } catch (err) {
      console.error("Failed to fetch characters:", err);
    }
  }, []);

  const refreshRun = useCallback(async (runName: string) => {
    try {
      setSelectedRun(await api.fetchRun(runName));
    } catch {
      // Ignore refresh errors
    }
  }, []);

  useEffect(() => {
    loadRuns();
    loadCharacters();
  }, [loadRuns, loadCharacters]);

  // Auto-refresh when viewing a run that's still in progress
  useEffect(() => {
    if (!selectedRunName || selectedRun?.final_answer) return;
    const interval = setInterval(() => refreshRun(selectedRunName), 2000);
    return () => clearInterval(interval);
  }, [selectedRunName, selectedRun?.final_answer, refreshRun]);

  async function selectRun(runName: string, retries = 5) {
    setLoading(true);
    setSelectedRunName(runName);
    setAppView("run");
    try {
      const data = await api.fetchRun(runName);
      setSelectedRun(data);
      setActiveView("chan-general");
      setLoading(false);
    } catch {
      if (retries > 0) {
        setTimeout(() => selectRun(runName, retries - 1), 1000);
        return;
      }
      setLoading(false);
    }
  }

  function goHome() {
    setSelectedRun(null);
    setSelectedRunName(null);
    setSelectedCharacter(null);
    setLastFocusedCharUuid(null);
    setActiveView("events");
    setAppView("home");
    loadRuns();
    loadCharacters();
  }

  function goBackToCharacterList() {
    setSelectedCharacter(null);
    setAppView("home");
    setHomeTab("characters");
    loadCharacters();
  }

  async function selectCharacter(uuid: string) {
    setLoading(true);
    setLastFocusedCharUuid(uuid);
    try {
      setSelectedCharacter(await api.fetchCharacter(uuid));
      setAppView("character");
    } catch (err) {
      console.error("Failed to fetch character:", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateCharacter(prompt: string): Promise<void> {
    await api.createCharacter(prompt);
    await loadCharacters();
  }

  async function handleDeleteCharacter(uuid: string) {
    try {
      await api.deleteCharacter(uuid);
      goHome();
    } catch (err) {
      console.error("Failed to delete character:", err);
    }
  }

  async function handleBulkDeleteCharacters(uuids: string[]) {
    try {
      await Promise.all(uuids.map(api.deleteCharacter));
      loadCharacters();
    } catch (err) {
      console.error("Failed to delete characters:", err);
    }
  }

  async function handleStartRun(chars: string[], mode: SimulationMode, task: string, votingStart: number, duration: number | null) {
    try {
      const data = await api.startRun(chars, mode, task, votingStart, duration);
      setAppView("home");
      if (data.runName) selectRun(data.runName);
    } catch (err) {
      console.error("Failed to start run:", err);
    }
  }

  async function handleStopRun() {
    if (!selectedRunName) return;
    try {
      await api.stopRun(selectedRunName);
      // Refresh to show stopped state
      await refreshRun(selectedRunName);
    } catch (err) {
      console.error("Failed to stop run:", err);
    }
  }

  async function handleContinueRun(message: string, duration: number) {
    if (!selectedRunName) return;
    try {
      await api.continueRun(selectedRunName, message, duration);
      // Start auto-refresh to show new messages
      // The existing refresh interval will pick up changes
    } catch (err) {
      console.error("Failed to continue run:", err);
    }
  }

  function handleExportRun() {
    if (!selectedRunName) return;
    // Trigger download by opening the export URL
    window.open(`/api/runs/${selectedRunName}/export`, "_blank");
  }

  const loadingMessage = selectedRunName
    ? "Starting simulation..."
    : appView === "newCharacter"
      ? "Researching character... this may take a minute"
      : "Loading...";

  if (loading) {
    return (
      <>
        <Header onBack={appView !== "home" ? goHome : undefined} />
        <LoadingState message={loadingMessage} />
      </>
    );
  }

  if (apiKeySource === null) {
    return (
      <>
        <Header onBack={undefined} />
        <ApiKeyModal onSave={handleSaveApiKey} />
      </>
    );
  }

  // Still checking for API key
  if (apiKeySource === undefined) {
    return (
      <>
        <Header onBack={undefined} />
        <LoadingState message="Loading..." />
      </>
    );
  }

  return (
    <>
      <Header
        onBack={appView !== "home" ? goHome : undefined}
        apiKeySource={apiKeySource ?? undefined}
        apiKeyPreview={apiKeyPreview}
        onClearApiKey={handleClearApiKey}
      />
      {appView === "run" && selectedRun ? (
        <SimulationView
          run={selectedRun}
          activeView={activeView}
          setActiveView={setActiveView}
          onStop={handleStopRun}
          onContinue={handleContinueRun}
          onExport={handleExportRun}
        />
      ) : appView === "newRun" ? (
        <NewRunForm onStart={handleStartRun} onCancel={goHome} />
      ) : appView === "character" && selectedCharacter ? (
        <CharacterDetailView
          character={selectedCharacter}
          onDelete={() => handleDeleteCharacter(selectedCharacter.uuid)}
          onBack={goBackToCharacterList}
        />
      ) : appView === "newCharacter" ? (
        <NewCharacterForm onCreate={handleCreateCharacter} onCancel={goHome} />
      ) : (
        <HomeScreen
          runs={runs}
          characters={characters}
          activeTab={homeTab}
          onTabChange={setHomeTab}
          initialFocusUuid={lastFocusedCharUuid ?? undefined}
          checkedCharacters={checkedCharacters}
          onCheckedChange={setCheckedCharacters}
          onSelectRun={(name) => selectRun(name)}
          onNewRun={() => setAppView("newRun")}
          onSelectCharacter={selectCharacter}
          onCreateCharacter={handleCreateCharacter}
          onReloadCharacters={loadCharacters}
          onBulkDelete={handleBulkDeleteCharacters}
        />
      )}
    </>
  );
}

export default App;
