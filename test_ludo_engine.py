from __future__ import annotations

import unittest

from ludo_engine import FINISH_PROGRESS, LudoGame


class LudoEngineTests(unittest.TestCase):
    def test_two_player_setup_uses_opposite_colors(self) -> None:
        game = LudoGame.new_game(player_count=2, player_names=["Asha", "Bharat"])

        self.assertEqual([player.color for player in game.players], ["red", "yellow"])
        self.assertEqual([player.name for player in game.players], ["Asha", "Bharat"])

    def test_non_six_without_move_passes_turn(self) -> None:
        game = LudoGame.new_game(player_count=2)

        success, message = game.roll_dice(value=3)

        self.assertTrue(success)
        self.assertIn("no legal move", message.lower())
        self.assertIsNone(game.active_roll)
        self.assertEqual(game.current_player.color, "yellow")

    def test_six_allows_token_to_leave_yard(self) -> None:
        game = LudoGame.new_game(player_count=2)

        success, _ = game.roll_dice(value=6)
        self.assertTrue(success)
        self.assertEqual(game.movable_token_ids(), {"red_0", "red_1", "red_2", "red_3"})

        moved, message = game.move_token("red_0")

        self.assertTrue(moved)
        self.assertIn("leaves the yard", message.lower())
        self.assertEqual(game.players[0].tokens[0].progress, 0)
        self.assertEqual(game.current_player.color, "red")

    def test_capture_sends_opponent_back_home_and_grants_extra_turn(self) -> None:
        game = LudoGame.new_game(player_count=2)
        red = game.players[0]
        yellow = game.players[1]

        red.tokens[0].progress = 3
        yellow.tokens[0].progress = 31
        game.active_roll = 2

        moved, message = game.move_token("red_0")

        self.assertTrue(moved)
        self.assertIn("captured", message.lower())
        self.assertEqual(red.tokens[0].progress, 5)
        self.assertEqual(yellow.tokens[0].progress, -1)
        self.assertEqual(game.current_player.color, "red")

    def test_exact_roll_is_required_to_finish(self) -> None:
        game = LudoGame.new_game(player_count=2)
        red = game.players[0]

        red.tokens[0].progress = 54
        red.tokens[1].progress = FINISH_PROGRESS
        red.tokens[2].progress = FINISH_PROGRESS
        red.tokens[3].progress = FINISH_PROGRESS

        success, message = game.roll_dice(value=3)

        self.assertTrue(success)
        self.assertIn("no legal move", message.lower())
        self.assertIsNone(game.active_roll)
        self.assertEqual(red.tokens[0].progress, 54)
        self.assertEqual(game.current_player.color, "yellow")

    def test_three_consecutive_sixes_forfeit_the_turn(self) -> None:
        game = LudoGame.new_game(player_count=2)
        red = game.players[0]

        self.assertTrue(game.roll_dice(value=6)[0])
        self.assertTrue(game.move_token("red_0")[0])
        self.assertEqual(red.tokens[0].progress, 0)

        self.assertTrue(game.roll_dice(value=6)[0])
        self.assertTrue(game.move_token("red_0")[0])
        self.assertEqual(red.tokens[0].progress, 6)

        success, message = game.roll_dice(value=6)

        self.assertTrue(success)
        self.assertIn("three consecutive sixes", message.lower())
        self.assertIsNone(game.active_roll)
        self.assertEqual(game.current_player.color, "yellow")

    def test_finishing_last_token_wins_match(self) -> None:
        game = LudoGame.new_game(player_count=2, player_names=["Asha", "Bharat"])
        red = game.players[0]

        red.tokens[0].progress = 55
        red.tokens[1].progress = FINISH_PROGRESS
        red.tokens[2].progress = FINISH_PROGRESS
        red.tokens[3].progress = FINISH_PROGRESS
        game.active_roll = 1

        moved, message = game.move_token("red_0")

        self.assertTrue(moved)
        self.assertTrue(game.game_over)
        self.assertEqual(game.winner_color, "red")
        self.assertIn("wins the match", message.lower())


if __name__ == "__main__":
    unittest.main()
