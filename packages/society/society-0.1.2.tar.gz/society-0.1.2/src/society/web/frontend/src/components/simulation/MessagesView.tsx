import { useMemo } from "react";
import type { Message, AgentEvent } from "../../types";
import { EmptyState } from "../EmptyState";

interface Props {
  messages: Message[];
  votingEvents?: AgentEvent[];
}

interface Proposal {
  id: string;
  time: number;
  proposer: string;
  text: string;
  votes: { person: string; vote: "yes" | "no" | "unsure"; time: number }[];
}

type TimelineItem =
  | { type: "message"; data: Message }
  | { type: "proposal"; data: Proposal };

export function MessagesView({ messages, votingEvents = [] }: Props) {
  // Extract proposals and votes from events
  const proposals = useMemo(() => {
    const proposalMap = new Map<string, Proposal>();

    for (const event of votingEvents) {
      if (event.kind !== "tool_result") continue;
      const data = event.data as { tool_name?: string; args?: Record<string, unknown>; result?: unknown };

      if (data.tool_name === "propose_answer") {
        const result = data.result as { id?: string; text?: string } | undefined;
        if (result?.id) {
          proposalMap.set(result.id, {
            id: result.id,
            time: event.time_s,
            proposer: event.person_name,
            text: result.text || "",
            votes: [],
          });
        }
      }

      if (data.tool_name === "vote_on_answer") {
        const args = data.args || {};
        const answerId = args.answer_id as string;
        const vote = args.vote as "yes" | "no" | "unsure";
        const proposal = proposalMap.get(answerId);
        if (proposal) {
          // Update or add vote
          const existingIdx = proposal.votes.findIndex((v) => v.person === event.person_name);
          if (existingIdx >= 0) {
            proposal.votes[existingIdx] = { person: event.person_name, vote, time: event.time_s };
          } else {
            proposal.votes.push({ person: event.person_name, vote, time: event.time_s });
          }
        }
      }
    }

    return Array.from(proposalMap.values());
  }, [votingEvents]);

  // Create interleaved timeline
  const timeline = useMemo(() => {
    const items: TimelineItem[] = [
      ...messages.map((m) => ({ type: "message" as const, data: m })),
      ...proposals.map((p) => ({ type: "proposal" as const, data: p })),
    ];
    return items.sort((a, b) => {
      const timeA = a.type === "message" ? a.data.t : a.data.time;
      const timeB = b.type === "message" ? b.data.t : b.data.time;
      return timeA - timeB;
    });
  }, [messages, proposals]);

  if (timeline.length === 0) {
    return <EmptyState>No messages in this channel</EmptyState>;
  }

  return (
    <div className="messages-list">
      {timeline.map((item) =>
        item.type === "message" ? (
          <div key={item.data.id} className="message">
            <div className="msg-header">
              <span className="msg-author">{item.data.person}</span>
              <span className="msg-time">{item.data.t.toFixed(1)}s</span>
            </div>
            <div className="msg-text">{item.data.text}</div>
          </div>
        ) : (
          <ProposalCard key={`proposal-${item.data.id}`} proposal={item.data} />
        ),
      )}
    </div>
  );
}

function ProposalCard({ proposal }: { proposal: Proposal }) {
  const yesVotes = proposal.votes.filter((v) => v.vote === "yes");
  const noVotes = proposal.votes.filter((v) => v.vote === "no");
  const unsureVotes = proposal.votes.filter((v) => v.vote === "unsure");

  return (
    <div className="proposal-card">
      <div className="proposal-header">
        <span className="proposal-icon">💡</span>
        <span className="proposal-author">{proposal.proposer}</span>
        <span className="proposal-label">proposed an answer</span>
        <span className="msg-time">{proposal.time.toFixed(1)}s</span>
      </div>
      <div className="proposal-text">{proposal.text}</div>
      {proposal.votes.length > 0 && (
        <div className="proposal-votes">
          {yesVotes.length > 0 && (
            <span className="vote-group vote-yes" title={yesVotes.map((v) => v.person).join(", ")}>
              ✅ {yesVotes.length}
            </span>
          )}
          {noVotes.length > 0 && (
            <span className="vote-group vote-no" title={noVotes.map((v) => v.person).join(", ")}>
              ❌ {noVotes.length}
            </span>
          )}
          {unsureVotes.length > 0 && (
            <span className="vote-group vote-unsure" title={unsureVotes.map((v) => v.person).join(", ")}>
              🤔 {unsureVotes.length}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

