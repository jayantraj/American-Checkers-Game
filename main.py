from copy import *
import time

ROW, COL = 8, 8
output_format = {
    (0, 0): 'a8', (0, 1): 'b8', (0, 2): 'c8', (0, 3): 'd8',
    (0, 4): 'e8', (0, 5): 'f8', (0, 6): 'g8', (0, 7): 'h8',

    (1, 0): 'a7', (1, 1): 'b7', (1, 2): 'c7', (1, 3): 'd7',
    (1, 4): 'e7', (1, 5): 'f7', (1, 6): 'g7', (1, 7): 'h7',

    (2, 0): 'a6', (2, 1): 'b6', (2, 2): 'c6', (2, 3): 'd6',
    (2, 4): 'e6', (2, 5): 'f6', (2, 6): 'g6', (2, 7): 'h6',

    (3, 0): 'a5', (3, 1): 'b5', (3, 2): 'c5', (3, 3): 'd5',
    (3, 4): 'e5', (3, 5): 'f5', (3, 6): 'g5', (3, 7): 'h5',

    (4, 0): 'a4', (4, 1): 'b4', (4, 2): 'c4', (4, 3): 'd4',
    (4, 4): 'e4', (4, 5): 'f4', (4, 6): 'g4', (4, 7): 'h4',

    (5, 0): 'a3', (5, 1): 'b3', (5, 2): 'c3', (5, 3): 'd3',
    (5, 4): 'e3', (5, 5): 'f3', (5, 6): 'g3', (5, 7): 'h3',

    (6, 0): 'a2', (6, 1): 'b2', (6, 2): 'c2', (6, 3): 'd2',
    (6, 4): 'e2', (6, 5): 'f2', (6, 6): 'g2', (6, 7): 'h2',

    (7, 0): 'a1', (7, 1): 'b1', (7, 2): 'c1', (7, 3): 'd1',
    (7, 4): 'e1', (7, 5): 'f1', (7, 6): 'g1', (7, 7): 'h1'
}
move_down, move_forward = [(1, -1), (1, 1)], [(-1, -1), (-1, 1)]
KING_PAWN_VALUE = 3.125
BLACK_CAPTURE = 1.0417
WHITE_CAPTURE = 1.0416
BLACK_KING_DIST = 1.429
WHITE_KING_DIST = 1.428
SAFE = 5.263

time_taken_for_depths = [0 for _ in range(8)]
file = open("calibration.txt", "r")
for i in range(1, 8):
    k = file.readline()
    time_taken_for_depths[i] = float(k)
print(time_taken_for_depths)


class Board:

    def __init__(self):
        self.length = 8
        self.grid = [[0 for _ in range(self.length)] for _ in range(self.length)]

    def get_grid(self):
        return self.grid

    def is_free(self, row, col):
        return self.grid[row][col] == 0

    def place(self, row, col, piece):
        self.grid[row][col] = piece

    def fetch(self, row, col):
        return self.grid[row][col]

    def remove(self, row, col):
        self.grid[row][col] = 0

    def print_board(self):
        for r in range(self.length):
            print()
            for c in range(self.length):
                if self.grid[r][c] != 0:
                    if self.grid[r][c].is_king:
                        print(self.grid[r][c].color[0].upper(), end=' ')
                    else:
                        print(self.grid[r][c].color[0], end=' ')
                else:
                    print(self.grid[r][c], end=' ')


class Piece:

    def __init__(self, color, is_king=False):
        self.color = color
        self.is_king = is_king

    def make_king(self):
        self.is_king = True


def initialize(given_board):
    board = Board()
    for r in range(ROW):
        for c in range(COL):
            if given_board[r][c] == 'w':
                board.place(r, c, Piece('white', False))
            elif given_board[r][c] == 'W':
                board.place(r, c, Piece('white', True))
            elif given_board[r][c] == 'b':
                board.place(r, c, Piece('black', False))
            elif given_board[r][c] == 'B':
                board.place(r, c, Piece('black', True))
    board.print_board()
    return board


def check_move_validity(board, given_row, given_col):
    if 0 <= given_row < ROW and 0 <= given_col < COL and board.is_free(given_row, given_col):
        return True
    return False


def check_jump_validity(board, current_piece, row, col, x, y):
    if 0 <= row + 2 * x < ROW and 0 <= col + 2 * y < COL and board.is_free(row + 2 * x,
                                                                           col + 2 * y) and not board.is_free(
        row + x, col + y) and board.fetch(row + x, col + y).color != current_piece.color:
        return True
    return False


