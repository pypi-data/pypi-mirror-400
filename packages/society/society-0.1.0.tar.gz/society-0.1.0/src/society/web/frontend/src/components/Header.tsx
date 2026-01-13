export function Header({ onBack }: { onBack?: () => void }) {
  return (
    <header className="header">
      {onBack && (
        <button className="back-btn" onClick={onBack}>
          ← Back
        </button>
      )}
      <h1>🎭 society</h1>
    </header>
  );
}

