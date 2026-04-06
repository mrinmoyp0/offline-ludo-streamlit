from __future__ import annotations

from collections import defaultdict
from html import escape

import streamlit as st

from ludo_board_component import render_ludo_board
from ludo_engine import COLORS_BY_COUNT, COLOR_LABELS, LudoGame


PAGE_CSS = """
<style>
    :root {
        --ink: #2c231a;
        --panel: rgba(255, 249, 239, 0.93);
        --panel-strong: rgba(255, 252, 246, 0.97);
        --line: rgba(74, 52, 29, 0.12);
        --shadow: rgba(70, 44, 21, 0.12);
        --red: #d6524f;
        --green: #34905c;
        --yellow: #bf9631;
        --blue: #3f77c6;
        --info: #58708c;
        --success: #3c7b54;
        --warning: #b07f26;
        --error: #9c4a42;
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(214, 130, 79, 0.16), transparent 32%),
            radial-gradient(circle at bottom right, rgba(85, 160, 120, 0.14), transparent 30%),
            linear-gradient(180deg, #f7f0e3, #eee1cb 100%);
        color: var(--ink);
        font-family: "Trebuchet MS", "Segoe UI", sans-serif;
    }
    header[data-testid="stHeader"],
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"],
    #MainMenu,
    footer {
        display: none;
    }
    .block-container {
        padding-top: 0.45rem;
        padding-bottom: 0.6rem;
        max-width: 1600px;
    }
    [data-testid="stHorizontalBlock"] {
        align-items: start;
    }
    .side-card {
        border: 1px solid rgba(44, 35, 26, 0.08);
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(255, 252, 246, 0.96), rgba(246, 234, 214, 0.92));
        box-shadow: 0 18px 38px var(--shadow);
        padding: 1rem 1.05rem;
        margin-bottom: 0.75rem;
    }
    .title-card h1 {
        margin: 0;
        font-size: clamp(1.9rem, 2.6vw, 2.7rem);
        line-height: 1.02;
        letter-spacing: 0.01em;
    }
    .title-kicker,
    .card-label {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.74rem;
        color: rgba(70, 50, 29, 0.72);
        margin-bottom: 0.3rem;
    }
    .title-card p,
    .mini-note {
        margin: 0.38rem 0 0;
        color: rgba(44, 35, 26, 0.72);
        font-size: 0.94rem;
        line-height: 1.38;
    }
    .status-text {
        font-size: 1.08rem;
        font-weight: 700;
        line-height: 1.3;
        color: #402d1a;
        margin-bottom: 0.65rem;
    }
    .meta-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.55rem;
    }
    .meta-item {
        border: 1px solid var(--line);
        background: var(--panel-strong);
        border-radius: 15px;
        padding: 0.6rem 0.72rem;
    }
    .meta-item span {
        display: block;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: rgba(70, 50, 29, 0.62);
        margin-bottom: 0.16rem;
    }
    .meta-item strong {
        display: block;
        font-size: 0.98rem;
    }
    .dice-card {
        border: 1px solid var(--line);
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.6);
        padding: 0.8rem 0.9rem;
        text-align: center;
        margin-bottom: 0.75rem;
    }
    .dice-label {
        text-transform: uppercase;
        letter-spacing: 0.11em;
        font-size: 0.72rem;
        color: rgba(70, 50, 29, 0.66);
    }
    .dice-value {
        font-size: 2.8rem;
        line-height: 1;
        font-weight: 800;
        margin: 0.35rem 0 0.15rem;
        color: #442d18;
    }
    .dice-subtext {
        font-size: 0.9rem;
        color: rgba(44, 35, 26, 0.72);
    }
    .notice-card {
        border-radius: 18px;
        padding: 0.82rem 0.95rem;
        border: 1px solid var(--line);
        background: var(--panel-strong);
        box-shadow: 0 14px 28px rgba(88, 60, 32, 0.06);
        margin-bottom: 0.75rem;
    }
    .notice-card.info { border-left: 5px solid var(--info); }
    .notice-card.success { border-left: 5px solid var(--success); }
    .notice-card.warning { border-left: 5px solid var(--warning); }
    .notice-card.error { border-left: 5px solid var(--error); }
    .notice-card strong {
        display: block;
        margin-bottom: 0.2rem;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: rgba(70, 50, 29, 0.75);
    }
    .notice-card p {
        margin: 0;
        font-size: 0.95rem;
        line-height: 1.35;
    }
    div.stButton > button {
        min-height: 2.75rem;
        border-radius: 15px;
        font-weight: 700;
        background: linear-gradient(180deg, #fff9f0, #ecd9b8);
        color: #3d2917;
        border: 1px solid rgba(92, 62, 34, 0.22);
        box-shadow:
            0 10px 18px rgba(92, 62, 34, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.65);
        transition: transform 120ms ease, box-shadow 120ms ease, filter 120ms ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(180deg, #fffdf7, #f0dfbf);
        border-color: rgba(139, 90, 43, 0.35);
        transform: translateY(-1px);
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(180deg, #c67e3b, #965724);
        color: #fff9f4;
        border-color: rgba(88, 48, 20, 0.38);
        box-shadow:
            0 12px 22px rgba(96, 57, 27, 0.18),
            inset 0 1px 0 rgba(255, 236, 208, 0.28);
    }
    div.stButton > button:disabled {
        opacity: 1;
        box-shadow: none;
        background: linear-gradient(180deg, #efe4d4, #e2d2bb);
        color: rgba(60, 40, 23, 0.56);
        border-color: rgba(92, 62, 34, 0.12);
        cursor: not-allowed;
    }
    .player-card {
        border-radius: 18px;
        padding: 0.82rem 0.9rem;
        margin-bottom: 0.6rem;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.64);
        box-shadow: 0 12px 24px rgba(88, 60, 32, 0.05);
    }
    .player-card.current {
        box-shadow: 0 0 0 2px rgba(215, 162, 82, 0.26), 0 14px 28px rgba(88, 60, 32, 0.08);
    }
    .player-card.red { border-left: 5px solid var(--red); }
    .player-card.green { border-left: 5px solid var(--green); }
    .player-card.yellow { border-left: 5px solid var(--yellow); }
    .player-card.blue { border-left: 5px solid var(--blue); }
    .player-title {
        display: flex;
        justify-content: space-between;
        gap: 0.8rem;
        align-items: center;
        margin-bottom: 0.35rem;
    }
    .player-title strong {
        font-size: 1rem;
    }
    .player-title span {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: rgba(70, 50, 29, 0.65);
    }
    .player-metrics {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.45rem;
        margin-top: 0.45rem;
    }
    .player-metrics div {
        border-radius: 12px;
        padding: 0.48rem 0.55rem;
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid rgba(74, 52, 29, 0.08);
    }
    .player-metrics span {
        display: block;
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: rgba(70, 50, 29, 0.58);
        margin-bottom: 0.12rem;
    }
    .player-metrics strong {
        display: block;
        font-size: 0.92rem;
    }
    .history-box {
        margin: 0;
        padding: 0.82rem 0.9rem;
        border-radius: 16px;
        background: #241912;
        color: #f4eadb;
        font-family: Consolas, "Courier New", monospace;
        font-size: 0.86rem;
        line-height: 1.45;
        max-height: 225px;
        overflow-y: auto;
        white-space: pre-wrap;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .mode-note {
        border: 1px dashed rgba(74, 52, 29, 0.18);
        border-radius: 14px;
        padding: 0.72rem 0.8rem;
        background: rgba(255, 255, 255, 0.45);
        color: rgba(44, 35, 26, 0.76);
        font-size: 0.88rem;
        line-height: 1.35;
    }
</style>
"""