def fetch_moves(board, row, col):
    # this function returns moves for a given single piece at row,col position.

    current_piece = board.fetch(row, col)
    diagonal_bottom, diagonal_top = [], []
    # black_piece travels from top to bottom, white piece travels from bottom to top.
    if current_piece:
        for (x, y) in move_down:
            given_row, given_col = row + x, col + y
            if check_move_validity(board, given_row, given_col):
                diagonal_bottom.append((given_row, given_col))

        for (x, y) in move_forward:
            given_row, given_col = row + x, col + y
            if check_move_validity(board, given_row, given_col):
                diagonal_top.append((given_row, given_col))

        if current_piece.is_king:
            return diagonal_bottom + diagonal_top
        elif current_piece.color == 'black':
            return diagonal_bottom
        else:
            return diagonal_top

    return []


def get_jumps(board, row, col):
    # this function lists all the captures for a single piece on the board located at row, col position.
    # move_down, move_forward = [(1, -1), (1, 1)], [(-1, -1), (-1, 1)]
    current_piece = board.fetch(row, col)
    diagonal_bottom, diagonal_top = [], []
    if current_piece:
        for (x, y) in move_down:
            if check_jump_validity(board, current_piece, row, col, x, y):
                diagonal_bottom.append((row + 2 * x, col + 2 * y))

        for (x, y) in move_forward:
            if check_jump_validity(board, current_piece, row, col, x, y):
                diagonal_top.append((row + 2 * x, col + 2 * y))

        if current_piece.is_king:
            return diagonal_bottom + diagonal_top
        elif current_piece.color == 'black':
            return diagonal_bottom
        else:
            return diagonal_top

    return []


def get_all_moves(board, color):
    all_moves = []
    for r in range(ROW):
        for c in range(COL):
            current_piece = board.fetch(r, c)
            if current_piece:
                if current_piece.color == color:
                    path_list = fetch_moves(board, r, c)
                    path_start = (r, c)
                    for path in path_list:
                        all_moves.append((path_start, path))
    return all_moves


def recurse_on_path(board, row, col, path, paths, is_turned_king):
    path.append((row, col))

    jumps_made = []
    # if I turn it into a king I can't continue the move to get further jumps.
    if not is_turned_king:
        jumps_made = get_jumps(board, row, col)

    if not jumps_made:
        paths.append(path)
    else:
        for (row_to, col_to) in jumps_made:
            current_piece = deepcopy(board.fetch(row, col))
            board.remove(row, col)
            board.place(row_to, col_to, current_piece)
            if (current_piece.color == 'black' and row_to == ROW - 1) or (
                    current_piece.color == 'white' and row_to == 0) and not current_piece.is_king:
                current_piece.make_king()
                is_turned_king = True
            if row_to > row:
                middle_row = row + 1
            else:
                middle_row = row - 1
            if col_to > col:
                middle_col = col + 1
            else:
                middle_col = col - 1
            captured_piece = board.fetch(middle_row, middle_col)
            board.remove(middle_row, middle_col)
            recurse_on_path(board, row_to, col_to, path.copy(), paths, is_turned_king)
            board.place(middle_row, middle_col, captured_piece)
            board.remove(row_to, col_to)
            board.place(row, col, current_piece)


def get_jumped_pieces(board, row, col):
    # this function finds all the capturing paths started at a row,col position
    # if there was no capture, then it will return []
    paths = []
    # board_ = deepcopy(board)
    recurse_on_path(board, row, col, [], paths, False)
    # print(row, col, paths)
    return paths


def get_all_jumped_pieces(board, color):
    # this function is used to get all the jumps that can be made by a piece of certain color.

    all_jumps = []
    for r in range(ROW):
        for c in range(COL):
            current_piece = board.fetch(r, c)
            if current_piece:
                if current_piece.color == color:
                    path_list = get_jumped_pieces(board, r, c)
                    for path in path_list:
                        if len(path) > 1:
                            all_jumps.append(path)
    return all_jumps


def do_move(board, moves):
    # moves[0] - source, moves[1] - destination

    row, col = moves[0]
    row_end, col_end = moves[1]
    current_piece = board.fetch(row, col)

    if (current_piece.color == 'black' and row_end == ROW - 1) or (current_piece.color == 'white' and row_end == 0):
        current_piece.make_king()
    board.remove(row, col)
    board.place(row_end, col_end, current_piece)
    return board
    # board.print_board()


