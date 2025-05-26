import os
import pygame
from src.ChessEngine import *
from src.ChessAI import *
from multiprocessing import Process, Queue
import ctypes
from src.Const import *
from src.Config import *
from src.GameComponents import *
from src.PGNExporter import PGNExporter

class Game:
    def __init__(self, game_mode='pvp', difficulty=1, algorithm=ALGORITHM_WITH_PRUNING):
        """
        Khởi tạo trò chơi cờ vua với chế độ cụ thể
        game_mode: 'pvp' cho chế độ Người đấu Người, 'ai' cho chế độ Người đấu Máy
        difficulty: Độ khó của AI (1-5)
        algorithm: Thuật toán AI sử dụng (negamax hoặc minimax)
        """
        # Khởi tạo pygame
        pygame.init()
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
        self.config = Config()
        self.mainScreen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Chess Game')
        pygame.display.set_icon(pygame.image.load('./assets/images/logo/logo.png'))
        if os.name == 'nt':
            myappid = 'chess.game.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # Khởi tạo trạng thái trò chơi
        self.gameState = GameState()
        self.validMoves = self.gameState.getValidMoves()
        
        # Tải hình ảnh quân cờ
        self.imageSmall = {}
        self.imageBig = {}
        self.loadImages()
        
        # Khởi tạo các biến theo dõi trạng thái
        self.captured = False
        self.hoveredSquare = None
        self.dragger = Dragger()
        
        # Thiết lập chế độ chơi
        self.game_mode = game_mode
        self.player_one = True  # Bên trắng luôn là người chơi
        
        # Thiết lập riêng cho chế độ đấu với máy
        if game_mode == 'ai':
            self.player_two = False  # Bên đen là AI trong chế độ đấu với máy
            self.ai_thinking = False
            self.move_finder_process = None
        else:
            self.player_two = True  # Bên đen là người trong chế độ đấu người-người
            self.ai_thinking = False
            self.move_finder_process = None
            
        self.move_undone = False
        self.game_over = False
        self.difficulty = difficulty
        self.algorithm = algorithm

        # Tải âm thanh (nếu có)
        try:
                self.config.castleSound = pygame.mixer.Sound('./assets/sounds/castle.wav')
        except:
            pass

    def mainLoop(self):
        """Vòng lặp chính của trò chơi, xử lý cả chế độ đấu người và đấu máy"""
        running = True
        while running:
            # Xác định lượt đi dựa trên người chơi hiện tại và chế độ chơi
            human_turn = (self.gameState.white_to_move and self.player_one) or (
                          not self.gameState.white_to_move and self.player_two)

            # Vẽ trạng thái hiện tại của bàn cờ
            self.drawGameState()
            Animation.highlightChecks(self)

            # Xử lý hiệu ứng kéo thả và hover
            if not self.dragger.dragging:
                Animation.showHover(self)

            if self.dragger.dragging:
                Animation.showMoves(self)
                self.dragger.updateBlit(self.mainScreen, self.dragger.piece)

            # Xử lý các sự kiện người dùng
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Khi người dùng nhấn nút đóng cửa sổ (X), quay về menu chính
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    motionRow = event.pos[1] // SQUARE_SIZE
                    motionCol = event.pos[0] // SQUARE_SIZE

                    self.setHover(motionRow, motionCol)
                    self.dragger.updateMouse(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Xử lý việc di chuyển quân cờ
                    if event.button == 1 and human_turn and not self.game_over:
                        clickRow = event.pos[1] // SQUARE_SIZE
                        clickCol = event.pos[0] // SQUARE_SIZE

                        if 0 <= clickRow < ROWS and 0 <= clickCol < COLS:
                            piece = self.gameState.board[clickRow][clickCol]
                            if piece != "--" and (
                                    (piece[0] == "w" and self.gameState.white_to_move) or
                                    (piece[0] == "b" and not self.gameState.white_to_move)):
                                self.dragger.saveInitial(event.pos)
                                self.dragger.dragPiece(piece)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.dragger.dragging and human_turn and not self.game_over:
                        releaseRow = event.pos[1] // SQUARE_SIZE
                        releaseCol = event.pos[0] // SQUARE_SIZE

                        if 0 <= releaseRow < ROWS and 0 <= releaseCol < COLS:
                            move = Move((self.dragger.initialRow, self.dragger.initialCol),
                                        (releaseRow, releaseCol),
                                        self.gameState.board)
                            # Xử lý nước đi bắt tốt qua đường (en passant)
                            # Chỉ đánh dấu là en passant khi đúng là tốt đi chéo vào vị trí enpassant_possible
                            if (move.piece_moved[1] == 'p' and                        # Quân di chuyển là tốt
                                abs(move.start_row - move.end_row) == 1 and           # Di chuyển 1 ô theo chiều dọc
                                abs(move.start_col - move.end_col) == 1 and           # Di chuyển 1 ô theo chiều ngang (chéo)
                                self.gameState.board[move.end_row][move.end_col] == "--" and  # Ô đích trống
                                (move.end_row, move.end_col) == self.gameState.enpassant_possible):  # Vị trí khớp với enpassant_possible
                                
                                # Xác minh quân bị bắt là quân tốt đối phương
                                captured_row = move.end_row + 1 if move.piece_moved[0] == 'w' else move.end_row - 1
                                captured_piece = self.gameState.board[captured_row][move.end_col]
                                
                                if captured_piece[1] == 'p' and captured_piece[0] != move.piece_moved[0]:
                                    move.is_enpassant_move = True

                            # Xử lý nước đi nhập thành
                            is_castle = False
                            if move.piece_moved[1] == 'K' and abs(move.start_col - move.end_col) == 2:
                                is_castle = True
                                move.is_castle_move = True
                            
                            self.validMoves = self.gameState.getValidMoves()
                            if move in self.validMoves:
                                print(f"Move: {move.start_row, move.start_col} -> {move.end_row, move.end_col}")
                                self.captured = self.gameState.board[releaseRow][releaseCol] != "--"
                                promotion_piece = 'Q'  # Mặc định là hậu
                                if move.is_pawn_promotion and human_turn:
                                    promotion_piece = Animation.showPromotionOptions(self, releaseRow, releaseCol, move.piece_moved[0])
                                    move.promotion_choice = promotion_piece
                                
                                # Thực hiện nước đi
                                self.gameState.makeMove(move, promotion_piece)
                                
                                # Cập nhật trạng thái chiếu/chiếu hết
                                self.validMoves = self.gameState.getValidMoves()
                                # Đánh dấu vào nước đi nếu gây ra chiếu hoặc chiếu hết
                                move.is_check = self.gameState.in_check
                                move.is_checkmate = self.gameState.checkmate
                                
                                if is_castle:
                                    Animation.handleCastlingDisplay(self, move)
                                    
                                self.playSound()
                                self.move_undone = False
                                self.dragger.reset()

                        self.dragger.undragPiece()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # Phím Escape để quay về menu chính
                        running = False
                    if event.key == pygame.K_z:  # Phím Z để hoàn tác nước đi
                        self.gameState.undoMove()
                        # if  not human_turn:
                        #     self.gameState.undoMove()
                        self.validMoves = self.gameState.getValidMoves()
                        self.move_undone = True
                        self.game_over = False
                        if self.ai_thinking:
                            self.move_finder_process.terminate()
                            self.ai_thinking = False
                    if event.key == pygame.K_r:  # Phím R để khởi động lại ván cờ
                        self.gameState = GameState()
                        self.validMoves = self.gameState.getValidMoves()
                        self.dragger.undragPiece()
                        self.game_over = False
                        if self.ai_thinking:
                            self.move_finder_process.terminate()
                            self.ai_thinking = False
                        self.move_undone = True
                    if event.key == pygame.K_n:  # Phím N để thay đổi giao diện
                        self.changeTheme()
                    if event.key == pygame.K_e:  # Phím E để xuất ván cờ ra file PGN
                        exporter = PGNExporter(self.gameState)
                        exporter.export_to_file()
                

            # Xử lý nước đi của AI (chỉ trong chế độ đấu với máy và khi đến lượt AI)
            if self.game_mode == 'ai' and not self.game_over and not human_turn and not self.move_undone:
                if not self.ai_thinking:
                    self.ai_thinking = True
                    return_queue = Queue()
                    self.move_finder_process = Process(target=findBestMove,
                                                       args=(self.gameState, self.validMoves, return_queue, self.difficulty, self.algorithm))
                    self.move_finder_process.start()

                if not self.move_finder_process.is_alive():
                    ai_move = return_queue.get()
                    if ai_move is None:
                        ai_move = findRandomMove(self.validMoves)
                        
                    is_castle = False
                    if ai_move.piece_moved[1] == 'K' and abs(ai_move.start_col - ai_move.end_col) == 2:
                        is_castle = True
                        ai_move.is_castle_move = True
                        
                    promotion_piece = 'Q'
                    if ai_move.is_pawn_promotion:
                        ai_move.promotion_choice = promotion_piece
                        
                    self.gameState.makeMove(ai_move, promotion_piece)
                        
                    if is_castle:
                        Animation.handleCastlingDisplay(self, ai_move)
                        
                    self.validMoves = self.gameState.getValidMoves()
                    # Đánh dấu vào nước đi nếu gây ra chiếu hoặc chiếu hết
                    ai_move.is_check = self.gameState.in_check
                    ai_move.is_checkmate = self.gameState.checkmate
                    
                    self.ai_thinking = False
                    self.move_undone = False
                    self.playSound()


            # Kiểm tra trạng thái kết thúc ván đấu
            if self.gameState.checkmate or self.gameState.stalemate or self.gameState.fifty_move_rule or self.gameState.threefold_repetition or self.gameState.insufficient_material:
                self.game_over = True
                self.drawGameState()
                Animation.highlightChecks(self)

                # Xác định kết quả
                if self.gameState.checkmate:
                    result = "1-0" if not  self.gameState.white_to_move else "0-1"
                    message = "Đen thắng bằng chiếu hết" if self.gameState.white_to_move else "Trắng thắng bằng chiếu hết"
                else:  # Hòa
                    result = "1/2-1/2"
                    if self.gameState.stalemate:
                        message = "Hòa do hết nước đi"
                    elif self.gameState.threefold_repetition:
                        message = "Hòa do lặp lại nước đi 3 lần"
                    elif self.gameState.fifty_move_rule:
                        message = "Hòa do luật 50 nước"
                    else:  # insufficient_material
                        message = "Hòa do không đủ quân chiếu hết"
                exporter = PGNExporter(self.gameState)
                exporter.export_to_file(result=result)  
                print(f"Game ended: {message}")
                Animation.drawEndGameText(self, message)


                pygame.display.update()
                pygame.time.delay(750)  
            self.clock.tick(FPS)
            pygame.display.update()
            
        # Quay về menu khi thoát vòng lặp game
        return
        
    def drawGameState(self):
        """Vẽ trạng thái hiện tại của bàn cờ"""
        self.drawBoard()
        Animation.showLastMove(self)
        self.showPieces()
    
    def drawBoard(self):
        """Vẽ bàn cờ"""
        theme = self.config.theme
        for row in range(ROWS):
            for col in range(COLS):
                color = theme.bg[0] if (row + col) % 2 == 0 else theme.bg[1]
                pygame.draw.rect(self.mainScreen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                if col == 0:
                    color = theme.bg[1] if row % 2 == 0 else theme.bg[0]
                    text = self.config.font.render(str(8 - row), 1, color)
                    self.mainScreen.blit(text, (5, 5 + row * SQUARE_SIZE))
                if row == 7:
                    color = theme.bg[0] if col % 2 == 0 else theme.bg[1]
                    text = self.config.font.render(chr(97 + col), 1, color)
                    self.mainScreen.blit(text, (col * SQUARE_SIZE + SQUARE_SIZE - 18, HEIGHT - 18))
                    
    def showPieces(self):
        """Hiển thị các quân cờ trên bàn cờ"""
        board = self.gameState.board
        for row in range(ROWS):
            for col in range(COLS):
                piece = board[row][col]
                if piece != "--":
                    if not (self.dragger.dragging and row == self.dragger.initialRow and col == self.dragger.initialCol):
                        pieceImg = self.imageSmall[piece]
                        self.mainScreen.blit(pieceImg, (col * SQUARE_SIZE + 5, row * SQUARE_SIZE + 5))
    
    def loadImages(self):
        """Tải hình ảnh các quân cờ"""
        for piece in PIECES:
            self.imageSmall[piece] = pygame.image.load(f'./assets/images/imgs-80px/{piece}.png')
            self.imageBig[piece] = pygame.image.load(f'./assets/images/imgs-128px/{piece}.png')
    
    def setHover(self, row, col):
        """Thiết lập ô được hover"""
        if 0 <= row < 8 and 0 <= col < 8:
            self.hoveredSquare = (row, col)
        else:
            self.hoveredSquare = None
    
    def playSound(self):
        try:
            if self.captured:
                self.config.captureSound.play()
                self.captured = False
            else:
                # Check if it's a castle move
                if len(self.gameState.move_log) > 0 and self.gameState.move_log[-1].is_castle_move:
                    if hasattr(self.config, 'castleSound'):
                        self.config.castleSound.play()
                    else:
                        if hasattr(self.config, 'moveSound'):
                            self.config.moveSound.play()
                else:
                    if hasattr(self.config, 'moveSound'):
                        self.config.moveSound.play()
        except Exception as e:
            print(f"Sound error: {e}")
    
    def changeTheme(self):
        """Thay đổi giao diện bàn cờ"""
        self.config.changeTheme()

    

# Các hàm để khởi động game ở các chế độ khác nhau
def run_pvp_game():
    """Chạy game ở chế độ người đấu người"""
    game = Game(game_mode='pvp')
    game.mainLoop()

def run_ai_game(difficulty=1, algorithm=ALGORITHM_WITH_PRUNING):
    """
    Chạy game ở chế độ người đấu máy
    
    Tham số:
    - difficulty: Độ khó của AI (1-5)
    - algorithm: Thuật toán AI (with_pruning hoặc without_pruning)
    """
    game = Game(game_mode='ai', difficulty=difficulty, algorithm=algorithm)
    game.mainLoop()


if __name__ == "__main__":
    # Khi chạy trực tiếp, hiển thị menu
    from src.ChessMenu import Menu
    menu = Menu()
    menu.run()