def ensure_state() -> None:
    if "player_count" not in st.session_state:
        st.session_state.player_count = 4

    defaults = {
        "red": "Player 1",
        "green": "Player 2",
        "yellow": "Player 3",
        "blue": "Player 4",
    }
    for color, default_name in defaults.items():
        key = f"setup_name_{color}"
        if key not in st.session_state:
            st.session_state[key] = default_name

    if "game" not in st.session_state:
        st.session_state.game = build_game_from_setup()
    if "last_board_event_id" not in st.session_state:
        st.session_state.last_board_event_id = None
    if "notice" not in st.session_state:
        st.session_state.notice = (
            "info",
            "Roll the die to begin. When a token can move, it glows on the board.",
        )


def build_game_from_setup() -> LudoGame:
    colors = COLORS_BY_COUNT[st.session_state.player_count]
    names: list[str] = []
    for index, color in enumerate(colors):
        raw_name = str(st.session_state.get(f"setup_name_{color}", "")).strip()
        names.append(raw_name or f"Player {index + 1}")
    return LudoGame.new_game(player_count=st.session_state.player_count, player_names=names)


def set_notice(level: str, message: str) -> None:
    st.session_state.notice = (level, message)


def mode_caption(player_count: int) -> str:
    if player_count == 2:
        return "Two-player mode uses Red and Yellow, which sit on opposite corners of the board."
    if player_count == 3:
        return "Three-player mode uses Red, Green, and Yellow."
    return "Four-player mode fills the full classic board."