def do_jumps(board, jumps):
    number_of_jumps = len(jumps)
    for i in range(number_of_jumps - 1):
        row, col = jumps[i]
        row_to, col_to = jumps[i + 1]
        if row_to > row:
            middle_row = row + 1
        else:
            middle_row = row - 1
        if col_to > col:
            middle_col = col + 1
        else:
            middle_col = col - 1
        jumping_piece = board.fetch(row, col)
        board.remove(row, col)
        board.place(row_to, col_to, jumping_piece)
        board.remove(middle_row, middle_col)
    # board.print_board()
    return board


def single_move(board, color):
    moves, jumps = get_all_moves(board, color), get_all_jumped_pieces(board, color)
    print('\n\n')
    file = open('output.txt', 'a')
    if jumps:
        for i in range(len(jumps[0]) - 1):
            print('J ', output_format[jumps[0][i]], output_format[jumps[0][i + 1]])
            write_data = 'J ' + output_format[jumps[0][i]] + ' ' + output_format[jumps[0][i + 1]] + '\n'
            file.write(write_data)

    else:
        print('E ', output_format[moves[0][0]], ' ', output_format[moves[0][1]])
        write_data = 'E ' + output_format[moves[0][0]] + ' ' + output_format[moves[0][1]]
        file.write(write_data)


def mean_square(a, b):
    t = (a ** 2 + b ** 2) ** 0.5
    return int(t / 2)


def count_number_of_captures(board, row, col):
    s = 0
    for c in get_jumped_pieces(board, row, col):
        if len(c) > 1:
            s += (len(c))

    return s


def calculate_black(black_pawn, black_king, number_of_pieces_captured_by_black, black_can_become_king_dist,
                    black_safe_distance, white_pawn, white_king, number_of_pieces_captured_by_white,
                    white_can_become_king_dist, white_safe_distance):
    a = KING_PAWN_VALUE * ((black_pawn + 2 * black_king) - (white_pawn + 2 * white_king) /
                           1 + (black_pawn + 2 * black_king) + (white_pawn + 2 * white_king))
    b = BLACK_CAPTURE * ((number_of_pieces_captured_by_black - number_of_pieces_captured_by_white) /
                         (1 + number_of_pieces_captured_by_black + number_of_pieces_captured_by_white))
    c = BLACK_KING_DIST * ((black_can_become_king_dist - white_can_become_king_dist) /
                           (1 + black_can_become_king_dist + white_can_become_king_dist))
    d = SAFE * ((black_safe_distance - white_safe_distance) / (1 + black_safe_distance + white_safe_distance))
    return a + b + c + d


def calculate_white(black_pawn, black_king, number_of_pieces_captured_by_black, black_can_become_king_dist,
                    black_safe_distance, white_pawn, white_king, number_of_pieces_captured_by_white,
                    white_can_become_king_dist, white_safe_distance):
    a = KING_PAWN_VALUE * ((white_pawn + 2 * white_king) - (black_pawn + 2 * black_king) /
                           1 + (white_pawn + 2 * white_king) + (black_pawn + 2 * black_king))
    b = WHITE_CAPTURE * ((number_of_pieces_captured_by_white - number_of_pieces_captured_by_black) /
                         (1 + number_of_pieces_captured_by_white + number_of_pieces_captured_by_black))
    c = WHITE_KING_DIST * ((white_can_become_king_dist - black_can_become_king_dist) / (
            1 + white_can_become_king_dist + black_can_become_king_dist))
    d = SAFE * ((white_safe_distance - black_safe_distance) / (1 + white_safe_distance + black_safe_distance))
    return a + b + c + d


