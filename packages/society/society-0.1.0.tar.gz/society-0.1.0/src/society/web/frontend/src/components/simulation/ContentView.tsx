import type { RunDetail } from "../../types";
import { EventsView } from "./EventsView";
import { MessagesView } from "./MessagesView";
import { PersonCard } from "./PersonCard";
import { EmptyState } from "../EmptyState";

/** Convert name to slug matching Python ChatClient.slugify */
function slugify(name: string): string {
  return name.replace(/[^a-zA-Z0-9\s]/g, "").toLowerCase().replace(/ /g, "-");
}

interface Props {
  run: RunDetail;
  activeView: string;
}

export function ContentView({ run, activeView }: Props) {
  if (activeView === "events") {
    return <EventsView events={run.events} />;
  }

  if (activeView.startsWith("chan-")) {
    const channel = activeView.slice(5);
    const messages = run.messages.filter((m) => m.channel === channel);
    // Only show voting for #general channel
    const votingEvents = channel === "general" ? run.events : [];
    return <MessagesView messages={messages} votingEvents={votingEvents} />;
  }

  if (activeView.startsWith("person-")) {
    const slug = activeView.slice(7);
    if (slug === "ceo") {
      return (
        <PersonCard
          name="CEO"
          role="Executive"
          bio="The CEO who initiates tasks and receives final answers."
          emoji="👔"
        />
      );
    }
    const char = run.characters.find((c) => slugify(c.name) === slug);
    if (char) {
      // Find journal messages for this person (channel name matches slugified person name)
      const journalMessages = run.messages.filter((m) => m.channel === slug);
      return (
        <>
          <PersonCard
            name={char.name}
            role={char.occupation || char.role || "Team Member"}
            bio={char.bio}
            emoji={char.emoji || "👤"}
          />
          {journalMessages.length > 0 && (
            <div className="journal-section">
              <h3 className="journal-header">Journal</h3>
              <MessagesView messages={journalMessages} />
            </div>
          )}
        </>
      );
    }
  }

  return <EmptyState>Select a view from the sidebar</EmptyState>;
}

