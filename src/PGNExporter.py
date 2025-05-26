"""
Module để xuất bản ghi ván cờ theo chuẩn PGN (Portable Game Notation)
PGN là định dạng chuẩn quốc tế để ghi lại và chia sẻ các ván cờ
"""
import datetime
import os
import copy

class PGNExporter:
    def __init__(self, game_state):
        """
        Khởi tạo exporter với trạng thái game hiện tại
        
        :param game_state: Đối tượng GameState chứa thông tin ván cờ
        """
        self.game_state = game_state
        
    def generate_pgn_string(self, white_name="White", black_name="Black", event="Chess Game", site="Local Game", result="*"):
        """
        Tạo chuỗi PGN từ lịch sử nước đi
        
        :param white_name: Tên người chơi quân trắng
        :param black_name: Tên người chơi quân đen
        :param event: Tên sự kiện
        :param site: Địa điểm
        :param result: Kết quả ("1-0" trắng thắng, "0-1" đen thắng, "1/2-1/2" hòa, "*" chưa kết thúc)
        :return: Chuỗi PGN hoàn chỉnh với định dạng nhiều dòng để dễ đọc
        """
        # Tạo phần header PGN
        current_date = datetime.datetime.now().strftime("%Y.%m.%d")
        pgn_header = [
            f'[Event "{event}"]',
            f'[Site "{site}"]',
            f'[Date "{current_date}"]',
            f'[Round "1"]',
            f'[White "{white_name}"]',
            f'[Black "{black_name}"]',
            f'[Result "{result}"]',
        ]
        
        # Tạo phần nội dung PGN từ lịch sử nước đi, mỗi lượt đi trên một dòng
        move_lines = []
        current_move_pair = ""
        
        for i, move in enumerate(self.game_state.move_log):
            # Kiểm tra nếu là nước đi của trắng (số chẵn) hoặc đen (số lẻ)
            if i % 2 == 0:  # Nước đi của trắng
                move_number = i // 2 + 1
                algebraic_notation = self._get_standard_algebraic_notation(move, i)
                current_move_pair = f"{move_number}. {algebraic_notation}"
            else:  # Nước đi của đen
                algebraic_notation = self._get_standard_algebraic_notation(move, i)
                current_move_pair += f" {algebraic_notation}"
                move_lines.append(current_move_pair)
                current_move_pair = ""
        
        # Thêm nước đi cuối cùng nếu là nước đi của trắng
        if current_move_pair:
            move_lines.append(current_move_pair)
        
        # Thêm kết quả vào cuối nếu có
        if result != "*":
            if move_lines:
                move_lines[-1] += f" {result}"
            else:
                move_lines.append(result)
        
        # Ghép tất cả thành chuỗi PGN hoàn chỉnh
        pgn_content = "\n".join(move_lines)
        pgn_string = "\n".join(pgn_header) + "\n\n" + pgn_content
        
        return pgn_string
    
    def _check_move_results(self, move):
        """
        Kiểm tra kết quả của một nước đi mà không thay đổi trạng thái game hiện tại
        
        :param move: Đối tượng Move cần kiểm tra
        :return: (is_check, is_checkmate) - Hai giá trị boolean chỉ ra trạng thái chiếu và chiếu bí
        """
        try:
            # Tạo bản sao của trạng thái bàn cờ để không ảnh hưởng đến game gốc
            game_state_copy = copy.deepcopy(self.game_state)
            
            # Xác định màu của người đi và đối thủ trước khi thực hiện nước đi
            moved_piece_color = move.piece_moved[0]  # 'w' hoặc 'b'
            opponent_color = 'b' if moved_piece_color == 'w' else 'w'
            
            # Lưu trạng thái ban đầu
            original_white_to_move = game_state_copy.white_to_move
            
            # Thực hiện nước đi trên bản sao
            game_state_copy.makeMove(move)
            
            # Sau khi thực hiện nước đi, đến lượt đối thủ
            # Kiểm tra xem vua của đối thủ có đang bị chiếu không
            king_position = game_state_copy.black_king_location if opponent_color == 'b' else game_state_copy.white_king_location
            is_check = game_state_copy.squareUnderAttack(king_position[0], king_position[1])
            
            # Kiểm tra xem đối thủ có còn nước đi hợp lệ không (đã ở lượt đối thủ sau makeMove)
            valid_moves = game_state_copy.getValidMoves()
            is_checkmate = is_check and len(valid_moves) == 0
            
            # Thêm thông tin debug chi tiết
            move_str = f"{move.piece_moved}({move.start_row},{move.start_col})->({move.end_row},{move.end_col})"
            print(f"Debug - Move: {move_str} | Check: {is_check} | Checkmate: {is_checkmate}")
            print(f"         King at: {king_position} | Valid moves left: {len(valid_moves)}")
            
            # Giải phóng bộ nhớ
            del game_state_copy
            
            return is_check, is_checkmate
            
        except Exception as e:
            print(f"Error in _check_move_results: {e}")
            return False, False
    
    def _get_standard_algebraic_notation(self, move, move_index):
        """
        Tạo ký hiệu đại số chuẩn (SAN) cho nước đi với các quy tắc phân biệt đúng
        
        :param move: Đối tượng Move
        :param move_index: Chỉ số của nước đi trong lịch sử
        :return: Chuỗi ký hiệu đại số chuẩn
        """
        # Xử lý nhập thành
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # nhập thành ngắn
                notation = "O-O"
            else:  # nhập thành dài
                notation = "O-O-O"
            
            # Sử dụng trực tiếp thuộc tính chiếu/chiếu hết
            if move.is_checkmate:
                notation += "#"
            elif move.is_check:
                notation += "+"
                
            return notation
        
        # Xử lý các nước đi thông thường
        piece = move.piece_moved[1]
        capture = "x" if move.is_capture else ""
        destination = move.getRankFile(move.end_row, move.end_col)
        
        # Quân tốt không hiển thị ký hiệu, chỉ hiển thị cột gốc khi bắt quân
        if piece == "p":
            if capture:
                origin = move.cols_to_files[move.start_col]
                notation = f"{origin}{capture}{destination}"
            else:
                notation = destination
                
            # Xử lý thăng cấp
            if move.is_pawn_promotion:
                notation += f"={move.promotion_choice}"
        else:
            # Xử lý phân biệt nước đi khi nhiều quân cùng loại có thể đi đến ô đích
            disambiguate = self._get_disambiguation(move, piece)
            notation = f"{piece}{disambiguate}{capture}{destination}"
        
        # Thêm ký hiệu chiếu tướng và chiếu bí sử dụng trực tiếp thuộc tính
        if move.is_checkmate:
            notation += "#"
        elif move.is_check:
            notation += "+"
            
        # Xử lý bắt tốt qua đường
        if move.is_enpassant_move:
            notation += " e.p."
            
        return notation
    
    def _get_disambiguation(self, move, piece):
        """
        Xử lý phân biệt nước đi khi nhiều quân cùng loại có thể đi đến ô đích
        
        :param move: Đối tượng Move
        :param piece: Loại quân cờ
        :return: Chuỗi ký tự phân biệt (file, rank hoặc cả hai)
        """
        disambiguate = ""
        file_disambiguation = False
        rank_disambiguation = False
        
        # Tạo bản sao trạng thái để kiểm tra các nước đi hợp lệ
        game_state_copy = copy.deepcopy(self.game_state)
        
        # Tìm tất cả các quân cùng loại có thể đi đến ô đích
        for r in range(8):
            for c in range(8):
                # Bỏ qua nếu không phải quân cùng loại hoặc chính là quân đang di chuyển
                current_piece = self.game_state.board[r][c]
                if current_piece[0] != move.piece_moved[0] or current_piece[1] != piece:
                    continue
                if r == move.start_row and c == move.start_col:
                    continue
                
                # Kiểm tra xem quân này có thể đi đến ô đích không
                possible_moves = []
                if piece == "p":
                    possible_moves = self.game_state.getPawnMoves(r, c, possible_moves) or []
                elif piece == "R":
                    possible_moves = self.game_state.getRookMoves(r, c, possible_moves) or []
                elif piece == "N":
                    possible_moves = self.game_state.getKnightMoves(r, c, possible_moves) or []
                elif piece == "B":
                    possible_moves = self.game_state.getBishopMoves(r, c, possible_moves) or []
                elif piece == "Q":
                    possible_moves = self.game_state.getQueenMoves(r, c, possible_moves) or []
                elif piece == "K":
                    possible_moves = self.game_state.getKingMoves(r, c, possible_moves) or []
                
                # Kiểm tra xem có nước đi nào đến ô đích không
                for possible_move in possible_moves:
                    if possible_move.end_row == move.end_row and possible_move.end_col == move.end_col:
                        # Đảm bảo đây là nước đi hợp lệ (không để vua trong tình trạng chiếu)
                        valid_move = True
                        # Nếu cần, thêm kiểm tra để xác nhận tính hợp lệ của nước đi
                        
                        if valid_move:
                            # Cần phân biệt
                            if move.start_col != c:
                                file_disambiguation = True
                            if move.start_row != r:
                                rank_disambiguation = True
        
        # Quy tắc phân biệt: ưu tiên file (cột), nếu không đủ thì thêm rank (hàng)
        if file_disambiguation:
            disambiguate += move.cols_to_files[move.start_col]
        if rank_disambiguation and (not file_disambiguation or move.piece_moved[1] == "R"):
            disambiguate += move.rows_to_ranks[move.start_row]
            
        return disambiguate
    
    def export_to_file(self, filename=None, white_name="White", black_name="Black", event="Chess Game", site="Local Game", result="*"):
        """
        Xuất ván cờ ra file PGN
        
        :param filename: Tên file (nếu None, sẽ tạo tên file dựa trên ngày giờ)
        :param white_name: Tên người chơi quân trắng
        :param black_name: Tên người chơi quân đen
        :param event: Tên sự kiện
        :param site: Địa điểm
        :param result: Kết quả
        :return: Đường dẫn đến file đã lưu
        """
        # Tạo thư mục exports nếu chưa tồn tại
        exports_dir = os.path.join(os.getcwd(), "exports")
        if not os.path.exists(exports_dir):
            os.makedirs(exports_dir)
        
        # Tạo tên file mặc định nếu không có
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chess_game_{timestamp}.pgn"
        
        # Đảm bảo file có đuôi .pgn
        if not filename.endswith(".pgn"):
            filename += ".pgn"
        
        # Đường dẫn đầy đủ đến file
        file_path = os.path.join(exports_dir, filename)
        
        # Tạo chuỗi PGN
        pgn_string = self.generate_pgn_string(white_name, black_name, event, site, result)
        
        # Ghi ra file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(pgn_string)
        
        print(f"PGN file exported to: {file_path}")
        
        # Mở file để kiểm tra nội dung
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"PGN file content:\n{content}")
        
        return file_path
