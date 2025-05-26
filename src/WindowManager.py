import pygame

class WindowManager:
    """
    Quản lý các cửa sổ và chuyển đổi giữa chúng
    """
    @staticmethod
    def switch_to_game(current_screen):
        """
        Chuyển từ màn hình menu sang màn hình game
        """
        # Lưu kích thước và vị trí cửa sổ hiện tại
        current_size = current_screen.get_size()
        
        # Đóng cửa sổ hiện tại (menu)
        pygame.display.quit()
        
        # Trả về kích thước để khởi tạo cửa sổ mới
        return current_size
    
    @staticmethod
    def switch_to_menu(current_screen):
        """
        Chuyển từ màn hình game sang màn hình menu
        """
        # Lưu kích thước và vị trí cửa sổ hiện tại
        current_size = current_screen.get_size()
        
        # Đóng cửa sổ hiện tại (game)
        pygame.display.quit()
        
        # Trả về kích thước để khởi tạo cửa sổ mới
        return current_size
