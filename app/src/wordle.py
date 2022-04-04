from dataclasses import dataclass


class WordleParserError(Exception):
    def __init__(self, message):
        super(message)


def validate(condition: bool, message: str):
    if not condition:
        raise WordleParserError(message)


@dataclass()
class WordleBoard:
    """
    Simple representation of a Wordle Board that is parsed from the emoji version.
    A 0 indicates a miss, a 1 indicates a hit in the wrong location, and a 2 indicates a hit in the right location.
    """

    rows: list[list[int]]

    @staticmethod
    def from_emoji_board(lines: list[str], expected_row_count: int):
        # this parser is lenient and will just loop while it find lines that are good
        # this allows people to write messages at the end of their posts without being punished
        rows = []
        for line in lines:
            trimmed_line = line.strip()
            validate(len(trimmed_line) == 5, "Wordle line must be 5 chars")
            row = []
            for c in trimmed_line:
                value = -1
                if c == '⬛' or c == '⬜':
                    value = 0
                elif c == '🟨':
                    value = 1
                elif c == '🟩':
                    value = 2

                if value == -1:
                    break
                else:
                    row.append(value)

            if len(row) != 5:
                break
            rows.append(row)

        validate(len(rows) == expected_row_count,
                 "Expected {0} rows based on title, but got {1}".format(expected_row_count, len(rows)))

        return WordleBoard(rows)


@dataclass()
class WordleGame:
    """
    Represents a played game of Wordle.
    """
    game_number: int
    attempts: int
    hard_mode: bool
    board: WordleBoard

    def is_win(self) -> bool:
        return self.attempts < 7


class WordleParser:
    """
    Parser to read the text given to a player by Wordle to share with others.
    """

    @staticmethod
    def parse(message: str) -> WordleGame:
        # read the first line
        stripped_msg = message.strip()
        lines = stripped_msg.split("\n")
        # At least 3 lines: Title, Empty, First line of boxes
        validate(len(lines) >= 3, "Message contains no lines. Expected at least 3.")

        first_line_parts = lines[0].strip().split(" ")
        validate(len(first_line_parts) == 3, "First line does not have 3 parts separated by whitespace.")
        validate("Wordle" == first_line_parts[0], "First word on the first line should be \"Wordle\"")
        validate(first_line_parts[1].isdigit(), "Second word on the first line should be all numbers")

        game_number = int(first_line_parts[1])

        score_part = first_line_parts[2]
        score_part_len = len(score_part)
        validate(score_part_len in (3, 4), "Third word of the first line should be 3 or 4 chars long")
        if score_part_len == 4:
            validate(score_part[3] == '*',
                     "The fourth char of the third word on the first line should be an asterisk")
        hard_mode = score_part_len == 4

        validate(score_part[0].isdigit() or score_part[0] == 'X',
                 "The first char of the third word of the first line must be a number or 'X'")
        validate(score_part[1] == '/', "The second char of the third word of the first line must be a '/'")
        validate(score_part[2].isdigit(), "The third char of the third word of the first line must be a number")

        attempts = 7 if score_part[0] == 'X' else int(score_part[0])
        validate(1 <= attempts <= 6, "Number of attempts must be in [1, 6]")

        board = WordleBoard.from_emoji_board(lines[2:], min(attempts, 6))

        return WordleGame(game_number, attempts, hard_mode, board)