def notice_markup(level: str, message: str) -> str:
    titles = {
        "info": "Game Note",
        "success": "Move Accepted",
        "warning": "Check This",
        "error": "Action Blocked",
    }
    title = titles.get(level, "Notice")
    return f"""
    <div class="notice-card {escape(level)}">
        <strong>{escape(title)}</strong>
        <p>{escape(message)}</p>
    </div>
    """


def serialize_board_state(game: LudoGame) -> dict[str, object]:
    placements: dict[str, list[dict[str, object]]] = defaultdict(list)
    movable_tokens = game.movable_token_ids()

    for player in game.players:
        for token in player.tokens:
            placements[game.token_cell_id(player.color, token)].append(
                {
                    "id": token.id,
                    "label": str(token.number + 1),
                    "color": player.color,
                    "player_name": player.name,
                    "movable": token.id in movable_tokens,
                    "last_moved": game.last_move is not None and game.last_move.token_id == token.id,
                }
            )

    ordered_placements: dict[str, list[dict[str, object]]] = {}
    for cell_id in sorted(placements):
        ordered_placements[cell_id] = sorted(placements[cell_id], key=lambda token: str(token["id"]))

    return {
        "placements": ordered_placements,
        "active_colors": [player.color for player in game.players],
        "player_names": {player.color: player.name for player in game.players},
        "current_color": None if game.game_over else game.current_player.color,
    }


def player_card_markup(game: LudoGame, index: int) -> str:
    player = game.players[index]
    current_class = " current" if not game.game_over and index == game.current_player_index else ""
    return f"""
    <div class="player-card {escape(player.color)}{current_class}">
        <div class="player-title">
            <strong>{escape(player.name)}</strong>
            <span>{escape(COLOR_LABELS[player.color])}</span>
        </div>
        <div class="player-metrics">
            <div>
                <span>Yard</span>
                <strong>{player.yard_count}</strong>
            </div>
            <div>
                <span>Board</span>
                <strong>{player.board_count}</strong>
            </div>
            <div>
                <span>Home</span>
                <strong>{player.finished_count}</strong>
            </div>
        </div>
    </div>
    """


def history_text(game: LudoGame) -> str:
    if not game.history:
        return "No moves yet."
    recent = game.history[-10:]
    recent.reverse()
    return "\n".join(f"- {line}" for line in recent)


