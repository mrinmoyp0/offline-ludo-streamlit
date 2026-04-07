from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit.components.v1 as components


_COMPONENT_PATH = Path(__file__).parent / "components" / "dice_cube"
_DICE_CUBE = components.declare_component("classic_ludo_dice_cube", path=str(_COMPONENT_PATH))


def render_dice_cube(
    state: dict[str, Any],
    key: str = "classic_ludo_dice_cube",
    height: int = 185,
) -> None:
    _DICE_CUBE(
        dice_state=state,
        height=height,
        key=key,
        default=None,
    )
