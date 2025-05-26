import pygame
import sys
import os
from src.Const import *
from src.Config import *
from src.WindowManager import WindowManager
from src.ChessMain_Module import run_pvp_game, run_ai_game
from src.ChessAI import ALGORITHM_WITH_PRUNING, ALGORITHM_WITHOUT_PRUNING

class Menu:
    def __init__(self):
        # Khởi tạo pygame
        pygame.init()

        try:
            pygame.mixer.init()
            print("Pygame mixer initialized successfully")
        except Exception as e:
            print(f"Error initializing pygame mixer: {e}")
        
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
        
        # Tải cấu hình
        self.config = Config()
        
        # Thiết lập màn hình
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chess Game')
        pygame.display.set_icon(pygame.image.load('./assets/images/logo/logo.png'))
        
        # Tải font chữ
        self.title_font = pygame.font.Font('./assets/fonts/Roboto-Bold.ttf', 72)
        self.subtitle_font = pygame.font.Font('./assets/fonts/Roboto-Medium.ttf', 42)
        self.button_font = pygame.font.Font('./assets/fonts/Roboto-Regular.ttf', 36)
        
        # Màu sắc
        self.theme = self.config.theme
        self.button_colors = {
            'normal': (80, 80, 90),
            'hover': (120, 120, 140),
            'text': (240, 240, 240)
        }
        
        # Kích thước nút
        self.button_width = 300
        self.button_height = 60
        self.button_margin = 30
        
        # Khởi tạo biến trạng thái menu
        self.show_difficulty_menu = False
        self.show_algorithm_menu = False
        self.selected_difficulty = 2  # Mặc định là dễ
        self.selected_algorithm = ALGORITHM_WITH_PRUNING  # Mặc định là có cắt tỉa alpha-beta
        
        # Tạo các nút bấm cho menu chính
        center_x = WIDTH // 2
        start_y = HEIGHT // 2 - 50
        
        self.buttons = [
            {
                'rect': pygame.Rect(center_x - self.button_width // 2, start_y, 
                                  self.button_width, self.button_height),
                'text': 'Player vs Player',
                'action': 'pvp'
            },
            {
                'rect': pygame.Rect(center_x - self.button_width // 2, 
                                  start_y + self.button_height + self.button_margin, 
                                  self.button_width, self.button_height),
                'text': 'Player vs AI',
                'action': 'ai_menu'
            },
            {
                'rect': pygame.Rect(center_x - self.button_width // 2, 
                                  start_y + 2 * (self.button_height + self.button_margin), 
                                  self.button_width, self.button_height),
                'text': 'Exit',
                'action': 'exit'
            }
        ]
        
        # Định nghĩa vị trí bắt đầu cho các nút trong menu độ khó
        difficulty_start_y = HEIGHT // 2
        
        # Nút cho menu độ khó AI
        self.difficulty_buttons = [
            {
                'rect': pygame.Rect(center_x - self.button_width // 2, difficulty_start_y, 
                                  self.button_width, self.button_height),
                'text': 'Dễ',
                'action': 'difficulty_easy'
            },
            {
                'rect': pygame.Rect(center_x - self.button_width // 2, 
                                  difficulty_start_y + self.button_height + self.button_margin, 
                                  self.button_width, self.button_height),
                'text': 'Trung bình',
                'action': 'difficulty_medium'
            },
            {
                'rect': pygame.Rect(center_x - self.button_width // 2, 
                                  difficulty_start_y + 2 * (self.button_height + self.button_margin), 
                                  self.button_width, self.button_height),
                'text': 'Khó',
                'action': 'difficulty_hard'
            },
            {
                'rect': pygame.Rect(center_x - self.button_width // 2, 
                                  difficulty_start_y + 3 * (self.button_height + self.button_margin), 
                                  self.button_width, self.button_height),
                'text': 'Quay lại',
                'action': 'back'
            }
        ]
        
        # Nút cho menu chọn thuật toán AI
        self.algorithm_buttons = [
            {
                'rect': pygame.Rect(center_x - self.button_width // 2, difficulty_start_y, 
                                  self.button_width, self.button_height),
                'text': 'Có cắt tỉa',
                'action': 'algorithm_with_pruning'
            },
            {
                'rect': pygame.Rect(center_x - self.button_width // 2, 
                                  difficulty_start_y + self.button_height + self.button_margin, 
                                  self.button_width, self.button_height),
                'text': 'Không cắt tỉa',
                'action': 'algorithm_without_pruning'
            },
            {
                'rect': pygame.Rect(center_x - self.button_width // 2, 
                                  difficulty_start_y + 2 * (self.button_height + self.button_margin), 
                                  self.button_width, self.button_height),
                'text': 'Quay lại',
                'action': 'back_to_difficulty'
            }
        ]
        
        # Tải hình nền từ file
        try:
            self.background = pygame.image.load('./assets/images/background.jpg')
            self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
            self.has_background_image = True
        except (pygame.error, FileNotFoundError):
            print("Không thể tải hình nền, sử dụng nền mặc định")
            self.has_background_image = False
            # Tạo hình nền mặc định (bàn cờ)
            self.background = pygame.Surface((WIDTH, HEIGHT))
            square_size = SQUARE_SIZE // 2
            for row in range(0, HEIGHT, square_size):
                for col in range(0, WIDTH, square_size):
                    color = self.theme.bg[0] if (row // square_size + col // square_size) % 2 == 0 else self.theme.bg[1]
                    pygame.draw.rect(self.background, color, (col, row, square_size, square_size))
    
    def draw(self):
        # Vẽ hình nền
        self.screen.blit(self.background, (0, 0))
        
        # Thêm lớp mờ cho nền để văn bản dễ đọc hơn nếu có hình nền tùy chỉnh
        if self.has_background_image:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # RGBA với độ trong suốt 150/255
            self.screen.blit(overlay, (0, 0))
        
        # Vẽ tiêu đề
        title_text = self.title_font.render("Chess Game", True, (255, 255, 255))
        # Điều chỉnh vị trí tiêu đề chính lên cao hơn
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 6))
        
        # Tạo hiệu ứng đổ bóng cho tiêu đề
        shadow_text = self.title_font.render("Chess Game", True, (50, 50, 50))
        shadow_rect = shadow_text.get_rect(center=(WIDTH // 2 + 4, HEIGHT // 6 - 16 + 20))
        self.screen.blit(shadow_text, shadow_rect)
        
        # Tạo hộp tiêu đề nửa trong suốt với gradient
        title_box = title_rect.inflate(120, 60)
        title_surface = pygame.Surface((title_box.width, title_box.height), pygame.SRCALPHA)
        
        # Tạo gradient từ tối sang sáng ở giữa rồi về tối
        for i in range(title_box.height):
            alpha = 150
            # Tạo hiệu ứng gradient
            darkness = 20 + int(35 * (1 - abs(i - title_box.height/2) / (title_box.height/2)))
            pygame.draw.line(title_surface, (darkness, darkness, darkness+10, alpha), 
                            (0, i), (title_box.width, i))
        
        self.screen.blit(title_surface, title_box)
        
        # Vẽ viền cho hộp tiêu đề với hiệu ứng ánh sáng
        pygame.draw.rect(self.screen, (200, 200, 210), title_box, 2, border_radius=15)
        pygame.draw.rect(self.screen, (100, 100, 110), title_box.inflate(4, 4), 1, border_radius=16)
        
        # Vẽ tiêu đề
        self.screen.blit(title_text, title_rect)
        
        # Vẽ các nút bấm
        mouse_pos = pygame.mouse.get_pos()
        
        # Chọn danh sách nút dựa trên trạng thái menu
        if self.show_algorithm_menu:
            current_buttons = self.algorithm_buttons
        elif self.show_difficulty_menu:
            current_buttons = self.difficulty_buttons
        else:
            current_buttons = self.buttons
        
        # Vẽ tiêu đề phụ cho menu
        subtitle_text = None
        subtitle_str = ""
        if self.show_difficulty_menu:
            subtitle_str = "Chọn độ khó"
            subtitle_text = self.subtitle_font.render(subtitle_str, True, (245, 245, 255))
        elif self.show_algorithm_menu:
            subtitle_str = "Chọn thuật toán"
            subtitle_text = self.subtitle_font.render(subtitle_str, True, (245, 245, 255))
            
        if subtitle_text:
            # Đặt tiêu đề phụ ở vị trí thấp hơn, xa tiêu đề chính
            subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 20))
            
            # Thêm hiệu ứng đổ bóng cho tiêu đề phụ
            shadow_subtitle = self.subtitle_font.render(subtitle_str, True, (40, 40, 45))
            shadow_subtitle_rect = shadow_subtitle.get_rect(center=(WIDTH // 2 + 2, HEIGHT // 3 + 22))
            self.screen.blit(shadow_subtitle, shadow_subtitle_rect)
            
            self.screen.blit(subtitle_text, subtitle_rect)
        
        # Điều chỉnh vị trí các nút
        start_y = HEIGHT // 2
        
        # Cập nhật vị trí các nút
        for i, button in enumerate(current_buttons):
            button['rect'].y = start_y + i * (self.button_height + self.button_margin)
    
        # Vẽ nút cho bất kỳ menu nào đang hiển thị
        for button in current_buttons:
            # Kiểm tra trạng thái di chuột
            if button['rect'].collidepoint(mouse_pos):
                color = self.button_colors['hover']
                
                # Hiệu ứng phóng to nút khi hover và thêm gradient
                expanded_rect = button['rect'].inflate(14, 10)
                
                # Tạo hiệu ứng gradient cho nút
                button_surface = pygame.Surface((expanded_rect.width, expanded_rect.height), pygame.SRCALPHA)
                for i in range(expanded_rect.height):
                    alpha = 220
                    # Màu sáng hơn ở giữa tối hơn ở viền
                    brightness = color[0] - 20 + int(40 * (1 - abs(i - expanded_rect.height/2) / (expanded_rect.height/2)))
                    pygame.draw.line(button_surface, (brightness, brightness, brightness+15, alpha), 
                                    (0, i), (expanded_rect.width, i))
                
                # Vẽ gradient
                pygame.draw.rect(button_surface, (0, 0, 0, 0), (0, 0, expanded_rect.width, expanded_rect.height), border_radius=12)
                self.screen.blit(button_surface, expanded_rect)
                
                # Vẽ viền với hiệu ứng ánh sáng
                pygame.draw.rect(self.screen, (220, 220, 240), expanded_rect, 2, border_radius=12)
                pygame.draw.rect(self.screen, (180, 180, 200), expanded_rect.inflate(4, 4), 1, border_radius=13)
                
                # Vẽ chữ với hiệu ứng đổ bóng
                text = self.button_font.render(button['text'], True, self.button_colors['text'])
                text_shadow = self.button_font.render(button['text'], True, (30, 30, 40))
                
                text_rect = text.get_rect(center=expanded_rect.center)
                text_shadow_rect = text_shadow.get_rect(center=(expanded_rect.center[0] + 2, expanded_rect.center[1] + 2))
                
                self.screen.blit(text_shadow, text_shadow_rect)
                self.screen.blit(text, text_rect)
            else:
                color = self.button_colors['normal']
                
                # Tạo bóng đổ cho nút
                shadow_rect = button['rect'].move(4, 4)
                shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                shadow_surf.fill((20, 20, 20, 100))
                pygame.draw.rect(shadow_surf, (0, 0, 0, 0), (0, 0, shadow_rect.width, shadow_rect.height), border_radius=10)
                self.screen.blit(shadow_surf, shadow_rect)
                
                # Tạo hiệu ứng gradient cho nút
                button_surface = pygame.Surface((button['rect'].width, button['rect'].height), pygame.SRCALPHA)
                for i in range(button['rect'].height):
                    alpha = 200
                    # Gradient từ tối lên sáng rồi về tối
                    brightness = color[0] - 15 + int(30 * (1 - abs(i - button['rect'].height/2) / (button['rect'].height/2)))
                    pygame.draw.line(button_surface, (brightness, brightness, brightness+10, alpha), 
                                    (0, i), (button['rect'].width, i))
                
                # Vẽ gradient
                pygame.draw.rect(button_surface, (0, 0, 0, 0), (0, 0, button['rect'].width, button['rect'].height), border_radius=10)
                self.screen.blit(button_surface, button['rect'])
                
                # Vẽ viền
                pygame.draw.rect(self.screen, (120, 120, 130), button['rect'], 2, border_radius=10)
                
                # Vẽ chữ với hiệu ứng đổ bóng nhẹ
                text = self.button_font.render(button['text'], True, self.button_colors['text'])
                text_shadow = self.button_font.render(button['text'], True, (40, 40, 45))
                
                text_rect = text.get_rect(center=button['rect'].center)
                text_shadow_rect = text_shadow.get_rect(center=(button['rect'].center[0] + 1, button['rect'].center[1] + 1))
                
                self.screen.blit(text_shadow, text_shadow_rect)
                self.screen.blit(text, text_rect)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Chuột trái
                    # Xử lý các nút ở menu hiện tại
                    if self.show_algorithm_menu:
                        current_buttons = self.algorithm_buttons
                    elif self.show_difficulty_menu:
                        current_buttons = self.difficulty_buttons
                    else:
                        current_buttons = self.buttons
                        
                    for button in current_buttons:
                        if button['rect'].collidepoint(event.pos):
                            return button['action']
        return None
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            action = self.handle_events()
            
            # Xử lý các hành động từ menu chính
            if not self.show_difficulty_menu and not self.show_algorithm_menu:
                if action == 'pvp':
                    # Sử dụng WindowManager để đóng cửa sổ menu trước khi mở game
                    WindowManager.switch_to_game(self.screen)
                    run_pvp_game()
                    # Kết thúc menu sau khi game đóng - không cần redraw
                    running = False
                    break  # Exit the loop immediately
                elif action == 'ai_menu':
                    # Chuyển sang menu chọn độ khó
                    self.show_difficulty_menu = True
                elif action == 'exit':
                    running = False
                    break  # Exit the loop immediately without trying to draw
            
            # Xử lý các hành động từ menu độ khó
            elif self.show_difficulty_menu and not self.show_algorithm_menu:
                if action == 'difficulty_easy':
                    self.selected_difficulty = 2
                    self.show_difficulty_menu = False
                    self.show_algorithm_menu = True
                elif action == 'difficulty_medium':
                    self.selected_difficulty = 3
                    self.show_difficulty_menu = False
                    self.show_algorithm_menu = True
                elif action == 'difficulty_hard':
                    self.selected_difficulty = 5
                    self.show_difficulty_menu = False
                    self.show_algorithm_menu = True
                elif action == 'back':
                    # Quay lại menu chính
                    self.show_difficulty_menu = False
            
            # Xử lý các hành động từ menu thuật toán
            elif self.show_algorithm_menu:
                if action == 'algorithm_with_pruning':
                    self.selected_algorithm = ALGORITHM_WITH_PRUNING
                    WindowManager.switch_to_game(self.screen)
                    run_ai_game(self.selected_difficulty, self.selected_algorithm)
                    running = False
                    break
                elif action == 'algorithm_without_pruning':
                    self.selected_algorithm = ALGORITHM_WITHOUT_PRUNING
                    WindowManager.switch_to_game(self.screen)
                    run_ai_game(self.selected_difficulty, self.selected_algorithm)
                    running = False
                    break
                elif action == 'back_to_difficulty':
                    # Quay lại menu độ khó
                    self.show_algorithm_menu = False
                    self.show_difficulty_menu = True
            
            if running:
                try:
                    self.draw()
                    pygame.display.flip()
                except pygame.error:
                    running = False
                    break
                    
            clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    menu = Menu()
    menu.run()
