from __future__ import annotations

from collections import defaultdict
from html import escape

import streamlit as st

from dice_cube_component import render_dice_cube
from ludo_board_component import render_ludo_board
from ludo_engine import ALL_COLORS, COLORS_BY_COUNT, COLOR_LABELS, LudoGame


PAGE_CSS = """
<style>
    :root {
        --ink: #2e241a;
        --line: rgba(72, 48, 24, 0.12);
        --shadow: rgba(56, 34, 16, 0.12);
        --panel-top: rgba(255, 252, 246, 0.98);
        --panel-bottom: rgba(245, 232, 212, 0.94);
        --red: #d7524c;
        --green: #30955f;
        --yellow: #c79b32;
        --blue: #477ed0;
        --info: #57708a;
        --success: #3c7c54;
        --warning: #b4842d;
        --error: #984941;
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(212, 127, 76, 0.15), transparent 32%),
            radial-gradient(circle at bottom right, rgba(76, 145, 112, 0.12), transparent 32%),
            linear-gradient(180deg, #f7f0e3 0%, #eddfc7 100%);
        color: var(--ink);
        font-family: "Trebuchet MS", "Segoe UI", sans-serif;
    }
    @media (min-width: 980px) {
        [data-testid="stAppViewContainer"] {
            overflow: hidden;
        }
        .block-container {
            height: calc(100vh - 0.4rem);
            overflow: hidden;
        }
        div[data-testid="column"]:has(.left-panel-anchor) {
            height: calc(100vh - 0.8rem);
            padding-right: 0.95rem;
            border-right: 1px solid rgba(94, 66, 36, 0.18);
        }
        div[data-testid="column"]:has(.right-panel-anchor) {
            height: calc(100vh - 0.8rem);
            overflow-y: auto;
            overflow-x: hidden;
            padding-left: 0.95rem;
            padding-right: 0.35rem;
            scrollbar-gutter: stable;
        }
        div[data-testid="column"]:has(.right-panel-anchor)::-webkit-scrollbar {
            width: 0.6rem;
        }
        div[data-testid="column"]:has(.right-panel-anchor)::-webkit-scrollbar-thumb {
            background: rgba(110, 81, 49, 0.35);
            border-radius: 999px;
            border: 2px solid rgba(247, 240, 227, 0.95);
        }
        div[data-testid="column"]:has(.right-panel-anchor)::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.26);
            border-radius: 999px;
        }
    }
    .left-panel-anchor,
    .right-panel-anchor {
        display: none;
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
        max-width: 1540px;
        padding-top: 0.32rem;
        padding-bottom: 0.3rem;
    }
    [data-testid="stHorizontalBlock"] {
        align-items: start;
    }
    [data-testid="stVerticalBlock"] {
        gap: 0.28rem;
    }
    .side-card {
        border: 1px solid rgba(46, 36, 26, 0.08);
        border-radius: 18px;
        background: linear-gradient(180deg, var(--panel-top), var(--panel-bottom));
        box-shadow: 0 12px 26px var(--shadow);
        padding: 0.7rem 0.8rem;
        margin-bottom: 0.4rem;
    }
    .title-kicker,
    .card-label {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.66rem;
        color: rgba(64, 47, 31, 0.7);
        margin-bottom: 0.18rem;
    }
    .title-card h1 {
        margin: 0;
        font-size: clamp(1.4rem, 2vw, 2rem);
        line-height: 1.04;
    }
    .title-card p,
    .mini-note {
        margin: 0.14rem 0 0;
        color: rgba(46, 36, 26, 0.72);
        font-size: 0.76rem;
        line-height: 1.18;
    }
    .status-text {
        font-size: 0.88rem;
        font-weight: 700;
        line-height: 1.2;
        color: #3f2d1c;
        margin-bottom: 0.28rem;
    }
    .meta-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.38rem;
    }
    .meta-item {
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.7);
        border-radius: 12px;
        padding: 0.42rem 0.5rem;
    }
    .meta-item span {
        display: block;
        font-size: 0.62rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: rgba(64, 47, 31, 0.6);
        margin-bottom: 0.08rem;
    }
    .meta-item strong {
        display: block;
        font-size: 0.83rem;
    }
    .dice-card {
        text-align: center;
        border-radius: 14px;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.64);
        padding: 0.38rem 0.48rem;
        margin-bottom: 0.24rem;
    }
    .dice-label {
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-size: 0.62rem;
        color: rgba(64, 47, 31, 0.64);
    }
    .dice-value {
        font-size: 1.72rem;
        line-height: 1;
        font-weight: 900;
        margin: 0.12rem 0 0.04rem;
        color: #432d1b;
    }
    .dice-subtext {
        font-size: 0.68rem;
        color: rgba(46, 36, 26, 0.72);
    }
    .notice-card {
        border-radius: 14px;
        padding: 0.56rem 0.68rem;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.82);
        box-shadow: 0 8px 18px rgba(88, 60, 32, 0.05);
        margin-bottom: 0.38rem;
    }
    .notice-card.info { border-left: 5px solid var(--info); }
    .notice-card.success { border-left: 5px solid var(--success); }
    .notice-card.warning { border-left: 5px solid var(--warning); }
    .notice-card.error { border-left: 5px solid var(--error); }
    .notice-card strong {
        display: block;
        margin-bottom: 0.12rem;
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: rgba(64, 47, 31, 0.74);
    }
    .notice-card p {
        margin: 0;
        font-size: 0.8rem;
        line-height: 1.24;
    }
    div.stButton > button {
        min-height: 2.28rem;
        border-radius: 12px;
        font-weight: 700;
        background: linear-gradient(180deg, #fffaf1, #ecd9b8);
        color: #3c2816;
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
        background: linear-gradient(180deg, #c97f3e, #985a26);
        color: #fff8f1;
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
    .section-note {
        border: 1px dashed rgba(74, 52, 29, 0.18);
        border-radius: 12px;
        padding: 0.44rem 0.55rem;
        background: rgba(255, 255, 255, 0.46);
        color: rgba(46, 36, 26, 0.76);
        font-size: 0.76rem;
        line-height: 1.22;
        margin-bottom: 0.35rem;
    }
    .summary-card {
        border-radius: 16px;
        padding: 0.52rem 0.62rem;
        margin-bottom: 0.38rem;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.66);
        box-shadow: 0 10px 20px rgba(88, 60, 32, 0.05);
    }
    .summary-head {
        display: flex;
        justify-content: space-between;
        gap: 0.8rem;
        align-items: center;
        margin-bottom: 0.35rem;
    }
    .summary-head strong {
        font-size: 0.78rem;
    }
    .summary-head span {
        font-size: 0.62rem;
        color: rgba(64, 47, 31, 0.7);
    }
    .summary-table {
        display: grid;
        gap: 0.26rem;
        margin-bottom: 0.42rem;
    }
    .summary-row {
        display: grid;
        grid-template-columns: 0.7rem minmax(0, 1.3fr) repeat(3, minmax(0, 0.62fr)) 2.4rem;
        gap: 0.28rem;
        align-items: center;
        border-radius: 10px;
        padding: 0.28rem 0.38rem;
        background: rgba(255, 255, 255, 0.74);
        border: 1px solid rgba(74, 52, 29, 0.08);
        font-size: 0.66rem;
    }
    .summary-row.current {
        box-shadow: 0 0 0 2px rgba(216, 165, 84, 0.2);
    }
    .summary-row.header {
        background: transparent;
        border: none;
        padding: 0 0.15rem 0.1rem;
        color: rgba(64, 47, 31, 0.6);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.58rem;
    }
    .swatch {
        width: 0.7rem;
        height: 0.7rem;
        border-radius: 999px;
    }
    .swatch.red { background: var(--red); }
    .swatch.green { background: var(--green); }
    .swatch.yellow { background: var(--yellow); }
    .swatch.blue { background: var(--blue); }
    .who {
        font-weight: 700;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .turn-pill {
        justify-self: end;
        border-radius: 999px;
        padding: 0.16rem 0.34rem;
        background: rgba(214, 166, 83, 0.18);
        color: #7d5525;
        font-size: 0.58rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .history-box {
        margin: 0;
        padding: 0.46rem 0.56rem;
        border-radius: 12px;
        background: #221811;
        color: #f4eadb;
        font-family: Consolas, "Courier New", monospace;
        font-size: 0.66rem;
        line-height: 1.18;
        white-space: pre-wrap;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .button-row {
        display: flex;
        gap: 0.42rem;
    }
    .button-row > div {
        flex: 1;
    }
    .setup-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.26rem 0.42rem;
    }
    .input-chip {
        font-size: 0.62rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: rgba(64, 47, 31, 0.62);
        margin-bottom: 0.08rem;
    }
    div[data-testid="stTextInput"],
    div[data-testid="stSelectbox"] {
        margin-bottom: 0.12rem;
    }
    div[data-testid="stWidgetLabel"] {
        margin-bottom: 0.1rem;
    }
    div[data-testid="stTextInput"] label p,
    div[data-testid="stSelectbox"] label p {
        font-size: 0.68rem;
    }
    @media (max-width: 980px) {
        .block-container {
            overflow: visible;
            height: auto;
        }
    }
</style>
"""


