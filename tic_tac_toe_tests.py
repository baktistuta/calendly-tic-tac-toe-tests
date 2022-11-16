import math
import random
from itertools import cycle
from seleniumbase import BaseCase


test_url = "https://roomy-fire-houseboat.glitch.me/"
default_board_size = 3
possible_board_sizes = range(3, 11)  # Assuming that your board size can be from 3x3 to 10x10
char_to_use = cycle(["X", "O"])      # X always goes first
cell_element_by_xpath = "//*[@id='{}']"
endgame_message = "Congratulations player {}! You've won. Refresh to play again!"

class TicTacToeTestClass(BaseCase):
    def test_player_can_generate_board(self):
        board_size = random.choice(possible_board_sizes)
        self.setup_empty_board(board_size)
        self.assert_correct_board_size(board_size)

    def test_invalid_board_size_inputs(self):
        self.setup_empty_board(-3)      # Testing negative integer
        self.assert_no_board_on_page()
        self.setup_empty_board(-2.33)   # Testing negative float
        self.assert_no_board_on_page()
        self.setup_empty_board(0)       # Testing 0
        self.assert_no_board_on_page()
        self.setup_empty_board("three") # Testing string
        self.assert_no_board_on_page()
        self.setup_empty_board(None)    # Testing null input
        self.assert_no_board_on_page()
    
    def test_correct_message_for_winner(self):
        self.setup_empty_board(default_board_size)
        self.let_winner_be("X")
        self.assert_exact_text(winner_msg, "#endgame")  # Expect to Fail due to bug in app
        self.refresh()
        self.setup_empty_board(default_board_size)
        self.let_winner_be("O")
        self.assert_exact_text(winner_msg, "#endgame")

    def test_refreshing_page_clears_page(self):
        self.setup_empty_board(default_board_size)
        self.let_winner_be("X")
        self.refresh()
        self.assert_text_not_visible(winner_msg)
        self.assert_no_board_on_page()

    def test_player_is_not_shown_msg_after_a_draw(self):
        self.setup_empty_board(default_board_size)
        self.end_game_in_a_draw()
        self.assert_text_not_visible(
            endgame_message.format("X") or
            endgame_message.format("O")
        )
    
    def setup_empty_board(self, board_size):
        """
        Helper method to generate an empty board to play.

        {board_size} should be a positive integer or float.
                     If the input type is 'None', it will click the start button without any input.
        """
        self.open(test_url)
        if type(board_size) in [int, float] and board_size > 0:
            self.type("#number", board_size)
            self.click("#start")
            self.assert_element("#table")
        elif board_size == None:
            self.click("#start")
        else:
            print("{} {}is an invalid board size.".format(board_size, type(board_size)))

    def let_winner_be(self, player):
        """
        Helper method to simulate a player winning a game.

        String {player} should be either string "X" or "O".
        """
        plays_for_X_to_win = [0, 3, 1, 4, 2]    # Player X completes a row at the top
        plays_for_O_to_win = [5, 2, 8, 4, 7, 6] # Player O completes a diagonal from top right to bottom left

        if player == "X":
            for id in plays_for_X_to_win:
                self.click(cell_element_by_xpath.format(id))
                self.assert_text(next(char_to_use), cell_element_by_xpath.format(id))
            next(char_to_use)  # Call this one more time to reset iterator
        elif player == "O":
            for id in plays_for_O_to_win:
                self.click(cell_element_by_xpath.format(id))
                self.assert_text(next(char_to_use), cell_element_by_xpath.format(id))
        else:
            print("{} is an invalid player".format(player))
    
        global winner_msg
        winner_msg = endgame_message
        winner_msg = winner_msg.format(player)

    def end_game_in_a_draw(self):
        """
        Helper method to simulate a draw.
        """
        cells_by_id_to_fill_in_order = [0, 1, 3, 4, 7, 6, 2, 5, 8]
        for id in cells_by_id_to_fill_in_order:
            self.click(cell_element_by_xpath.format(id))

    def assert_correct_board_size(self, expected_size):
        """
        Assertion to check that the number of rows and columns match the expected size.
        """
        num_rows = len (self.driver.find_elements("xpath", "//*[@id='table']/tr"))
        num_columns = len (self.driver.find_elements("xpath", "//*[@id='table']/tr[1]/td"))
        if type(expected_size) == float:
            expected_size = math.ceil(expected_size)  # Rounding up the decimal input to match current behavior
        print("Generated board size: {} x {}".format(num_rows, num_columns))
        print("Expected board size: ", expected_size)
        self.assert_true(num_rows == num_columns == expected_size)
    
    def assert_no_board_on_page(self):
        """
        Assertion to check that the web page is clean and no Tic Tac Toe board is visible.

        Checks for cell with id 0, which is the top left cell of a visible board.
        """
        self.assert_element_not_visible(cell_element_by_xpath.format("0"))
