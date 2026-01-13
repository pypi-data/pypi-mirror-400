import type { AgentEvent } from "../../types";
import { EmptyState } from "../EmptyState";

interface Props {
  events: AgentEvent[];
}

interface FormattedEvent {
  time: number;
  name: string;
  content: string;
}

interface EventData {
  tool_name?: string;
  args?: Record<string, unknown>;
  output?: string;
}

export function EventsView({ events }: Props) {
  const formattedEvents = events
    .map(formatEvent)
    .filter((e): e is FormattedEvent => e !== null);

  if (formattedEvents.length === 0) {
    return <EmptyState>No events recorded</EmptyState>;
  }

  return (
    <div className="events-list">
      {formattedEvents.map((event, i) => (
        <div key={i} className="event-row">
          <span className="event-time">[{event.time.toFixed(1)}s]</span>
          <span className="event-name">{event.name}</span>
          <span className="event-content">{event.content}</span>
        </div>
      ))}
    </div>
  );
}

function formatEvent(event: AgentEvent): FormattedEvent | null {
  const data = (event.data || {}) as EventData;

  if (event.kind === "tool_result") {
    const toolName = data.tool_name as string;
    const args = (data.args as Record<string, unknown>) || {};

    if (toolName === "wait") {
      return { time: event.time_s, name: event.person_name, content: "⏳ Waiting..." };
    }
    if (toolName === "send_message") {
      const channel = args.channel as string;
      return { time: event.time_s, name: event.person_name, content: `💬 Posted to #${channel}` };
    }
    if (toolName === "read_channel") {
      const channel = args.channel as string;
      return { time: event.time_s, name: event.person_name, content: `📖 Read #${channel}` };
    }
    if (toolName === "create_channel") {
      const name = args.name as string;
      return { time: event.time_s, name: event.person_name, content: `📢 Created #${name}` };
    }
    if (toolName === "join_channel") {
      const channel = args.channel as string;
      return { time: event.time_s, name: event.person_name, content: `➡️ Joined #${channel}` };
    }
    if (toolName === "leave_channel") {
      const channel = args.channel as string;
      return { time: event.time_s, name: event.person_name, content: `⬅️ Left #${channel}` };
    }
    if (toolName === "propose_answer") {
      const text = ((args.text as string) || "").slice(0, 40);
      return { time: event.time_s, name: event.person_name, content: `💡 Proposed: ${text}...` };
    }
    if (toolName === "vote_on_answer") {
      const vote = args.vote as string;
      const emoji = { yes: "✅", no: "❌", unsure: "🤔" }[vote] || "❓";
      return { time: event.time_s, name: event.person_name, content: `${emoji} Voted ${vote}` };
    }
    return { time: event.time_s, name: event.person_name, content: `🔧 ${toolName}` };
  }

  if (event.kind === "builtin_tool_call") {
    const toolName = data.tool_name as string;
    const args = (data.args as Record<string, unknown>) || {};
    if (toolName === "web_search") {
      const query = ((args.query as string) || "").slice(0, 30);
      return { time: event.time_s, name: event.person_name, content: `🔍 Searched: ${query}` };
    }
    return { time: event.time_s, name: event.person_name, content: `🔧 ${toolName}` };
  }

  if (event.kind === "agent_run_result") {
    const output = data.output as string;
    if (output !== "done") {
      return { time: event.time_s, name: event.person_name, content: `🏁 Ended: ${output}` };
    }
    return null;
  }

  if (event.kind === "simulation_end") {
    return { time: event.time_s, name: event.person_name, content: "🎉 Simulation Complete" };
  }

  return null;
}

