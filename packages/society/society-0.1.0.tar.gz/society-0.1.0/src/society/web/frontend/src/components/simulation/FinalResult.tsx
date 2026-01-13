interface Props {
  answer: string;
}

export function FinalResult({ answer }: Props) {
  return (
    <div className="final-result">
      <div className="final-result-title">⚔️ Final Answer: {answer}</div>
    </div>
  );
}

