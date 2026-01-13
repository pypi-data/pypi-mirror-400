interface Props {
  name: string;
  role: string;
  bio: string;
  emoji: string;
}

export function PersonCard({ name, role, bio, emoji }: Props) {
  return (
    <div className="person-card">
      <div className="person-card-header">
        <span className="person-name">
          {emoji} {name}
        </span>
        <span className="person-role">({role})</span>
      </div>
      <div className="person-bio">{bio}</div>
    </div>
  );
}