def ensure_state() -> None:
    if "player_count" not in st.session_state:
        st.session_state.player_count = 4

    default_colors = COLORS_BY_COUNT[4]
    for index, color in enumerate(default_colors):
        color_key = f"setup_player_color_{index}"
        name_key = f"setup_player_name_{index}"
        if color_key not in st.session_state:
            st.session_state[color_key] = color
        if name_key not in st.session_state:
            st.session_state[name_key] = f"Player {index + 1}"

    if "game" not in st.session_state:
        st.session_state.game = build_game_from_setup()
    if "last_board_event_id" not in st.session_state:
        st.session_state.last_board_event_id = None
    if "roll_nonce" not in st.session_state:
        st.session_state.roll_nonce = 0
    if "notice" not in st.session_state:
        st.session_state.notice = (
            "info",
            "Roll the die to begin. When a move is possible, the valid token lights up on the board.",
        )


def setup_players() -> tuple[list[str], list[str], str | None]:
    player_count = int(st.session_state.player_count)
    colors: list[str] = []
    names: list[str] = []
    for index in range(player_count):
        color = str(st.session_state.get(f"setup_player_color_{index}", "")).strip().lower()
        name = str(st.session_state.get(f"setup_player_name_{index}", "")).strip()
        colors.append(color)
        names.append(name or f"Player {index + 1}")

    if any(color not in ALL_COLORS for color in colors):
        return colors, names, "Choose a valid color for each player."
    if len(set(colors)) != len(colors):
        return colors, names, "Each player needs a different color."
    return colors, names, None


