import type { CharacterInfo, Channel } from "../../types";

/** Convert name to slug matching Python ChatClient.slugify */
function slugify(name: string): string {
  return name.replace(/[^a-zA-Z0-9\s]/g, "").toLowerCase().replace(/ /g, "-");
}

interface Props {
  channels: Channel[];
  characters: CharacterInfo[];
  activeView: string;
  setActiveView: (view: string) => void;
}

export function Sidebar({ channels, characters, activeView, setActiveView }: Props) {
  // Filter out personal/journal channels (those with only 1 person)
  const groupChannels = channels.filter((c) => c.person_ids.length > 1);

  return (
    <aside className="sidebar">
      <SidebarSection header="Events">
        <SidebarButton active={activeView === "events"} onClick={() => setActiveView("events")}>
          Activity
        </SidebarButton>
      </SidebarSection>

      <SidebarSection header="Channels">
        {groupChannels.map((channel) => (
          <SidebarButton
            key={channel.name}
            className="channel-item"
            active={activeView === `chan-${channel.name}`}
            onClick={() => setActiveView(`chan-${channel.name}`)}
          >
            {channel.name}
          </SidebarButton>
        ))}
      </SidebarSection>

      <SidebarSection header="People">
        <SidebarButton
          className="person-item"
          active={activeView === "person-ceo"}
          onClick={() => setActiveView("person-ceo")}
        >
          <span>👔</span> CEO
        </SidebarButton>
        {characters.map((char) => {
          const slug = slugify(char.name);
          return (
            <SidebarButton
              key={char.uuid || char.name}
              className="person-item"
              active={activeView === `person-${slug}`}
              onClick={() => setActiveView(`person-${slug}`)}
            >
              <span>{char.emoji || "👤"}</span> {char.name}
            </SidebarButton>
          );
        })}
      </SidebarSection>
    </aside>
  );
}

function SidebarSection({ header, children }: { header: string; children: React.ReactNode }) {
  return (
    <div className="sidebar-section">
      <div className="section-header">▸ {header}</div>
      {children}
    </div>
  );
}

function SidebarButton({
  active,
  className = "",
  onClick,
  children,
}: {
  active: boolean;
  className?: string;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      className={`sidebar-item ${className} ${active ? "active" : ""}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

