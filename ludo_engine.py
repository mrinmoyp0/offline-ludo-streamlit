from __future__ import annotations

from dataclasses import dataclass, field
from random import randint


COLORS_BY_COUNT: dict[int, tuple[str, ...]] = {
    2: ("red", "yellow"),
    3: ("red", "green", "yellow"),
    4: ("red", "green", "yellow", "blue"),
}

COLOR_LABELS: dict[str, str] = {
    "red": "Red",
    "green": "Green",
    "yellow": "Yellow",
    "blue": "Blue",
}

START_INDICES: dict[str, int] = {
    "red": 0,
    "green": 13,
    "yellow": 26,
    "blue": 39,
}

SAFE_TRACK_INDICES = {0, 8, 13, 21, 26, 34, 39, 47}
FINISH_PROGRESS = 56


@dataclass(frozen=True)
class MoveOption:
    token_id: str
    color: str
    token_number: int
    roll: int
    from_progress: int
    to_progress: int
    spawns: bool = False
    finishes: bool = False


@dataclass
class TokenState:
    id: str
    number: int
    progress: int = -1


@dataclass
class PlayerState:
    color: str
    name: str
    tokens: list[TokenState]

    @property
    def finished_count(self) -> int:
        return sum(token.progress == FINISH_PROGRESS for token in self.tokens)

    @property
    def yard_count(self) -> int:
        return sum(token.progress == -1 for token in self.tokens)

    @property
    def board_count(self) -> int:
        return sum(0 <= token.progress < FINISH_PROGRESS for token in self.tokens)


@dataclass(frozen=True)
class LastMove:
    token_id: str
    color: str
    roll: int
    from_cell: str
    to_cell: str
    captured_ids: tuple[str, ...] = ()
    finished: bool = False