def evaluation_function(board, color):
    black_pawn, black_king, number_of_pieces_captured_by_black, black_can_become_king_dist, black_safe_distance = 0, 0, 0, 0, 0
    white_pawn, white_king, number_of_pieces_captured_by_white, white_can_become_king_dist, white_safe_distance = 0, 0, 0, 0, 0
    for row in range(ROW):
        for col in range(COL):
            current_piece = board.fetch(row, col)
            if current_piece:
                r = max(row, 7 - row)
                c = max(col, 7 - col)
                ms = mean_square(r, c)
                if current_piece.color == "black":
                    number_of_pieces_captured_by_black += count_number_of_captures(board, row, col)
                    if not current_piece.is_king:
                        black_pawn += 1
                        black_can_become_king_dist += 1 + row
                        black_safe_distance += ms
                    else:
                        black_king += 1

                else:
                    number_of_pieces_captured_by_white += count_number_of_captures(board, row, col)
                    # print("wc ",number_of_pieces_captured_by_white)
                    if not current_piece.is_king:
                        white_pawn += 1
                        white_can_become_king_dist += 7 - row
                        white_safe_distance += ms
                    else:
                        white_king += 1

    if color == "black":
        # print(black_pawn, black_king, number_of_pieces_captured_by_black, black_can_become_king_dist,
        # black_safe_distance, white_pawn, white_king, number_of_pieces_captured_by_white,
        # white_can_become_king_dist, white_safe_distance)
        value = calculate_black(black_pawn, black_king, number_of_pieces_captured_by_black, black_can_become_king_dist,
                                black_safe_distance, white_pawn, white_king, number_of_pieces_captured_by_white,
                                white_can_become_king_dist, white_safe_distance)
        return value
    else:
        # print(black_pawn, black_king, number_of_pieces_captured_by_black, black_can_become_king_dist,
        # black_safe_distance, white_pawn, white_king, number_of_pieces_captured_by_white,
        # white_can_become_king_dist, white_safe_distance)
        value = calculate_white(black_pawn, black_king, number_of_pieces_captured_by_black, black_can_become_king_dist,
                                black_safe_distance, white_pawn, white_king, number_of_pieces_captured_by_white,
                                white_can_become_king_dist, white_safe_distance)
        return value


def temporary_board(board, move_type, action):
    temp_board = deepcopy(board)
    if move_type == "jump":
        temp_board = do_jumps(temp_board, action)
    else:
        temp_board = do_move(temp_board, action)
    # temp_board.print_board()
    return temp_board


def minimizing(board, color, max_depth, alpha, beta):
    if max_depth == 0:
        return evaluation_function(board, color)
    else:
        val = float('inf')
        moves, jumps = get_all_moves(board, color), get_all_jumped_pieces(board, color)
        if jumps:
            for j in jumps:
                temp_board = temporary_board(deepcopy(board), "jump", j)
                val = min(val, maximizing(temp_board, color, max_depth - 1, alpha, beta))
                if alpha and beta:
                    if val <= alpha:
                        return val
                    beta = min(beta, val)
            return val

        elif moves:
            for m in moves:
                temp_board = temporary_board(deepcopy(board), "move", m)
                val = min(val, maximizing(temp_board, color, max_depth - 1, alpha, beta))
                if alpha and beta:
                    if val <= alpha:
                        return val
                    beta = min(beta, val)
            return val


def maximizing(board, color, max_depth, alpha, beta):
    if max_depth == 0:
        return evaluation_function(board, color)
    else:
        val = float('-inf')
        moves, jumps = get_all_moves(board, color), get_all_jumped_pieces(board, color)
        if jumps:
            for j in jumps:
                temp_board = temporary_board(deepcopy(board), "jump", j)
                val = max(val, minimizing(temp_board, color, max_depth - 1, alpha, beta))
                if alpha and beta:
                    if val >= beta:
                        return val
                    alpha = max(alpha, val)
            return val

        elif moves:
            for m in moves:
                temp_board = temporary_board(deepcopy(board), "move", m)
                val = max(val, minimizing(temp_board, color, max_depth - 1, alpha, beta))
                if alpha and beta:
                    if val >= beta:
                        return val
                    alpha = max(alpha, val)
            return val


def play_game(board, piece_color,depth):
    # for first 2 moves play precomputed moves..(do this later)

    # for upcoming moves play using minimax_alpha_beta
    #depth = 6
    moves, jumps = get_all_moves(board, piece_color), get_all_jumped_pieces(board, piece_color)
    max_value = float('-inf')
    is_jump = True
    best_move = []
    if jumps:
        # if there is only one jump possible, you should do that jump.
        if len(jumps) == 1:
            return is_jump, jumps[0]
        for j in jumps:
            temp_board = temporary_board(deepcopy(board), "jump", j)
            temp = minimizing(temp_board, piece_color, depth - 1, float('-inf'), float('inf'))
            if temp > max_value:
                max_value = temp
                best_move = j

    else:
        is_jump = False
        if len(moves) == 1:
            return is_jump, moves[0]
        for m in moves:
            temp_board = temporary_board(deepcopy(board), "move", m)
            temp = minimizing(temp_board, piece_color, depth - 1, float('-inf'), float('inf'))
            # print(temp)
            if temp > max_value:
                max_value = temp
                best_move = m
        print(best_move, max_value)

    return is_jump, best_move


