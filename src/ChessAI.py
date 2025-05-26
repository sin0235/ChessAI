"""
Handling the AI moves.
Có sử dụng thuật toán Minimax và cắt tỉa Alpha-beta
"""
import random

piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
#Đánh giá mức độ quan trọng của từng quân cờ (VD: 0 là không thể để mất,Q là quan trọng nhất và chỉ mang tính tương đối)

knight_scores = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                 [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                 [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                 [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                 [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishop_scores = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rook_scores = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queen_scores = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawn_scores = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
               [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
               [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
               [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

piece_position_scores = {"wN": knight_scores,
                         "bN": knight_scores[::-1],
                         "wB": bishop_scores,
                         "bB": bishop_scores[::-1],
                         "wQ": queen_scores,
                         "bQ": queen_scores[::-1],
                         "wR": rook_scores,
                         "bR": rook_scores[::-1],
                         "wp": pawn_scores,
                         "bp": pawn_scores[::-1]}

CHECKMATE = 1000
STALEMATE = 0

# Định nghĩa các thuật toán cho AI
ALGORITHM_WITH_PRUNING = "with_pruning"      # Sử dụng cắt tỉa alpha-beta
ALGORITHM_WITHOUT_PRUNING = "without_pruning" # Không sử dụng cắt tỉa

def findBestMove(game_state, valid_moves, return_queue, depth=3, algorithm=ALGORITHM_WITH_PRUNING):
    """
    Tìm nước đi tốt nhất cho AI dựa trên thuật toán được chọn
    
    Tham số:
    - game_state: Trạng thái hiện tại của trò chơi
    - valid_moves: Danh sách các nước đi hợp lệ
    - return_queue: Hàng đợi để trả về nước đi tốt nhất
    - depth: Độ sâu tìm kiếm
    - algorithm: Thuật toán sử dụng (with_pruning hoặc without_pruning)
    """
    global DEPTH
    DEPTH = depth
    global next_move
    next_move = None
    #random.shuffle(valid_moves)
    valid_moves = orderMoves(game_state, valid_moves)  
    
    is_white = game_state.white_to_move
    
    if algorithm == ALGORITHM_WITH_PRUNING:
        # Sử dụng Minimax với cắt tỉa alpha-beta
        findMoveMiniMaxAlphaBeta(game_state, valid_moves, depth, is_white, -CHECKMATE, CHECKMATE)
    else:  # ALGORITHM_WITHOUT_PRUNING
        # Sử dụng Minimax không cắt tỉa
        findMoveMiniMax(game_state, valid_moves, depth, is_white)
    
    return_queue.put(next_move)


def findMoveMiniMax(game_state, valid_moves, depth, is_maximizing):
    """
    Thuật toán Minimax không cắt tỉa
    
    Tham số:
    - game_state: Trạng thái hiện tại của trò chơi
    - valid_moves: Danh sách các nước đi hợp lệ
    - depth: Độ sâu hiện tại của tìm kiếm
    - is_maximizing: True nếu đang tối đa hóa (lượt trắng), False nếu đang tối thiểu hóa (lượt đen)
    """
    global next_move
    
    if depth == 0:
        return scoreBoard(game_state)
    
    valid_moves = orderMoves(game_state, valid_moves)
    
    if is_maximizing:
        max_eval = -CHECKMATE
        for move in valid_moves:
            game_state.makeMove(move)
            next_moves = game_state.getValidMoves()
            eval = findMoveMiniMax(game_state, next_moves, depth - 1, False)
            game_state.undoMove()
            if eval > max_eval:
                max_eval = eval
                if depth == DEPTH:
                    next_move = move
        return max_eval
    else:
        min_eval = CHECKMATE
        for move in valid_moves:
            game_state.makeMove(move)
            next_moves = game_state.getValidMoves()
            eval = findMoveMiniMax(game_state, next_moves, depth - 1, True)
            game_state.undoMove()
            if eval < min_eval:
                min_eval = eval
                if depth == DEPTH:
                    next_move = move
        return min_eval


def findMoveMiniMaxAlphaBeta(game_state, valid_moves, depth, is_maximizing, alpha, beta):
    """
    Thuật toán Minimax với cắt tỉa Alpha-Beta
    
    Tham số:
    - game_state: Trạng thái hiện tại của trò chơi
    - valid_moves: Danh sách các nước đi hợp lệ
    - depth: Độ sâu hiện tại của tìm kiếm
    - is_maximizing: True nếu đang tối đa hóa (lượt trắng), False nếu đang tối thiểu hóa (lượt đen)
    - alpha, beta: Giá trị giới hạn cho cắt tỉa Alpha-Beta
    """
    global next_move
    
    if depth == 0:
        return scoreBoard(game_state)
    
    valid_moves = orderMoves(game_state, valid_moves)
    
    if is_maximizing:
        max_eval = -CHECKMATE
        for move in valid_moves:
            game_state.makeMove(move)
            next_moves = game_state.getValidMoves()
            eval = findMoveMiniMaxAlphaBeta(game_state, next_moves, depth - 1, False, alpha, beta)
            game_state.undoMove()
            if eval > max_eval:
                max_eval = eval
                if depth == DEPTH:
                    next_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = CHECKMATE
        for move in valid_moves:
            game_state.makeMove(move)
            next_moves = game_state.getValidMoves()
            eval = findMoveMiniMaxAlphaBeta(game_state, next_moves, depth - 1, True, alpha, beta)
            game_state.undoMove()
            if eval < min_eval:
                min_eval = eval
                if depth == DEPTH:
                    next_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def scoreBoard(game_state):
    """
    Score the board. A positive score is good for white, a negative score is good for black.
    """
    if game_state.checkmate:
        if game_state.white_to_move:
            return -CHECKMATE  # đen thắng
        else:
            return CHECKMATE  # trắng thắng
    elif game_state.stalemate:
        return STALEMATE
    
    # Tính điểm thông thường
    score = 0
    for row in range(len(game_state.board)):
        for col in range(len(game_state.board[row])):
            piece = game_state.board[row][col]
            if piece != "--":
                piece_position_score = 0
                if piece[1] != "K":
                    piece_position_score = piece_position_scores[piece][row][col]
                if piece[0] == "w":
                    score += piece_score[piece[1]] + piece_position_score
                if piece[0] == "b":
                    score -= piece_score[piece[1]] + piece_position_score

    return score


def findRandomMove(valid_moves):
    """
    Picks and returns a random valid move.
    """
    return random.choice(valid_moves)


# def orderMoves(game_state, moves):
#     """
#     Sắp xếp các nước đi theo thứ tự ưu tiên để cải thiện tốc độ tìm kiếm Alpha-beta:
#     1. Nước ăn quân (đặc biệt ưu tiên ăn quân có giá trị cao bằng quân có giá trị thấp)
#     2. Nước phong cấp tốt
#     3. Nước chiếu
#     4. Các nước đi khác
    
#     Trả về một danh sách nước đi đã được sắp xếp.
#     """
#     move_scores = []
    
#     for move in moves:
#         move_score = 0
        
#         # Ưu tiên 1: Nước ăn quân
#         if move.is_capture:
#             # Giá trị quân bị ăn - giá trị quân ăn (MVV-LVA: Most Valuable Victim - Least Valuable Aggressor)
#             captured_piece_value = piece_score[move.piece_captured[1]]
#             capturing_piece_value = piece_score[move.piece_moved[1]]
#             move_score = 10 * captured_piece_value - capturing_piece_value
        
#         # Ưu tiên 2: Phong cấp tốt (thường cho điểm cao vì tốt thành hậu rất mạnh)
#         if move.is_pawn_promotion:
#             move_score += 8  # Gần bằng ăn một con hậu
        
#         # Ưu tiên 3: Nước chiếu (thử nước đi để kiểm tra xem có chiếu không)
#         game_state.makeMove(move)
#         if game_state.inCheck():
#             move_score += 5  # Điểm cho nước chiếu
#         game_state.undoMove()
        
#         move_scores.append((move, move_score))
    
#     # Sắp xếp các nước đi theo điểm giảm dần
#     sorted_moves = [move for move, score in sorted(move_scores, key=lambda x: x[1], reverse=True)]
#     return sorted_moves

def orderMoves(game_state, moves):
    """
    Sắp xếp và chọn lọc nước đi theo chiến lược:
    1. Ưu tiên nước ăn quân (không quan tâm giá trị)
    2. Phong cấp tốt
    3. Nước chiếu
    4. Các nước còn lại

    Sau đó chọn 40% nước đi tốt nhất (khai thác) và 20% ngẫu nhiên trong phần còn lại (khám phá).
    """
    move_scores = []

    for move in moves:
        move_score = 0

        # Ưu tiên 1: Nước ăn quân (không quan tâm giá trị)
        if move.is_capture:
            move_score += 10  # điểm cao cho nước ăn

        # Ưu tiên 2: Phong cấp tốt
        if move.is_pawn_promotion:
            move_score += 8

        # Ưu tiên 3: Nước chiếu
        game_state.makeMove(move)
        if game_state.inCheck():
            move_score += 5
        game_state.undoMove()

        move_scores.append((move, move_score))

    # Sắp xếp theo điểm giảm dần
    sorted_moves = sorted(move_scores, key=lambda x: x[1], reverse=True)
    sorted_moves_only = [move for move, _ in sorted_moves]

    # Chọn 40% nước đi khai thác (tốt nhất)
    num_exploit = max(1, int(0.4 * len(sorted_moves_only)))
    exploit_moves = sorted_moves_only[:num_exploit]

    # Chọn 20% nước đi khám phá từ phần còn lại
    remaining_moves = sorted_moves_only[num_exploit:]
    num_explore = max(1, int(0.2 * len(sorted_moves_only))) if remaining_moves else 0
    explore_moves = random.sample(remaining_moves, min(num_explore, len(remaining_moves)))

    # Kết hợp
    final_moves = exploit_moves + explore_moves
    return final_moves