@dataclass
class LudoGame:
    players: list[PlayerState]
    current_player_index: int = 0
    active_roll: int | None = None
    last_roll: int | None = None
    consecutive_sixes: int = 0
    status: str = ""
    game_over: bool = False
    winner_color: str | None = None
    history: list[str] = field(default_factory=list)
    last_move: LastMove | None = None

    @classmethod
    def new_game(cls, player_count: int = 4, player_names: list[str] | None = None) -> "LudoGame":
        colors = COLORS_BY_COUNT.get(player_count)
        if colors is None:
            raise ValueError("Ludo supports only 2, 3, or 4 players.")

        provided_names = list(player_names or [])
        players: list[PlayerState] = []
        for index, color in enumerate(colors):
            name = provided_names[index].strip() if index < len(provided_names) else ""
            players.append(
                PlayerState(
                    color=color,
                    name=name or f"Player {index + 1}",
                    tokens=[TokenState(id=f"{color}_{number}", number=number) for number in range(4)],
                )
            )

        opener = players[0]
        return cls(
            players=players,
            status=f"{opener.name} ({COLOR_LABELS[opener.color]}) is ready to roll.",
        )

    @property
    def current_player(self) -> PlayerState:
        return self.players[self.current_player_index]

    def legal_moves(self) -> list[MoveOption]:
        if self.game_over or self.active_roll is None:
            return []

        player = self.current_player
        moves: list[MoveOption] = []
        for token in player.tokens:
            destination = self._destination_progress(token.progress, self.active_roll)
            if destination is None:
                continue
            moves.append(
                MoveOption(
                    token_id=token.id,
                    color=player.color,
                    token_number=token.number,
                    roll=self.active_roll,
                    from_progress=token.progress,
                    to_progress=destination,
                    spawns=token.progress == -1 and destination == 0,
                    finishes=destination == FINISH_PROGRESS,
                )
            )
        return moves

    def roll_dice(self, value: int | None = None) -> tuple[bool, str]:
        if self.game_over:
            return False, "The match is over. Start a new game to keep playing."
        if self.active_roll is not None:
            return False, "Finish the current move before rolling again."

        roll = value if value is not None else randint(1, 6)
        if roll < 1 or roll > 6:
            return False, "Dice rolls must be between 1 and 6."

        player = self.current_player
        self.last_roll = roll
        self.last_move = None

        if roll == 6:
            self.consecutive_sixes += 1
        else:
            self.consecutive_sixes = 0

        if self.consecutive_sixes == 3:
            self.active_roll = None
            self.consecutive_sixes = 0
            message = f"{player.name} rolled three consecutive sixes and loses the turn."
            self.history.append(message)
            self._advance_turn()
            return True, f"{message} {self.current_player.name} is up next."

        self.active_roll = roll
        legal_moves = self.legal_moves()
        if legal_moves:
            self.status = f"{player.name} rolled {roll}. Click one of the glowing tokens."
            return True, self.status

        self.active_roll = None
        no_move_message = f"{player.name} rolled {roll} but has no legal move."
        self.history.append(no_move_message)
        if roll == 6:
            self.status = f"{no_move_message} A six keeps the turn, so roll again."
            return True, self.status

        self._advance_turn()
        return True, f"{no_move_message} {self.current_player.name} is up next."

    def move_token(self, token_id: str) -> tuple[bool, str]:
        if self.game_over:
            return False, "The match is already finished."
        if self.active_roll is None:
            return False, "Roll the dice before moving a token."

        options = {option.token_id: option for option in self.legal_moves()}
        option = options.get(token_id)
        if option is None:
            return False, "That token cannot move for the current roll."

        player = self.current_player
        token = self._token_by_id(token_id)
        from_cell = self.token_cell_id(player.color, token)
        rolled_value = self.active_roll

        token.progress = option.to_progress
        to_cell = self.token_cell_id(player.color, token)
        captured_ids = self._capture_opponents(player.color, token.progress)
        finished = token.progress == FINISH_PROGRESS

        self.last_roll = rolled_value
        self.active_roll = None
        self.last_move = LastMove(
            token_id=token.id,
            color=player.color,
            roll=rolled_value,
            from_cell=from_cell,
            to_cell=to_cell,
            captured_ids=tuple(captured_ids),
            finished=finished,
        )

        message_parts = [f"{player.name} moved {COLOR_LABELS[player.color]} token {token.number + 1}."]
        if option.spawns:
            message_parts.append("The token leaves the yard.")
        if captured_ids:
            message_parts.append(f"Captured {len(captured_ids)} opposing token{'s' if len(captured_ids) != 1 else ''}.")
        if finished:
            message_parts.append("That token reached home.")

        if player.finished_count == len(player.tokens):
            self.game_over = True
            self.winner_color = player.color
            self.consecutive_sixes = 0
            self.status = f"{player.name} wins the match for {COLOR_LABELS[player.color]}."
            message_parts.append(self.status)
            message = " ".join(message_parts)
            self.history.append(message)
            return True, message

        extra_turn = rolled_value == 6 or bool(captured_ids) or finished
        if extra_turn:
            if rolled_value != 6:
                self.consecutive_sixes = 0
            self.status = f"{player.name} earned another roll."
            message_parts.append(self.status)
        else:
            self.consecutive_sixes = 0
            self._advance_turn()
            message_parts.append(f"{self.current_player.name} is up next.")

        message = " ".join(message_parts)
        self.history.append(message)
        return True, message

    def movable_token_ids(self) -> set[str]:
        return {move.token_id for move in self.legal_moves()}

    def token_cell_id(self, color: str, token: TokenState) -> str:
        if token.progress == -1:
            return f"yard-{color}-{token.number}"
        if 0 <= token.progress <= 50:
            return f"track-{self.absolute_track_index(color, token.progress)}"
        if 51 <= token.progress <= 55:
            return f"lane-{color}-{token.progress - 51}"
        return f"finish-{color}"

    def absolute_track_index(self, color: str, progress: int) -> int:
        return (START_INDICES[color] + progress) % 52

    def is_safe_position(self, color: str, progress: int) -> bool:
        if progress < 0 or progress >= 51:
            return True
        return self.absolute_track_index(color, progress) in SAFE_TRACK_INDICES

    def _destination_progress(self, current_progress: int, roll: int) -> int | None:
        if current_progress == FINISH_PROGRESS:
            return None
        if current_progress == -1:
            return 0 if roll == 6 else None

        destination = current_progress + roll
        if destination > FINISH_PROGRESS:
            return None
        return destination

    def _capture_opponents(self, moving_color: str, progress: int) -> list[str]:
        if progress < 0 or progress > 50 or self.is_safe_position(moving_color, progress):
            return []

        capture_index = self.absolute_track_index(moving_color, progress)
        captured: list[str] = []
        for player in self.players:
            if player.color == moving_color:
                continue
            for token in player.tokens:
                if 0 <= token.progress <= 50 and self.absolute_track_index(player.color, token.progress) == capture_index:
                    token.progress = -1
                    captured.append(token.id)
        return captured

    def _advance_turn(self) -> None:
        self.active_roll = None
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        player = self.current_player
        self.status = f"{player.name} ({COLOR_LABELS[player.color]}) is ready to roll."

    def _token_by_id(self, token_id: str) -> TokenState:
        for player in self.players:
            for token in player.tokens:
                if token.id == token_id:
                    return token
        raise KeyError(f"Unknown token id: {token_id}")
