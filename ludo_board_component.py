from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


_COMPONENT_PATH = Path(__file__).parent / "components" / "ludo_board"
_LUDO_BOARD = components.declare_component("classic_offline_ludo_board", path=str(_COMPONENT_PATH))


def render_ludo_board(
    state: dict[str, Any],
    key: str = "classic_offline_ludo_board",
    height: int = 820,
) -> dict[str, Any] | None:
    return _LUDO_BOARD(
        board_state=state,
        height=height,
        key=key,
        default=None,
    )
