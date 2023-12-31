import nicegui


# Game logic
class TicTacToe:
    def __init__(self):
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"
        self.winner = None
        self.draw = False

    def make_move(self, row: int, col: int) -> bool:
        if self.is_valid_move(row, col):
            self.board[row][col] = self.current_player
            self.check_game_status()
            self.current_player = "0" if self.current_player == "X" else "X"
            return True
        return False

    def is_valid_move(self, row: int, col: int) -> bool:
        return self.board[row][col] == "" and not self.game_over()

    def game_over(self) -> bool:
        return self.winner is not None or self.draw

    def check_game_status(self):
        # Check rows, columns, and diagonals for a win
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != "":
                self.winner = self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != "":
                self.winner = self.board[0][i]

        if self.board[0][0] == self.board[1][1] == self.board[2][2] != "":
            self.winner = self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != "":
            self.winner = self.board[0][2]

        # Check for a draw
        if all(all(cell != "" for cell in row) for row in self.board) and self.winner is None:
            self.draw = True


# NiceGUI interface
ui = nicegui.ui


def restart_game():
    game.__init__()
    for row in buttons:
        for btn in row:
            btn.text = ''


def button_click(row, col):
    current_player = game.current_player
    if game.make_move(row, col):
        buttons[row][col].text = current_player
        if game.game_over():
            status_label.text = f"Winner: {game.winner}" if game.winner else "Draw!"
        else:
            status_label.text = f"Current Player: {game.current_player}"


game = TicTacToe()

# Creating a grid layout for buttons
with ui.grid(columns=3).classes("grid gap-4"):
    buttons = [
        [ui.button('', on_click=lambda row=row, col=col: button_click(row, col)) for col in range(3)]
        for row in range(3)
    ]

status_label = ui.label(f"Current Player: {game.current_player}")
ui.button('Restart Game', on_click=restart_game)

if __name__ in {"__main__", "__mp_main__"}:
    # Start the server
    ui.run()