def gaming_mode(board, piece_color,start_time,given_time,depth = 6):
    try:
        play_file = open("playdata.txt", "r")
        time_taken_for_previous_move = float(play_file.readline())

        if 0.35*given_time<time_taken_for_previous_move:
            depth-=1

        is_jump, best_move = play_game(board, piece_color,depth)
        # print(best_move)
        file = open('output.txt', 'a')

        if is_jump:
            for i in range(len(best_move) - 1):
                print('J ', output_format[best_move[i]], output_format[best_move[i + 1]])
                write_data = 'J ' + output_format[best_move[i]] + ' ' + output_format[best_move[i + 1]] + '\n'
                file.write(write_data)

        else:
            print('E ', output_format[best_move[0]], ' ', output_format[best_move[1]])
            write_data = 'E ' + output_format[best_move[0]] + ' ' + output_format[best_move[1]] + '\n'
            file.write(write_data)
        end_time = time.time()
        print(end_time-start_time)
        write_time = str(end_time-start_time)
        play_file.write(write_time)

    except:
        play_file =open("playdata.txt", 'w+')

        if piece_color == "white":
            best_move = [(5, 4), (4, 5)]
            file = open("output.txt", "a")
            print('E ', output_format[best_move[0]], ' ', output_format[best_move[1]])
            write_data = 'E ' + output_format[best_move[0]] + ' ' + output_format[best_move[1]] + '\n'
            file.write(write_data)
        else:
            best_move = [(2, 5), (3, 4)]
            file = open("output.txt", "a")
            print('E ', output_format[best_move[0]], ' ', output_format[best_move[1]])
            write_data = 'E ' + output_format[best_move[0]] + ' ' + output_format[best_move[1]] + '\n'
            file.write(write_data)
        end_time = time.time()
        print(end_time-start_time)
        write_time = str(end_time-start_time)
        play_file.write(write_time)


def main():
    start_time = time.time()
    given_board = []
    file = open("input6.txt", 'r')
    game_mode = file.readline().rstrip()
    piece_color = file.readline().rstrip().lower()
    given_time = float(file.readline())
    for _ in range(8):
        given_board.append(list(file.readline().rstrip()))

    board = initialize(given_board)

    # gaming_mode(board, piece_color)
    if game_mode == "SINGLE":
        single_move(board, piece_color)
    else:
        gaming_mode(board, piece_color,start_time,given_time,6)



# def useful comments():

# moving_places = fetch_moves(board, 2, 7)
# print(moving_places)

# jumping_places = get_jumps(board, 6, 3)
# print(jumping_places)

# all_moves = get_all_moves(board, piece_color)
# print(all_moves)

# captured_moves = get_jumped_pieces(board, 6, 3)
# print(captured_moves)

# all_moves = get_all_moves(board, 'black')
# print("all moves for black :")
# print(all_moves)

# all_moves = get_all_moves(board, 'white')
# print("all moves for white :")
# print(all_moves)

# all_captures = get_all_jumped_pieces(board, 'black')
# print("all captures for black :")
# print(all_captures)

# all_captures = get_all_jumped_pieces(board, 'white')
# print("all captures for white :")
# print(all_captures)

# for i in moves:
#    print(i)
#    do_move(deepcopy(board), i)

# for i in jumps:
#    do_jumps(deepcopy(board), i)

board = Board()

board.place(1, 0, Piece('white'))
board.place(1, 4, Piece('black'))
board.place(1, 6, Piece('black'))
board.place(3, 2, Piece('white'))
board.place(3, 4, Piece('black'))
board.place(4, 1, Piece('white'))
board.place(4, 5, Piece('black'))
board.place(5, 4, Piece('black'))
board.place(6, 1, Piece('white'))
board.place(6, 7, Piece('black'))
board.place(7, 2, Piece('white'))
board.place(7, 6, Piece('white'))

# current_state = [board, depth]

# depth = 6
# print(evaluation_function(board, 'white'))
#board.print_board()
# play_game(board, 'white')

main()