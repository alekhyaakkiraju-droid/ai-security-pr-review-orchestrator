"""Tiny print helpers so each graph node is easy to follow in the terminal."""

import json

from pydantic import BaseModel


def banner(title: str) -> None:
    print("\n" + "=" * 64)
    print(title)
    print("=" * 64)


def show(label: str, data) -> None:
    print(f"\n{label}")
    if isinstance(data, BaseModel):
        data = data.model_dump()
    print(json.dumps(data, indent=2, default=str))
