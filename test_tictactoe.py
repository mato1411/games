import unittest

from tictactoe import TicTacToe


class TestTicTacToe(unittest.TestCase):
    def setUp(self):
        self.game = TicTacToe()

    def test_valid_move(self):
        self.assertTrue(self.game.make_move(0, 0))
        self.assertEqual(self.game.board[0][0], "X")

    def test_invalid_move(self):
        self.game.make_move(0, 0)
        self.assertFalse(self.game.make_move(0, 0))  # Repeating the same move

    def test_win_condition(self):
        moves = [(0, 0), (1, 1), (0, 1), (2, 2), (0, 2)]  # X wins
        for row, col in moves:
            self.game.make_move(row, col)
        self.assertEqual(self.game.winner, "X")

    def test_draw_condition(self):
        # Draw
        # [
        #     ['X', '0', 'X'],
        #     ['X', '0', '0'],
        #     ['0', 'X', 'X']
        # ]
        moves = [(0, 0), (0, 1), (0, 2),
                 (1, 1), (1, 0), (1, 2),
                 (2, 1), (2, 0), (2, 2)]
        for row, col in moves:
            self.game.make_move(row, col)
        self.assertTrue(self.game.draw)


if __name__ == '__main__':
    unittest.main()