def build_game_from_setup() -> LudoGame:
    colors, names, setup_error = setup_players()
    if setup_error is not None:
        fallback_colors = list(COLORS_BY_COUNT[st.session_state.player_count])
        fallback_names = [f"Player {index + 1}" for index in range(st.session_state.player_count)]
        return LudoGame.new_game(
            player_count=st.session_state.player_count,
            player_names=fallback_names,
            player_colors=fallback_colors,
        )
    return LudoGame.new_game(
        player_count=st.session_state.player_count,
        player_names=names,
        player_colors=colors,
    )


def set_notice(level: str, message: str) -> None:
    st.session_state.notice = (level, message)


def mode_caption(player_count: int) -> str:
    if player_count == 2:
        return "Pick any two colors for a head-to-head game."
    if player_count == 3:
        return "Pick any three colors for a three-player game."
    return "All four colors are active in four-player mode."


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
        "current_color": None if game.game_over else game.current_player.color,
    }


def history_text(game: LudoGame, limit: int = 5) -> str:
    if not game.history:
        return "No moves yet."
    recent = game.history[-limit:]
    recent.reverse()
    return "\n".join(f"- {line}" for line in recent)


def summary_markup(game: LudoGame) -> str:
    rows = [
        """
        <div class="summary-row header">
            <div></div>
            <div>Player</div>
            <div>Yard</div>
            <div>Board</div>
            <div>Home</div>
            <div></div>
        </div>
        """
    ]
    for index, player in enumerate(game.players):
        current = " current" if not game.game_over and index == game.current_player_index else ""
        turn_badge = "<span class='turn-pill'>Turn</span>" if current else ""
        rows.append(
            f"""
            <div class="summary-row{current}">
                <div class="swatch {escape(player.color)}"></div>
                <div class="who">{escape(player.name)}</div>
                <div>{player.yard_count}</div>
                <div>{player.board_count}</div>
                <div>{player.finished_count}</div>
                <div>{turn_badge}</div>
            </div>
            """
        )

    return f"""
    <div class="summary-card">
        <div class="summary-head">
            <strong>Players</strong>
            <span>Latest moves below</span>
        </div>
        <div class="summary-table">
            {''.join(rows)}
        </div>
        <pre class="history-box">{escape(history_text(game, limit=5))}</pre>
    </div>
    """


