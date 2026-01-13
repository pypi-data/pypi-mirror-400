import fcntl
import json
import re
import time
import uuid
from pathlib import Path

from society.datatypes import Channel, Message, Person


class ChatClient:
    """
    Client to a disk-backed chat workspace with multiple people and channels

    The metadata for people and channels is stored in a JSON file.
    Messages are appended to a JSONL file.

    If user_id is None, acts as admin view (sees all channels, can't send).
    """

    def __init__(self, run_dir: Path, user_id: uuid.UUID | None) -> None:
        self.run_dir = run_dir
        self.user_id = user_id

    @property
    def user(self) -> Person:
        if self.user_id is None:
            raise ValueError("No user set")
        return self._get_person_by_id(self.user_id)

    def list_channels(self) -> list[Channel]:
        """
        Channels this user is a member of (or all channels if no user)
        """
        _, channels = self._load_metadata()
        if self.user_id is None:
            return channels
        return [c for c in channels if self.user_id in c.person_ids]

    def list_people(self) -> list[Person]:
        """
        All people in the chat workspace
        """
        people, _ = self._load_metadata()
        return people

    def send_message(
        self,
        channel_name: str,
        text: str,
        t: float | None = None,
    ) -> Message:
        """
        Post a new message to a channel
        """
        channel = self._get_channel_by_name(channel_name)

        message = Message(
            id=uuid.uuid4(),
            person_id=self.user.id,
            person=self.user.name,
            t=t if t is not None else time.time(),
            channel_id=channel.id,
            channel=channel.name,
            text=text,
        )
        self._append_message(message)
        return message

    def get_messages(
        self,
        channel_name: str,
        since: float | None = None,
    ) -> list[Message]:
        """
        Get messages in a channel
        """
        channel_name = channel_name.lstrip("#")
        all_messages = self._load_messages()
        messages = [m for m in all_messages if m.channel == channel_name]
        if since is not None:
            messages = [m for m in messages if m.t > since]
        return sorted(messages, key=lambda m: m.t)

    def get_all_messages(
        self,
        since: float | None = None,
    ) -> list[Message]:
        """
        Get all messages the user can see
        """
        messages: list[Message] = []
        for channel in self.list_channels():
            messages.extend(self.get_messages(channel.name, since=since))
        return sorted(messages, key=lambda m: m.t)

    def create_channel(
        self,
        name: str,
        description: str,
        person_ids: list[uuid.UUID] | None = None,
    ) -> Channel:
        """
        Create a new channel
        """
        people, channels = self._load_metadata()
        if any(c.name == name for c in channels):
            raise ValueError(f"Channel '{name}' already exists")

        channel = Channel(
            id=uuid.uuid4(),
            name=name,
            description=description,
            person_ids=person_ids or [],
        )
        channels.append(channel)
        self._save_metadata(people, channels)
        return channel

    def add_person(self, person: Person) -> None:
        """
        Add a new person to the chat workspace
        """
        people, channels = self._load_metadata()
        if any(p.id == person.id for p in people):
            raise ValueError(f"Person {person.id} already exists")
        people.append(person)
        self._save_metadata(people, channels)

    def add_person_to_channel(
        self,
        person_id: uuid.UUID,
        channel_name: str,
    ) -> None:
        """Add a person to an existing channel."""
        people, channels = self._load_metadata()

        # Look up from all channels, not just user's channels
        channel_name = channel_name.lstrip("#")
        channel = next((c for c in channels if c.name == channel_name), None)
        if channel is None:
            raise ValueError(f"Channel '{channel_name}' not found")

        if person_id in channel.person_ids:
            return  # Already a member

        channel.person_ids.append(person_id)
        self._save_metadata(people, channels)

    def remove_person_from_channel(
        self,
        person_id: uuid.UUID,
        channel_name: str,
    ) -> None:
        """Remove a person from a channel. Users can only remove themselves."""
        if self.user_id is not None and person_id != self.user_id:
            raise ValueError("You can only remove yourself from a channel")

        people, channels = self._load_metadata()

        channel = self._get_channel_by_name(channel_name)
        if person_id not in channel.person_ids:
            return  # Not a member

        channel.person_ids.remove(person_id)
        self._save_metadata(people, channels)

    def format_channel(self, channel_name: str) -> str:
        """
        Format messages from a single channel as a readable transcript
        """
        channel = self._get_channel_by_name(channel_name)
        messages = self.get_messages(channel_name)
        person_id_to_name = {p.id: p.name for p in self.list_people()}
        people = [person_id_to_name[pid] for pid in channel.person_ids]

        lines: list[str] = []
        sep = "=" * 40
        lines.append(sep)
        lines.append(f"#{channel.name}")
        lines.append(sep)
        lines.append(f"People: {', '.join(people)}")
        lines.append("")

        if not messages:
            lines.append("(no messages)")
            lines.append("")
        else:
            for m in messages:
                lines.append(f"[{m.t:.1f}s] {m.person}")
                lines.append(m.text)
                lines.append("")

        return "\n".join(lines)

    def format(self) -> str:
        """
        Format all messages as a readable transcript, grouped by channel
        """
        lines: list[str] = []
        for channel in self.list_channels():
            lines.append(self.format_channel(channel.name))
        return "\n".join(lines)

    @staticmethod
    def slugify(name: str) -> str:
        """
        Convert a string to a lowercase slug, e.g. 'John Smith' -> 'john-smith',
        as well as handling punctuation, whitespace, and parenthesis.
        """
        return re.sub(r"[^a-zA-Z0-9\s]", "", name).lower().replace(" ", "-")

    @property
    def _metadata_path(self) -> Path:
        return self.run_dir / "chat_metadata.json"

    @property
    def _messages_path(self) -> Path:
        return self.run_dir / "chat_messages.jsonl"

    def _load_metadata(self) -> tuple[list[Person], list[Channel]]:
        if not self._metadata_path.exists():
            return [], []
        data = json.loads(self._metadata_path.read_text())
        people = [Person.model_validate(p) for p in data.get("people", [])]
        channels = [Channel.model_validate(c) for c in data.get("channels", [])]
        return people, channels

    def _save_metadata(
        self,
        people: list[Person],
        channels: list[Channel],
    ) -> None:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "people": [p.model_dump(mode="json") for p in people],
            "channels": [c.model_dump(mode="json") for c in channels],
        }
        self._metadata_path.write_text(json.dumps(data, indent=2))

    def _get_channel_by_name(self, name: str) -> Channel:
        name = name.lstrip("#")
        # Look up from ALL channels, not just user's channels
        _, channels = self._load_metadata()
        channel = next((c for c in channels if c.name == name), None)
        if channel is None:
            raise ValueError(f"Channel '{name}' not found")
        return channel

    def _get_person_by_id(self, id: uuid.UUID) -> Person:
        person = next((p for p in self.list_people() if p.id == id), None)
        if person is None:
            raise ValueError(f"Person {id} not found")
        return person

    def _append_message(self, message: Message) -> None:
        """
        Append a single message to the log (atomic with file lock)
        """
        with open(self._messages_path, "a") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(message.model_dump_json() + "\n")
            fcntl.flock(f, fcntl.LOCK_UN)

    def _load_messages(self) -> list[Message]:
        """
        Load all messages from disk
        """
        if not self._messages_path.exists():
            return []
        text = self._messages_path.read_text().strip()
        if not text:
            return []
        lines = text.split("\n")
        return [Message.model_validate_json(line) for line in lines]
