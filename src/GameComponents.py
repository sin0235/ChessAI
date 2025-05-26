import pygame
from src.Const import *
from src.Config import *
import sys
from src.ChessEngine import *
import math
import os


# Lớp hỗ trợ kéo thả quân cờ
class Dragger:

    def __init__(self):
        # Khởi tạo các thuộc tính cho việc kéo thả
        self.piece = None
        self.dragging = False
        self.mouseX = 0
        self.mouseY = 0
        self.initialRow = 0
        self.initialCol  = 0

    # Cập nhật hình ảnh quân cờ khi kéo
    def updateBlit(self, surface, piece):
        img = pygame.image.load(f'./assets/images/imgs-128px/{piece}.png')
        img_center = (self.mouseX, self.mouseY)
        texture_rect = img.get_rect(center=img_center)
        surface.blit(img, texture_rect)

    # Cập nhật vị trí chuột
    def updateMouse(self, pos):
        self.mouseX, self.mouseY = pos 
        
    # Lưu vị trí bắt đầu kéo
    def saveInitial(self, pos):
        self.initialRow = pos[1] // SQUARE_SIZE
        self.initialCol  = pos[0] // SQUARE_SIZE

    # Bắt đầu kéo quân cờ
    def dragPiece(self, piece):
        self.piece = piece
        self.dragging = True

    # Dừng kéo quân cờ
    def undragPiece(self):
        self.piece = None
        self.dragging = False
        
    # Đặt lại tất cả trạng thái về mặc định
    def reset(self):
        self.piece = None
        self.dragging = False
        self.initialRow = 0
        self.initialCol = 0