def run_app() -> None:
    st.set_page_config(page_title="Classic Ludo", page_icon="L", layout="wide")
    ensure_state()

    game: LudoGame = st.session_state.game
    st.markdown(PAGE_CSS, unsafe_allow_html=True)

    left_col, right_col = st.columns([1.08, 0.92], gap="medium")
    board_event: dict[str, object] | None = None

    with left_col:
        st.markdown('<div class="left-panel-anchor"></div>', unsafe_allow_html=True)
        board_event = render_ludo_board(
            serialize_board_state(game),
            key="classic_ludo_board",
            height=700,
        )

    if board_event is not None:
        event_id = board_event.get("event_id")
        if event_id is not None and event_id != st.session_state.last_board_event_id:
            st.session_state.last_board_event_id = event_id
            if board_event.get("kind") == "token" and board_event.get("token_id"):
                success, message = game.move_token(str(board_event["token_id"]))
                set_notice("success" if success else "warning", message)
            st.rerun()

    notice_level, notice_message = st.session_state.notice

    with right_col:
        st.markdown('<div class="right-panel-anchor"></div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="side-card title-card">
                <div class="title-kicker">Offline Local Multiplayer</div>
                <h1>Classic Ludo</h1>
                <p>Everything you need stays visible on this screen while the board remains square on the left.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

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

        last_roll_display = game.active_roll if game.active_roll is not None else game.last_roll
        st.markdown(
            f"""
            <div class="side-card">
                <div class="dice-card">
                    <div class="dice-label">Dice</div>
                    <div class="dice-value">{escape(str(last_roll_display if last_roll_display is not None else '--'))}</div>
                    <div class="dice-subtext">{escape('Waiting for a token move.' if game.active_roll is not None else 'Ready for the next roll.')}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_dice_cube(
            {
                "value": int(last_roll_display or 1),
                "roll_nonce": int(st.session_state.roll_nonce),
            },
            key="classic_ludo_dice",
            height=185,
        )

        roll_col, new_col = st.columns(2, gap="small")
        with roll_col:
            if st.button("Roll Dice", type="primary", use_container_width=True, disabled=game.game_over or game.active_roll is not None):
                success, message = game.roll_dice()
                set_notice("success" if success else "warning", message)
                if success:
                    st.session_state.roll_nonce += 1
                st.rerun()

        with new_col:
            if st.button("New Match", use_container_width=True):
                colors, names, setup_error = setup_players()
                if setup_error is not None:
                    set_notice("warning", setup_error)
                else:
                    st.session_state.game = LudoGame.new_game(
                        player_count=st.session_state.player_count,
                        player_names=names,
                        player_colors=colors,
                    )
                    st.session_state.last_board_event_id = None
                    st.session_state.roll_nonce = 0
                    set_notice("info", "Fresh match ready. Roll to start the opening turn.")
                st.rerun()

        st.markdown(
            """
            <div class="side-card">
                <div class="card-label">Match Setup</div>
                <div class="mini-note" style="margin:0;">
                    Change player count or names here, then apply the setup to a fresh match.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(f"<div class='section-note'>{escape(mode_caption(st.session_state.player_count))}</div>", unsafe_allow_html=True)
        st.selectbox("Players", [2, 3, 4], key="player_count", format_func=lambda value: f"{value} players")
        for index in range(int(st.session_state.player_count)):
            name_col, color_col = st.columns([1.5, 1], gap="small")
            with name_col:
                st.text_input(f"Player {index + 1} name", key=f"setup_player_name_{index}")
            with color_col:
                st.selectbox(
                    f"Player {index + 1} color",
                    options=list(ALL_COLORS),
                    key=f"setup_player_color_{index}",
                    format_func=lambda value: COLOR_LABELS[str(value)],
                )
        colors, _, setup_error = setup_players()
        if setup_error is None:
            chosen_labels = ", ".join(COLOR_LABELS[color] for color in colors)
            st.markdown(f"<div class='section-note'>Selected colors: {escape(chosen_labels)}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='section-note'>{escape(setup_error)}</div>", unsafe_allow_html=True)
        if st.button("Apply Setup To New Match", use_container_width=True):
            colors, names, setup_error = setup_players()
            if setup_error is not None:
                set_notice("warning", setup_error)
            else:
                st.session_state.game = LudoGame.new_game(
                    player_count=st.session_state.player_count,
                    player_names=names,
                    player_colors=colors,
                )
                st.session_state.last_board_event_id = None
                st.session_state.roll_nonce = 0
                set_notice("info", f"Started a new {st.session_state.player_count}-player match.")
            st.rerun()
        st.markdown(
            """
            <div class="section-note">
                Roll a 6 to leave the yard. Exact rolls are required to reach home. Captures and finishes grant another roll.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(summary_markup(game), unsafe_allow_html=True)


__all__ = ["run_app"]
