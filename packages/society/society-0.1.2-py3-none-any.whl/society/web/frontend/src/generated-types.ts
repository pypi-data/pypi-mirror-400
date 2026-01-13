// Auto-generated from society.datatypes using gen_types.py
import type { FromSchema } from "json-schema-to-ts";

const AgentEventSchema = {
  "description": "Event from agent streaming, serializable for IPC",
  "properties": {
    "kind": {
      "title": "Kind",
      "type": "string"
    },
    "person_name": {
      "title": "Person Name",
      "type": "string"
    },
    "time_s": {
      "title": "Time S",
      "type": "number"
    },
    "data": {
      "default": null,
      "title": "Data"
    }
  },
  "required": [
    "kind",
    "person_name",
    "time_s"
  ],
  "title": "AgentEvent",
  "type": "object"
} as const;

const AnswerSchema = {
  "properties": {
    "id": {
      "format": "uuid",
      "title": "Id",
      "type": "string"
    },
    "person_id": {
      "format": "uuid",
      "title": "Person Id",
      "type": "string"
    },
    "text": {
      "title": "Text",
      "type": "string"
    }
  },
  "required": [
    "id",
    "person_id",
    "text"
  ],
  "title": "Answer",
  "type": "object"
} as const;

const ChannelSchema = {
  "properties": {
    "id": {
      "format": "uuid",
      "title": "Id",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    },
    "description": {
      "title": "Description",
      "type": "string"
    },
    "person_ids": {
      "items": {
        "format": "uuid",
        "type": "string"
      },
      "title": "Person Ids",
      "type": "array"
    }
  },
  "required": [
    "id",
    "name",
    "description",
    "person_ids"
  ],
  "title": "Channel",
  "type": "object"
} as const;

const CharacterOutputSchema = {
  "properties": {
    "uuid": {
      "format": "uuid",
      "title": "Uuid",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    },
    "birth_year": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "title": "Birth Year"
    },
    "gender": {
      "title": "Gender",
      "type": "string"
    },
    "location": {
      "title": "Location",
      "type": "string"
    },
    "occupation": {
      "title": "Occupation",
      "type": "string"
    },
    "bio": {
      "title": "Bio",
      "type": "string"
    },
    "personality": {
      "title": "Personality",
      "type": "string"
    },
    "context": {
      "title": "Context",
      "type": "string"
    },
    "emoji": {
      "title": "Emoji",
      "type": "string"
    },
    "confidence": {
      "title": "Confidence",
      "type": "integer"
    }
  },
  "required": [
    "uuid",
    "name",
    "birth_year",
    "gender",
    "location",
    "occupation",
    "bio",
    "personality",
    "context",
    "emoji",
    "confidence"
  ],
  "title": "CharacterOutput",
  "type": "object"
} as const;

const MessageSchema = {
  "properties": {
    "id": {
      "format": "uuid",
      "title": "Id",
      "type": "string"
    },
    "person_id": {
      "format": "uuid",
      "title": "Person Id",
      "type": "string"
    },
    "person": {
      "title": "Person",
      "type": "string"
    },
    "t": {
      "title": "T",
      "type": "number"
    },
    "channel_id": {
      "format": "uuid",
      "title": "Channel Id",
      "type": "string"
    },
    "channel": {
      "title": "Channel",
      "type": "string"
    },
    "text": {
      "title": "Text",
      "type": "string"
    }
  },
  "required": [
    "id",
    "person_id",
    "person",
    "t",
    "channel_id",
    "channel",
    "text"
  ],
  "title": "Message",
  "type": "object"
} as const;

const PersonSchema = {
  "properties": {
    "id": {
      "format": "uuid",
      "title": "Id",
      "type": "string"
    },
    "name": {
      "title": "Name",
      "type": "string"
    },
    "bio": {
      "title": "Bio",
      "type": "string"
    },
    "role": {
      "default": "member",
      "enum": [
        "ceo",
        "member"
      ],
      "title": "Role",
      "type": "string"
    }
  },
  "required": [
    "id",
    "name",
    "bio"
  ],
  "title": "Person",
  "type": "object"
} as const;

const VoteSchema = {
  "properties": {
    "id": {
      "format": "uuid",
      "title": "Id",
      "type": "string"
    },
    "person_id": {
      "format": "uuid",
      "title": "Person Id",
      "type": "string"
    },
    "answer_id": {
      "format": "uuid",
      "title": "Answer Id",
      "type": "string"
    },
    "vote": {
      "enum": [
        "yes",
        "no",
        "unsure"
      ],
      "title": "Vote",
      "type": "string"
    }
  },
  "required": [
    "id",
    "person_id",
    "answer_id",
    "vote"
  ],
  "title": "Vote",
  "type": "object"
} as const;

export type AgentEvent = FromSchema<typeof AgentEventSchema>;

export type Answer = FromSchema<typeof AnswerSchema>;

export type Channel = FromSchema<typeof ChannelSchema>;

export type CharacterOutput = FromSchema<typeof CharacterOutputSchema>;

export type Message = FromSchema<typeof MessageSchema>;

export type Person = FromSchema<typeof PersonSchema>;

export type Vote = FromSchema<typeof VoteSchema>;