# Lớp chứa các hiệu ứng hoạt hình và giao diện
class Animation:
    # Hiển thị lựa chọn phong cấp quân cờ
    def showPromotionOptions(game, row, col, color):
        boardSurface = game.mainScreen.copy()
        
        promotion_x = col * SQUARE_SIZE
        promotion_y = row * SQUARE_SIZE
        highlightAlpha = 0
        # Hiệu ứng làm sáng ô phong cấp
        while highlightAlpha < 180:
            game.mainScreen.blit(boardSurface, (0, 0))
            highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight.fill((255, 255, 100, highlightAlpha))  # Màu vàng nhạt
            game.mainScreen.blit(highlight, (promotion_x, promotion_y))
            pygame.draw.rect(game.mainScreen, (255, 215, 0), 
                            (promotion_x, promotion_y, SQUARE_SIZE, SQUARE_SIZE), 3)
            
            highlightAlpha += 10
            pygame.display.update()
            game.clock.tick(FPS)
        panelWidth  = 240
        panelHeight  = 100
        
        # Xác định vị trí panel phong cấp (trên/dưới)
        if row < 4: 
            panel_y = promotion_y + SQUARE_SIZE + 10
        else: 
            panel_y = promotion_y - panelHeight  - 10
        panel_y = max(10, min(HEIGHT - panelHeight  - 10, panel_y))

        panel_x = max(10, min(WIDTH - panelWidth  - 10, promotion_x - (panelWidth  - SQUARE_SIZE)/2))

        start_x = WIDTH + panelWidth 
        current_x = start_x
        target_x = panel_x
        
        # Hiệu ứng trượt panel vào màn hình
        while current_x > target_x:
            game.mainScreen.blit(boardSurface, (0, 0))
            highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight.fill((255, 255, 100, 180))
            game.mainScreen.blit(highlight, (promotion_x, promotion_y))
            pygame.draw.rect(game.mainScreen, (255, 215, 0), 
                            (promotion_x, promotion_y, SQUARE_SIZE, SQUARE_SIZE), 3)
            
            panel = pygame.Surface((panelWidth , panelHeight ), pygame.SRCALPHA)
            panel.fill((240, 240, 240, 200)) 

            pygame.draw.rect(panel, (70, 70, 70, 230), (0, 0, panelWidth , panelHeight ), 2)
            
            current_x -= 20
            if current_x < target_x:
                current_x = target_x
                
            game.mainScreen.blit(panel, (current_x, panel_y))
            pygame.display.update()
            game.clock.tick(FPS)
        
        # Vẽ panel phong cấp cuối cùng
        panel = pygame.Surface((panelWidth , panelHeight ), pygame.SRCALPHA)
        panel.fill((240, 240, 240, 200))
        pygame.draw.rect(panel, (70, 70, 70, 230), (0, 0, panelWidth , panelHeight ), 2)
        
        font = pygame.font.SysFont("monospace", 14, True)
        title = font.render("Chọn quân cờ phong cấp", True, (0, 0, 0))
        title_rect = title.get_rect(center=(panelWidth  // 2, 15))
        panel.blit(title, title_rect)
        
        pieceSize = 40
        piece_y = panelHeight  // 2 + 5
        spacing = 10
        pieces = ['Q', 'R', 'B', 'N']
        pieceRects = []
        total_width = 4 * pieceSize + 3 * spacing
        start_piece_x = (panelWidth  - total_width) // 2
        
        # Vẽ các lựa chọn quân cờ phong cấp
        for i, piece in enumerate(pieces):
            piece_x = start_piece_x + i * (pieceSize + spacing)
            pieceRect = pygame.Rect(piece_x, piece_y - 15, pieceSize, pieceSize)
            pieceRects.append(pieceRect)

            pygame.draw.rect(panel, (200, 200, 200, 180), pieceRect)
            pygame.draw.rect(panel, (100, 100, 100, 230), pieceRect, 2)
            
            pieceImage  = game.imageSmall[f"{color}{piece}"]
            pieceImage  = pygame.transform.scale(pieceImage , (pieceSize - 10, pieceSize - 10))
            panel.blit(pieceImage , (piece_x + 5, piece_y - 15 + 5))
        

        game.mainScreen.blit(panel, (panel_x, panel_y))
        pygame.display.update()

        waiting  = True
        chosenPiece = 'Q' 
        hoveredPiece = -1
        
        # Vòng lặp chờ người chơi chọn quân phong cấp
        while waiting :
            mousePosition = pygame.mouse.get_pos()
            positionRelative = (mousePosition[0] - panel_x, mousePosition[1] - panel_y)

            currentHover  = -1
            for i, rect in enumerate(pieceRects):
                if rect.collidepoint(positionRelative) and panel_x <= mousePosition[0] <= panel_x + panelWidth  and panel_y <= mousePosition[1] <= panel_y + panelHeight :
                    currentHover  = i
                    break

            # Hiệu ứng hover khi rê chuột lên quân cờ
            if currentHover  != hoveredPiece:
                hoveredPiece = currentHover 

                game.mainScreen.blit(boardSurface, (0, 0))
                highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                highlight.fill((255, 255, 100, 180))
                game.mainScreen.blit(highlight, (promotion_x, promotion_y))
                pygame.draw.rect(game.mainScreen, (255, 215, 0), 
                                (promotion_x, promotion_y, SQUARE_SIZE, SQUARE_SIZE), 3)
 
                panel = pygame.Surface((panelWidth , panelHeight ), pygame.SRCALPHA)
                panel.fill((240, 240, 240, 200))
                pygame.draw.rect(panel, (70, 70, 70, 230), (0, 0, panelWidth , panelHeight ), 2)

                panel.blit(title, title_rect)

                for i, piece in enumerate(pieces):
                    piece_x = start_piece_x + i * (pieceSize + spacing)
                    pieceRect = pieceRects[i]
                    
                    if i == hoveredPiece:
                        pygame.draw.rect(panel, (180, 210, 255, 230), pieceRect)
                        pygame.draw.rect(panel, (0, 120, 215, 255), pieceRect, 2)
                        
                    else:
                        pygame.draw.rect(panel, (200, 200, 200, 180), pieceRect)
                        pygame.draw.rect(panel, (100, 100, 100, 230), pieceRect, 2)
                    
                    pieceImage  = game.imageSmall[f"{color}{piece}"]
                    pieceImage  = pygame.transform.scale(pieceImage , (pieceSize - 10, pieceSize - 10))
                    panel.blit(pieceImage , (piece_x + 5, piece_y - 15 + 5))
                    

                game.mainScreen.blit(panel, (panel_x, panel_y))
                pygame.display.update()

            # Xử lý sự kiện chuột và bàn phím để chọn quân phong cấp
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        for i, rect in enumerate(pieceRects):
                            if rect.collidepoint(positionRelative) and panel_x <= mousePosition[0] <= panel_x + panelWidth  and panel_y <= mousePosition[1] <= panel_y + panelHeight :
                                chosenPiece = pieces[i]
                                pygame.draw.rect(panel, (160, 190, 255, 255), pieceRect)
                                pygame.draw.rect(panel, (0, 80, 185, 255), pieceRect, 2)
                                game.mainScreen.blit(panel, (panel_x, panel_y))
                                pygame.display.update()
                                pygame.time.delay(100)
                                
                                waiting  = False
                                break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        chosenPiece = 'Q'
                        waiting  = False
                    elif event.key == pygame.K_r:
                        chosenPiece = 'R'
                        waiting  = False
                    elif event.key == pygame.K_b:
                        chosenPiece = 'B'
                        waiting  = False
                    elif event.key == pygame.K_n:
                        chosenPiece = 'N'
                        waiting  = False
                    elif event.key == pygame.K_ESCAPE:
                        chosenPiece = 'Q'
                        waiting  = False
            
            game.clock.tick(FPS)
        
        # Hiệu ứng mờ dần khi đóng panel phong cấp
        for alpha in range(200, 0, -20):
            game.mainScreen.blit(boardSurface, (0, 0))
            highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight.fill((255, 255, 100, alpha))
            game.mainScreen.blit(highlight, (promotion_x, promotion_y))

            pygame.draw.rect(game.mainScreen, (255, 215, 0, alpha), 
                            (promotion_x, promotion_y, SQUARE_SIZE, SQUARE_SIZE), 3)

            panel = pygame.Surface((panelWidth , panelHeight ), pygame.SRCALPHA)
            panel.fill((240, 240, 240, alpha))
            pygame.draw.rect(panel, (70, 70, 70, alpha), (0, 0, panelWidth , panelHeight ), 2)
            game.mainScreen.blit(panel, (panel_x, panel_y))
            
            pygame.display.update()
            game.clock.tick(FPS)

        # Vẽ lại trạng thái bàn cờ sau khi chọn xong
        game.drawGameState()
        pygame.display.update()
        
        return chosenPiece

    # Hiệu ứng nhập thành (castle)
    def handleCastlingDisplay(game, move):
            """
            Hiệu ứng nhập thành
            """
            kingRowIndex = move.end_row
            if move.end_col - move.start_col == 2: 
                rookOldCol = 7
                rookNewCol  = move.end_col - 1
            else:  
                rookOldCol = 0
                rookNewCol  = move.end_col + 1
            
            oldColor = game.config.theme.bg[0] if (kingRowIndex + rookOldCol) % 2 == 0 else game.config.theme.bg[1]
            pygame.draw.rect(game.mainScreen, oldColor, 
                            (rookOldCol * SQUARE_SIZE, kingRowIndex * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
            pieceColor  = "w" if move.piece_moved[0] == "w" else "b"
            rookPiece  = f"{pieceColor }R"
            game.mainScreen.blit(game.imageSmall[rookPiece ], 
                                (rookNewCol  * SQUARE_SIZE + 5, kingRowIndex * SQUARE_SIZE + 5))
            
            pygame.display.update() 
            
    # Hiển thị hiệu ứng hover khi rê chuột lên ô cờ
    def showHover(game):
        if game.hoveredSquare:
            color = (200, 200, 100)
            row, col = game.hoveredSquare
            rect = (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(game.mainScreen, color, rect, width=3)
    
    # Hiển thị nước đi cuối cùng
    def showLastMove(game):
        theme = game.config.theme
        if len(game.gameState.move_log) > 0:
            lastMove = game.gameState.move_log[-1]
            initial = lastMove.start_row, lastMove.start_col
            final = lastMove.end_row, lastMove.end_col
            
            for position in [initial, final]:
                color = theme.trace[0] if (position[0] + position[1]) % 2 == 0 else theme.trace[1]
                pygame.draw.rect(game.mainScreen, color, (position[1] * SQUARE_SIZE, position[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
            # Nếu là nước nhập thành thì cũng highlight vị trí xe
            if lastMove.is_castle_move:
                if lastMove.end_col - lastMove.start_col == 2:  
                    rookInitial = (lastMove.end_row, 7)
                    rookFinal  = (lastMove.end_row, lastMove.end_col - 1)
                else:  
                    rookInitial = (lastMove.end_row, 0)
                    rookFinal  = (lastMove.end_row, lastMove.end_col + 1)
                
                for position in [rookInitial, rookFinal ]:
                    color = theme.trace[0] if (position[0] + position[1]) % 2 == 0 else theme.trace[1]
                    pygame.draw.rect(game.mainScreen, color, (position[1] * SQUARE_SIZE, position[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    # Hiển thị các nước đi hợp lệ cho quân cờ đang kéo
    def showMoves(game):
        theme = game.config.theme
        
        if game.dragger.dragging:
            piece = game.dragger.piece
            initialRow = game.dragger.initialRow
            initialCol  = game.dragger.initialCol 
            
            for move in game.validMoves:
                if move.start_row == initialRow and move.start_col == initialCol :
                    color = theme.move[0] if (move.end_row + move.end_col) % 2 == 0 else theme.move[1]
                    
                    # Nếu là nước nhập thành thì highlight cả ô vua và ô xe
                    if piece[1] == 'K' and abs(move.start_col - move.end_col) == 2:
                        rect = (move.end_col * SQUARE_SIZE, 
                               move.end_row * SQUARE_SIZE, 
                               SQUARE_SIZE, SQUARE_SIZE)
                        pygame.draw.rect(game.mainScreen, color, rect, width=3)
                        
                        if move.end_col > move.start_col:  
                            rookCol  = move.end_col - 1
                        else:  
                            rookCol  = move.end_col + 1
                        
                        rookRect = (rookCol  * SQUARE_SIZE, 
                                    move.end_row * SQUARE_SIZE, 
                                    SQUARE_SIZE, SQUARE_SIZE)
                        pygame.draw.rect(game.mainScreen, color, rookRect, width=3)
                    else:
                        # Nếu là nước ăn quân thì vẽ viền, còn nước đi thường thì vẽ chấm tròn
                        if game.gameState.board[move.end_row][move.end_col] != "--":
                            rect = (move.end_col * SQUARE_SIZE, 
                                   move.end_row * SQUARE_SIZE, 
                                   SQUARE_SIZE, SQUARE_SIZE)
                            pygame.draw.rect(game.mainScreen, color, rect, width=3)
                        else:
                            center = (move.end_col * SQUARE_SIZE + SQUARE_SIZE//2, 
                                    move.end_row * SQUARE_SIZE + SQUARE_SIZE//2)
                            radius = SQUARE_SIZE // 4
                            pygame.draw.circle(game.mainScreen, color, center, radius)
    
    # Hiển thị màn hình kết thúc ván cờ với hiệu ứng đẹp
    def showEndGameScreen(game, result_text, winner=None):
        board_surface = game.mainScreen.copy()
        
        # Phát âm thanh chiến thắng/thua/hòa
        try:
            if winner == "w":
                sound_file = './assets/sounds/victory.wav'
            elif winner == "b":
                sound_file = './assets/sounds/lose.wav'
            else:
                # Nếu hòa thì dùng âm thanh chiến thắng làm mặc định
                sound_file = './assets/sounds/victory.wav'
                
            victorySound = pygame.mixer.Sound(sound_file)
            victorySound.play()
        except Exception as e:
            print(f"Sound error: {e}")
        
        # Hiệu ứng mờ dần nền bàn cờ
        for alpha in range(0, 100, 5):  
            game.mainScreen.blit(board_surface, (0, 0))
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((20, 20, 50, alpha))  
            game.mainScreen.blit(overlay, (0, 0))
            pygame.display.update()
            game.clock.tick(FPS)

        # Tạo nền bán trong suốt cho màn hình kết thúc
        background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        background.fill((20, 20, 50, 100))  

        # Thêm hình trang trí (quân cờ mờ) vào nền
        piece_img = pygame.image.load("./assets/images/imgs-128px/wK.png")
        piece_img = pygame.transform.scale(piece_img, (80, 80))
        piece_img.set_alpha(40)  
        background.blit(piece_img, (WIDTH-100, 50))
            
        piece_img = pygame.image.load("./assets/images/imgs-128px/bQ.png")
        piece_img = pygame.transform.scale(piece_img, (80, 80))
        piece_img.set_alpha(40)  
        background.blit(piece_img, (50, HEIGHT-130))
        # Vẽ viền trang trí cho màn hình kết thúc
        border_width = 5
        pygame.draw.rect(background, (200, 170, 100, 200), (40, 40, WIDTH-80, HEIGHT-80), border_width)
        
        # Khởi tạo font chữ cho các thành phần giao diện
        title_font = pygame.font.Font(None, 72)  
        subtitle_font = pygame.font.Font(None, 36)
        stats_font = pygame.font.Font(None, 24)
        button_font = pygame.font.Font(None, 28)
        
        try:
            # Thử tải font tùy chỉnh nếu có
            title_font = pygame.font.Font("./assets/fonts/Roboto-Bold.ttf", 72)
            subtitle_font = pygame.font.Font("./assets/fonts/Roboto-Medium.ttf", 42)
            stats_font = pygame.font.Font("./assets/fonts/Roboto-Regular.ttf", 24)
            button_font = pygame.font.Font("./assets/fonts/Roboto-Medium.ttf", 32)
        except:
            print("Custom fonts not found, using system fonts")

        # Thiết lập nội dung và màu sắc tiêu đề chính
        if winner == "w":
            main_text = "VICTORY!"
            main_color = (240, 200, 75)  
            highlight_color = (255, 230, 100)
        elif winner == "b":
            main_text = "DEFEATED"
            main_color = (200, 70, 70)  
            highlight_color = (230, 100, 100)
        else:
            main_text = "STALEMATE"
            main_color = (100, 180, 220)  
            highlight_color = (150, 210, 240)

        # Hiệu ứng phóng to tiêu đề chính
        for size in range(30, 72, 3):
            game.mainScreen.blit(board_surface, (0, 0))  
            game.mainScreen.blit(background, (0, 0))  

            temp_font = pygame.font.Font(None, size)
            try:
                temp_font = pygame.font.Font("./assets/fonts/Roboto-Bold.ttf", size)
            except:
                pass
                
            # Nền mờ cho tiêu đề
            text_bg_width = temp_font.size(main_text)[0] + 40
            text_bg_height = temp_font.size(main_text)[1] + 20
            text_bg = pygame.Surface((text_bg_width, text_bg_height), pygame.SRCALPHA)
            text_bg.fill((10, 10, 30, 150))  
            text_bg_rect = text_bg.get_rect(center=(WIDTH//2, HEIGHT//4))
            game.mainScreen.blit(text_bg, text_bg_rect)
            
            # Đổ bóng cho tiêu đề
            shadow_surface = temp_font.render(main_text, True, (30, 30, 30))
            shadow_rect = shadow_surface.get_rect(center=(WIDTH//2+5, HEIGHT//4+5))
            game.mainScreen.blit(shadow_surface, shadow_rect)
            
            # Vẽ tiêu đề chính
            text_surface = temp_font.render(main_text, True, main_color)
            text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//4))
            game.mainScreen.blit(text_surface, text_rect)
            
            pygame.display.update()
            game.clock.tick(FPS)
        
        # Lưu lại các đối tượng tiêu đề cuối cùng
        title_shadow = title_font.render(main_text, True, (30, 30, 30))
        title_shadow_rect = title_shadow.get_rect(center=(WIDTH//2+5, HEIGHT//4+5))
        
        title_text = title_font.render(main_text, True, main_color)
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//4))
        
        # Nền mờ cho tiêu đề
        title_bg_width = title_font.size(main_text)[0] + 60
        title_bg_height = title_font.size(main_text)[1] + 30
        title_bg = pygame.Surface((title_bg_width, title_bg_height), pygame.SRCALPHA)
        title_bg.fill((10, 10, 30, 150))  
        title_bg_rect = title_bg.get_rect(center=(WIDTH//2, HEIGHT//4))
        
        # Nền cho phụ đề - Di chuyển phụ đề xuống dưới, tăng khoảng cách với tiêu đề chính
        subtitle_text = subtitle_font.render(result_text, True, (230, 230, 230))
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH//2, HEIGHT//4 + 120))
        
        subtitle_bg_width = subtitle_font.size(result_text)[0] + 60
        subtitle_bg_height = subtitle_font.size(result_text)[1] + 20
        subtitle_bg = pygame.Surface((subtitle_bg_width, subtitle_bg_height), pygame.SRCALPHA)
        subtitle_bg.fill((10, 10, 30, 150))
        subtitle_bg_rect = subtitle_bg.get_rect(center=(WIDTH//2, HEIGHT//4 + 120))
        
        # Biến lưu nút đang được hover
        active_button = None
        
        # Hiệu ứng mờ dần cho phụ đề
        for alpha in range(0, 255, 10):
            game.mainScreen.blit(board_surface, (0, 0))
            game.mainScreen.blit(background, (0, 0))  

            game.mainScreen.blit(title_bg, title_bg_rect)
            game.mainScreen.blit(title_shadow, title_shadow_rect)
            game.mainScreen.blit(title_text, title_rect)
            
            game.mainScreen.blit(subtitle_bg, subtitle_bg_rect)
            temp_surface = subtitle_font.render(result_text, True, (230, 230, 230, alpha))
            game.mainScreen.blit(temp_surface, subtitle_rect)
            
            pygame.display.update()
            game.clock.tick(FPS)
        
        # Tạo các nút chức năng
        buttons = [
            {"text": "Chơi lại (R)", "rect": pygame.Rect(0, 0, 200, 60), "action": "restart"},
            {"text": "Menu (M)", "rect": pygame.Rect(0, 0, 200, 60), "action": "menu"},
            {"text": "Thoát (ESC)", "rect": pygame.Rect(0, 0, 200, 60), "action": "exit"}
        ]
        
        # Đặt vị trí các nút - khoảng cách lớn hơn giữa các nút
        button_y = HEIGHT - 150
        button_spacing = 250
        for i, button in enumerate(buttons):
            button["rect"].center = (WIDTH//2 - button_spacing + i*button_spacing, button_y)
        
        # Hiệu ứng mờ dần cho nút
        for alpha in range(0, 255, 10):
            game.mainScreen.blit(board_surface, (0, 0))  
            game.mainScreen.blit(background, (0, 0))  

            game.mainScreen.blit(title_bg, title_bg_rect)
            game.mainScreen.blit(title_shadow, title_shadow_rect)
            game.mainScreen.blit(title_text, title_rect)
            game.mainScreen.blit(subtitle_bg, subtitle_bg_rect)
            game.mainScreen.blit(subtitle_text, subtitle_rect)
            
            for button in buttons:
                # Nền nút với hiệu ứng mờ dần
                button_bg = pygame.Surface((button["rect"].width, button["rect"].height), pygame.SRCALPHA)
                button_bg.fill((40, 40, 60, alpha))  # Nền nút
                game.mainScreen.blit(button_bg, button["rect"].topleft)
                
                # Viền nút với alpha
                pygame.draw.rect(game.mainScreen, (*main_color, alpha), button["rect"], 2, border_radius=10)
                
                # Chữ trên nút
                button_text = button_font.render(button["text"], True, (220, 220, 220, alpha))
                button_text_rect = button_text.get_rect(center=button["rect"].center)
                game.mainScreen.blit(button_text, button_text_rect)
            
            pygame.display.update()
            game.clock.tick(FPS)
        
        # Vòng lặp chính cho màn hình kết thúc
        waiting_for_key = True
        pulse_time = 0
        
        while waiting_for_key:
            # Xử lý sự kiện bàn phím và chuột
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game.gameState = GameState()
                        game.validMoves = game.gameState.getValidMoves()
                        game.game_over = False
                        waiting_for_key = False
                    elif event.key == pygame.K_m:
                        # Quay về menu chính
                        pygame.quit()
                        python = sys.executable
                        os.execl(python, python, *sys.argv)
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                
                # Sự kiện chuột cho nút
                elif event.type == pygame.MOUSEMOTION:
                    active_button = None
                    for button in buttons:
                        if button["rect"].collidepoint(event.pos):
                            active_button = button
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button in buttons:
                        if button["rect"].collidepoint(event.pos):
                            if button["action"] == "restart":
                                game.gameState = GameState()
                                game.validMoves = game.gameState.getValidMoves()
                                game.game_over = False
                                waiting_for_key = False
                            elif button["action"] == "menu":
                                pygame.quit()
                                python = sys.executable
                                os.execl(python, python, *sys.argv)
                            elif button["action"] == "exit":
                                pygame.quit()
                                sys.exit()
            
            # Cập nhật hiệu ứng giao diện
            game.mainScreen.blit(board_surface, (0, 0))  
            game.mainScreen.blit(background, (0, 0))  

            # Hiệu ứng nhấp nháy cho tiêu đề
            pulse_time += 0.05
            pulse_value = abs(math.sin(pulse_time)) * 30
            
            # Tiêu đề với hiệu ứng nhấp nháy
            title_glow = title_font.render(main_text, True, (
                min(main_color[0] + pulse_value, 255),
                min(main_color[1] + pulse_value, 255),
                min(main_color[2] + pulse_value, 255)
            ))
            
            game.mainScreen.blit(title_bg, title_bg_rect)
            game.mainScreen.blit(title_shadow, title_shadow_rect)
            game.mainScreen.blit(title_glow, title_rect)
            game.mainScreen.blit(subtitle_bg, subtitle_bg_rect)
            game.mainScreen.blit(subtitle_text, subtitle_rect)
            
            # Vẽ các nút với hiệu ứng hover
            for button in buttons:
                # Nền nút
                pygame.draw.rect(game.mainScreen, (60, 60, 80), button["rect"], 0, border_radius=10)
                
                # Viền sáng nếu đang hover
                if button == active_button:
                    pygame.draw.rect(game.mainScreen, highlight_color, button["rect"], 3, border_radius=10)
                else:
                    pygame.draw.rect(game.mainScreen, main_color, button["rect"], 2, border_radius=10)
                
                # Chữ trên nút
                button_text = button_font.render(button["text"], True, (220, 220, 220))
                button_text_rect = button_text.get_rect(center=button["rect"].center)
                game.mainScreen.blit(button_text, button_text_rect)
            
            pygame.display.update()
            game.clock.tick(FPS)
        
        # Hiệu ứng mờ dần khi thoát màn hình kết thúc
        for alpha in range(150, 0, -5):
            game.mainScreen.blit(board_surface, (0, 0))
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((20, 20, 50, alpha))
            game.mainScreen.blit(overlay, (0, 0))
            
            pygame.display.update()
            game.clock.tick(FPS)

    # Hàm gọi nhanh để hiển thị màn hình kết thúc dựa vào kết quả
    def drawEndGameText(game, result_text):
        winner = None
        if "White wins" in result_text or "Trắng thắng" in result_text:
            winner = "w"
        elif "Black wins" in result_text or "Đen thắng" in result_text:
            winner = "b"
        Animation.showEndGameScreen(game, result_text, winner)
        
    # Hiệu ứng cảnh báo khi vua bị chiếu
    def highlightChecks(game):
        # Nếu vua đang bị chiếu
        if game.gameState.inCheck():  
            # Xác định vị trí vua
            king_row, king_col = game.gameState.white_king_location if game.gameState.white_to_move else game.gameState.black_king_location
            
            # Tính alpha cho hiệu ứng nhấp nháy
            flash_speed = 0.004  # Tốc độ nhấp nháy
            alpha = int(80 + 60 * math.sin(pygame.time.get_ticks() * flash_speed))  # Dao động alpha
            
            # Nền đỏ cảnh báo
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            s.fill((255, 100, 100, alpha))  # Đỏ nhấp nháy
            game.mainScreen.blit(s, (king_col * SQUARE_SIZE, king_row * SQUARE_SIZE))
            
            # Viền nhấp nháy nổi bật
            border_alpha = min(150, alpha + 50)
            border_color = (255, 150, 150, border_alpha)
            border_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(border_surface, border_color, (0, 0, SQUARE_SIZE, SQUARE_SIZE), 2)
            game.mainScreen.blit(border_surface, (king_col * SQUARE_SIZE, king_row * SQUARE_SIZE))