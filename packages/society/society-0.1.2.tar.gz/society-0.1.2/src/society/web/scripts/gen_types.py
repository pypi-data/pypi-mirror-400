"""
Generate TS types from Python types using json-schema-to-ts
"""

import json
import typing as T
from pathlib import Path

from pydantic import BaseModel, TypeAdapter

from society import datatypes

OUTPUT = Path(__file__).parent.parent / "frontend/src/generated-types.ts"


def main() -> None:
    all_models = tuple(
        v
        for v in datatypes.__dict__.values()
        if isinstance(v, type) and issubclass(v, BaseModel) and v is not BaseModel
    )

    schema = TypeAdapter(T.Union[all_models]).json_schema()
    defs = schema.get("$defs", {})

    lines = [
        "// Auto-generated from society.datatypes using gen_types.py",
        'import type { FromSchema } from "json-schema-to-ts";',
        "",
    ]

    for name, defn in defs.items():
        lines.append(f"const {name}Schema = {json.dumps(defn, indent=2)} as const;")
        lines.append("")

    for name, defn in defs.items():
        lines.append(f"export type {name} = FromSchema<typeof {name}Schema>;")
        lines.append("")

    OUTPUT.write_text("\n".join(lines))
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