def run_app() -> None:
    st.set_page_config(page_title="Offline Ludo", page_icon="L", layout="wide")
    ensure_state()

    game: LudoGame = st.session_state.game
    st.markdown(PAGE_CSS, unsafe_allow_html=True)

    notice_level, notice_message = st.session_state.notice
    board_col, side_col = st.columns([1.78, 0.92], gap="large")
    board_event: dict[str, object] | None = None

    with board_col:
        st.markdown(
            """
            <div class="side-card title-card">
                <div class="title-kicker">Offline Streamlit Board Game</div>
                <h1>Classic Ludo</h1>
                <p>The board is rendered with a custom HTML/CSS/JS component while all dice and turn logic stay in Python.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div class='mini-note'>Roll from the panel on the right. When a move is available, the board highlights the legal token or tokens for you to click.</div>", unsafe_allow_html=True)
        board_event = render_ludo_board(
            serialize_board_state(game),
            key="main_ludo_board",
            height=780,
        )

    if board_event is not None:
        event_id = board_event.get("event_id")
        if event_id is not None and event_id != st.session_state.last_board_event_id:
            st.session_state.last_board_event_id = event_id
            if board_event.get("kind") == "token" and board_event.get("token_id"):
                success, message = game.move_token(str(board_event["token_id"]))
                set_notice("success" if success else "warning", message)
            st.rerun()

    with side_col:
        st.markdown(
            f"""
            <div class="side-card">
                <div class="card-label">Turn Status</div>
                <div class="status-text">{escape(game.status)}</div>
                <div class="meta-grid">
                    <div class="meta-item">
                        <span>Current</span>
                        <strong>{escape(game.current_player.name)}</strong>
                    </div>
                    <div class="meta-item">
                        <span>Phase</span>
                        <strong>{escape('Move Token' if game.active_roll is not None else ('Match Over' if game.game_over else 'Roll Dice'))}</strong>
                    </div>
                    <div class="meta-item">
                        <span>Roll</span>
                        <strong>{escape(str(game.active_roll if game.active_roll is not None else game.last_roll or '--'))}</strong>
                    </div>
                    <div class="meta-item">
                        <span>Players</span>
                        <strong>{len(game.players)}</strong>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(notice_markup(notice_level, notice_message), unsafe_allow_html=True)

    with side_col:
        last_roll_display = game.active_roll if game.active_roll is not None else game.last_roll
        st.markdown(
            f"""
            <div class="side-card">
                <div class="dice-card">
                    <div class="dice-label">Latest Die</div>
                    <div class="dice-value">{escape(str(last_roll_display if last_roll_display is not None else '--'))}</div>
                    <div class="dice-subtext">{escape('Waiting for a token move.' if game.active_roll is not None else 'Ready for the next roll.')}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Roll Dice", type="primary", use_container_width=True, disabled=game.game_over or game.active_roll is not None):
            success, message = game.roll_dice()
            set_notice("success" if success else "warning", message)
            st.rerun()

        if st.button("Start New Match", use_container_width=True):
            st.session_state.game = build_game_from_setup()
            st.session_state.last_board_event_id = None
            set_notice("info", "Fresh match ready. Roll to start the opening turn.")
            st.rerun()

        st.markdown("<div class='mini-note'>Use the setup fields below when you want to switch between 2, 3, and 4 local players or change the displayed names.</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="side-card">
                <div class="card-label">Match Setup</div>
                <div class="mini-note" style="margin:0;">
                    Change the player count or names here, then launch a fresh match with the updated setup.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.selectbox("Players", [2, 3, 4], key="player_count", format_func=lambda value: f"{value} players")
        st.markdown(f"<div class='mode-note'>{escape(mode_caption(st.session_state.player_count))}</div>", unsafe_allow_html=True)
        for color in COLORS_BY_COUNT[st.session_state.player_count]:
            st.text_input(f"{COLOR_LABELS[color]} player", key=f"setup_name_{color}")
        if st.button("Apply Setup To New Match", use_container_width=True):
            st.session_state.game = build_game_from_setup()
            st.session_state.last_board_event_id = None
            set_notice("info", f"Started a new {st.session_state.player_count}-player match.")
            st.rerun()

        st.markdown(
            """
            <div class="side-card">
                <div class="card-label">Quick Rules</div>
                <div class="mini-note" style="margin:0;">
                    Roll a 6 to leave the yard. Exact rolls are required to reach home. Landing on an opponent outside a safe star sends that token back to its yard. A 6, a capture, or reaching home grants another roll.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with side_col:
        st.markdown(
            """
            <div class="side-card">
                <div class="card-label">Players</div>
                <div class="mini-note" style="margin:0;">
                    Yard counts waiting tokens, board counts active tokens, and home counts finished ones.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        for index in range(len(game.players)):
            st.markdown(player_card_markup(game, index), unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="side-card">
                <div class="card-label">Recent Moves</div>
                <pre class="history-box">{escape(history_text(game))}</pre>
            </div>
            """,
            unsafe_allow_html=True,
        )


__all__ = ["run_app"]
