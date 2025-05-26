"""
Module đo lường hiệu suất các thuật toán AI cờ vua.
"""
import time
import psutil
import os
import pandas as pd
import matplotlib.pyplot as plt
from multiprocessing import Queue
import uuid
import datetime

from src.ChessEngine import GameState, Move
import src.ChessAI as ChessAI

class PerformanceAnalyzer:
    """
    Phân tích hiệu suất của các thuật toán AI cờ vua.
    Đo lường thời gian thực thi và bộ nhớ sử dụng, sau đó xuất kết quả ra file Excel.
    """
    
    def __init__(self, output_folder="exports"):
        """
        Khởi tạo PerformanceAnalyzer
        
        Tham số:
        - output_folder: Thư mục lưu các file kết quả
        """
        self.output_folder = output_folder
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        self.results = []
        self.process = psutil.Process(os.getpid())
    
    def measure_specific_position(self, game_state, algorithm, position_description="Vị trí cơ bản", depth_levels=[1, 2, 3, 4], repetitions=3):
        """
        Đo lường hiệu suất của một thuật toán AI với một vị trí cụ thể
        
        Tham số:
        - game_state: Trạng thái cụ thể của trò chơi cần đánh giá
        - algorithm: Thuật toán cần đo lường ('with_pruning' hoặc 'without_pruning')
        - position_description: Mô tả vị trí đang được đánh giá
        - depth_levels: Danh sách các độ sâu cần đo lường
        - repetitions: Số lần lặp lại mỗi phép đo để lấy kết quả trung bình
        
        Trả về:
        - Kết quả đo lường cho vị trí cụ thể
        """
        print(f"Đo lường thuật toán {algorithm} trên vị trí: {position_description}")
        
        # Lấy các nước đi hợp lệ từ vị trí hiện tại
        valid_moves = game_state.getValidMoves()
        if not valid_moves:
            print(f"Không có nước đi hợp lệ cho vị trí này!")
            return
        
        # Ghi lại trạng thái ban đầu để đảm bảo mỗi lần kiểm tra đều bắt đầu từ cùng một vị trí
        board_state = []
        for row in game_state.board:
            board_state.append(row.copy())
        castle_rights = game_state.current_castling_rights.copy()
        en_passant_possible = game_state.enpassant_possible
        white_to_move = game_state.white_to_move
        
        for depth in depth_levels:
            print(f"  Độ sâu: {depth}")
            
            for rep in range(repetitions):
                print(f"    Lần lặp: {rep+1}/{repetitions}")
                
                # Khôi phục lại trạng thái ban đầu trước mỗi lần kiểm tra
                game_state.board = []
                for row in board_state:
                    game_state.board.append(row.copy())
                game_state.current_castling_rights = castle_rights.copy()
                game_state.enpassant_possible = en_passant_possible
                game_state.white_to_move = white_to_move
                
                # Đảm bảo cập nhật các trạng thái khác nếu cần
                game_state.updateCastleRights()
                
                # Đo lường bộ nhớ sử dụng trước khi thực thi
                memory_before = self.process.memory_info().rss / 1024 / 1024  # Chuyển đổi sang MB
                
                # Tạo queue để nhận kết quả
                return_queue = Queue()
                
                # Đo lường thời gian thực thi
                start_time = time.time()
                
                # Thực thi thuật toán
                ChessAI.findBestMove(game_state, valid_moves, return_queue, depth=depth, algorithm=algorithm)
                
                # Lấy nước đi tốt nhất từ queue
                best_move = return_queue.get()
                
                # Tính thời gian thực thi
                execution_time = time.time() - start_time
                
                # Đo lường bộ nhớ sử dụng sau khi thực thi
                memory_after = self.process.memory_info().rss / 1024 / 1024  # Chuyển đổi sang MB
                memory_used = memory_after - memory_before
                
                # Lưu kết quả
                self.results.append({
                    'Vị trí': position_description,
                    'Thuật toán': algorithm,
                    'Độ sâu': depth,
                    'Lần lặp': rep + 1,
                    'Thời gian (giây)': execution_time,
                    'Bộ nhớ (MB)': memory_used,
                    'Nước đi tốt nhất': best_move.getChessNotation() if best_move else "None"
                })
    
    def create_test_positions(self):
        """
        Tạo các vị trí kiểm tra tiêu chuẩn để đánh giá thuật toán
        
        Trả về:
        - Danh sách các cặp (trạng thái, mô tả) để kiểm tra
        """
        test_positions = []
        
        # Vị trí 1: Vị trí bắt đầu cơ bản
        start_position = GameState()
        test_positions.append((start_position, "Vị trí ban đầu"))
        
        # Vị trí 2: Sau khi đã đi vài nước mở đầu (ví dụ: e4, e5, Nf3)
        mid_opening = GameState()
        # Thực hiện các nước đi mở đầu
        mid_opening.makeMove(Move((6, 4), (4, 4), mid_opening.board))  # e4
        mid_opening.makeMove(Move((1, 4), (3, 4), mid_opening.board))  # e5
        mid_opening.makeMove(Move((7, 6), (5, 5), mid_opening.board))  # Nf3
        test_positions.append((mid_opening, "Mở đầu cơ bản (e4, e5, Nf3)"))
        
        # Vị trí 3: Tình huống trung cuộc phức tạp
        # Ví dụ tạo một vị trí trung cuộc với nhiều quân (có thể tùy chỉnh)
        mid_game = GameState()
        # Đặt bàn cờ vào một vị trí trung cuộc đặc biệt
        mid_game.board = [
            ["bR", "bN", "bB", "--", "bK", "bB", "--", "bR"],
            ["bp", "bp", "bp", "--", "--", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "bp", "--", "--", "--"],
            ["--", "--", "bQ", "bp", "wN", "--", "--", "--"],
            ["--", "wB", "--", "wp", "--", "--", "--", "--"],
            ["--", "--", "wN", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "--", "wp", "wp", "wp", "wp"],
            ["wR", "--", "wB", "wQ", "wK", "--", "--", "wR"]
        ]
        mid_game.white_to_move = True
        mid_game.updateCastleRights()
        test_positions.append((mid_game, "Tình huống trung cuộc phức tạp"))
        
        # Vị trí 4: Tình huống cuối game với ít quân
        end_game = GameState()
        # Đặt bàn cờ vào một vị trí cuối game với ít quân
        end_game.board = [
            ["--", "--", "--", "--", "bK", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "bp", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "wR", "--", "--", "--", "--", "--"],
            ["wp", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "wK", "--", "--", "--"]
        ]
        end_game.white_to_move = True
        end_game.updateCastleRights()
        test_positions.append((end_game, "Tình huống cuối game"))
        
        return test_positions
    
    def compare_algorithms_specific_position(self, position, position_description, algorithms=None, depth_levels=None, repetitions=3):
        """
        So sánh hiệu suất của nhiều thuật toán AI trên một vị trí cụ thể
        
        Tham số:
        - position: Trạng thái cụ thể của trò chơi cần đánh giá
        - position_description: Mô tả vị trí đang được đánh giá
        - algorithms: Danh sách các thuật toán cần so sánh
        - depth_levels: Danh sách các độ sâu cần đo lường
        - repetitions: Số lần lặp lại mỗi phép đo để lấy kết quả trung bình
        """
        if algorithms is None:
            algorithms = [ChessAI.ALGORITHM_WITH_PRUNING, ChessAI.ALGORITHM_WITHOUT_PRUNING]
        
        if depth_levels is None:
            depth_levels = [1, 2, 3]
        
        # Đo lường hiệu suất của từng thuật toán trên vị trí cụ thể
        for algorithm in algorithms:
            self.measure_specific_position(
                position, 
                algorithm, 
                position_description, 
                depth_levels, 
                repetitions
            )
    
    def compare_algorithms_all_positions(self, algorithms=None, depth_levels=None, repetitions=3):
        """
        So sánh hiệu suất của nhiều thuật toán AI trên nhiều vị trí chuẩn
        
        Tham số:
        - algorithms: Danh sách các thuật toán cần so sánh
        - depth_levels: Danh sách các độ sâu cần đo lường
        - repetitions: Số lần lặp lại mỗi phép đo để lấy kết quả trung bình
        """
        # Tạo các vị trí kiểm tra
        test_positions = self.create_test_positions()
        
        # So sánh thuật toán trên từng vị trí
        for position, description in test_positions:
            self.compare_algorithms_specific_position(
                position, 
                description, 
                algorithms, 
                depth_levels, 
                repetitions
            )
    
    def export_to_excel(self, filename=None):
        """
        Xuất kết quả đo lường ra file Excel
        
        Tham số:
        - filename: Tên file Excel. Nếu không chỉ định, một tên file ngẫu nhiên sẽ được tạo.
        
        Trả về:
        - Đường dẫn đến file Excel đã tạo
        """
        if not self.results:
            print("Không có dữ liệu để xuất ra Excel.")
            return None
        
        # Tạo DataFrame từ kết quả
        df = pd.DataFrame(self.results)
        
        # Tạo tên file nếu không được chỉ định
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chess_performance_{timestamp}.xlsx"
        
        # Thêm đường dẫn thư mục
        file_path = os.path.join(self.output_folder, filename)
        
        # Tạo một ExcelWriter
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            # Xuất dữ liệu chi tiết
            df.to_excel(writer, sheet_name='Chi tiết', index=False)
            
            # Tạo pivot table cho thời gian thực thi trung bình theo thuật toán, vị trí và độ sâu
            pivot_time = df.pivot_table(
                values='Thời gian (giây)', 
                index=['Vị trí', 'Thuật toán'],
                columns='Độ sâu', 
                aggfunc='mean'
            )
            pivot_time.to_excel(writer, sheet_name='Thời gian TB (giây)')
            
            # Tạo pivot table cho bộ nhớ sử dụng trung bình
            pivot_memory = df.pivot_table(
                values='Bộ nhớ (MB)', 
                index=['Vị trí', 'Thuật toán'],
                columns='Độ sâu', 
                aggfunc='mean'
            )
            pivot_memory.to_excel(writer, sheet_name='Bộ nhớ TB (MB)')
            
            # Xuất kết quả nước đi theo vị trí và thuật toán
            pivot_moves = df.pivot_table(
                values='Nước đi tốt nhất',
                index=['Vị trí', 'Thuật toán'],
                columns='Độ sâu',
                aggfunc=lambda x: pd.Series.mode(x).iloc[0] if len(pd.Series.mode(x)) > 0 else None
            )
            pivot_moves.to_excel(writer, sheet_name='Nước đi tốt nhất')
            
            # Tạo biểu đồ cho từng vị trí
            positions = df['Vị trí'].unique()
            for position in positions:
                # Lọc dữ liệu cho vị trí hiện tại
                df_position = df[df['Vị trí'] == position]
                
                # Pivot cho thời gian
                pivot_time_pos = df_position.pivot_table(
                    values='Thời gian (giây)', 
                    index='Thuật toán',
                    columns='Độ sâu', 
                    aggfunc='mean'
                )
                
                # Tạo sheet cho biểu đồ thời gian
                pos_chart_name = f"{position[:15]} - Thời gian"
                time_chart_sheet = workbook.add_worksheet(pos_chart_name)
                
                # Xuất dữ liệu pivot cho biểu đồ
                pivot_sheet_name = f"_temp_{position[:10]}_time"
                pivot_time_pos.to_excel(writer, sheet_name=pivot_sheet_name)
                
                # Tạo biểu đồ
                chart_time = workbook.add_chart({'type': 'line'})
                
                # Thêm dữ liệu cho mỗi thuật toán
                for i, algorithm in enumerate(pivot_time_pos.index):
                    chart_time.add_series({
                        'name': algorithm,
                        'categories': [pivot_sheet_name, 0, 1, 0, len(pivot_time_pos.columns)],
                        'values': [pivot_sheet_name, i+1, 1, i+1, len(pivot_time_pos.columns)],
                        'marker': {'type': 'circle', 'size': 8},
                    })
                
                # Cấu hình biểu đồ
                chart_time.set_title({'name': f'Thời gian thực thi - {position}'})
                chart_time.set_x_axis({'name': 'Độ sâu'})
                chart_time.set_y_axis({'name': 'Thời gian (giây)'})
                chart_time.set_style(10)
                time_chart_sheet.insert_chart('B2', chart_time, {'x_scale': 1.5, 'y_scale': 1.5})
                
                # Thêm tạm thời vào danh sách sheets để xóa sau
                workbook._add_sheet_name(pivot_sheet_name)
            
            # Tạo biểu đồ so sánh tổng hợp cho các thuật toán
            workbook = writer.book
            
            # Biểu đồ so sánh thời gian giữa các thuật toán
            summary_time_sheet = workbook.add_worksheet('Biểu đồ so sánh thời gian')
            
            # Tạo pivot table cho biểu đồ tổng hợp
            pivot_time_summary = df.pivot_table(
                values='Thời gian (giây)',
                index='Thuật toán',
                columns=['Vị trí', 'Độ sâu'],
                aggfunc='mean'
            )
            
            # Xuất dữ liệu pivot
            pivot_time_summary.to_excel(writer, sheet_name='_temp_summary_time')
            chart_summary = workbook.add_chart({'type': 'column'})
            
            # Thêm dữ liệu cho mỗi thuật toán và độ sâu cụ thể (chọn độ sâu cao nhất)
            max_depth = max(depth_levels)
            for i, algorithm in enumerate(pivot_time_summary.index):
                chart_summary.add_series({
                    'name': f"{algorithm} (độ sâu {max_depth})",
                    'categories': ['_temp_summary_time', 0, 1, 0, len(positions)],
                    'values': ['_temp_summary_time', i+1, len(positions)*(max_depth-1)+1, i+1, len(positions)*max_depth],
                })
            
            # Cấu hình biểu đồ
            chart_summary.set_title({'name': f'So sánh thời gian giữa các thuật toán (Độ sâu {max_depth})'})
            chart_summary.set_x_axis({'name': 'Vị trí'})
            chart_summary.set_y_axis({'name': 'Thời gian (giây)'})
            chart_summary.set_style(10)
            summary_time_sheet.insert_chart('B2', chart_summary, {'x_scale': 2, 'y_scale': 1.5})
            
            # Thêm tạm thời vào danh sách sheets để xóa sau
            workbook._add_sheet_name('_temp_summary_time')
        
        print(f"Đã xuất kết quả ra file: {file_path}")
        return file_path
    
    def generate_report(self, specific_position=None, position_description=None, algorithms=None, depth_levels=None, repetitions=3, filename=None):
        """
        Tạo báo cáo đầy đủ, bao gồm đo lường hiệu suất và xuất kết quả ra file Excel
        
        Tham số:
        - specific_position: Trạng thái của trò chơi cụ thể. Nếu None, sẽ sử dụng các vị trí mặc định.
        - position_description: Mô tả vị trí, chỉ dùng khi specific_position được chỉ định.
        - algorithms: Danh sách các thuật toán cần so sánh
        - depth_levels: Danh sách các độ sâu cần đo lường
        - repetitions: Số lần lặp lại mỗi phép đo để lấy kết quả trung bình
        - filename: Tên file Excel. Nếu không chỉ định, một tên file ngẫu nhiên sẽ được tạo.
        
        Trả về:
        - Đường dẫn đến file Excel đã tạo
        """
        if specific_position is not None and position_description is not None:
            # Nếu vị trí cụ thể được chỉ định, chỉ đánh giá vị trí đó
            self.compare_algorithms_specific_position(
                specific_position, 
                position_description, 
                algorithms, 
                depth_levels, 
                repetitions
            )
        else:
            # Nếu không, đánh giá tất cả các vị trí chuẩn
            self.compare_algorithms_all_positions(algorithms, depth_levels, repetitions)
        
        # Xuất kết quả ra file Excel
        return self.export_to_excel(filename)


def run_performance_test(specific_position=False):
    """
    Hàm chạy kiểm tra hiệu suất các thuật toán AI cờ vua
    
    Tham số:
    - specific_position: True nếu muốn kiểm tra trên một vị trí cụ thể, False nếu muốn kiểm tra trên các vị trí mặc định
    """
    # Tạo đối tượng PerformanceAnalyzer
    analyzer = PerformanceAnalyzer()
    
    # Cấu hình kiểm tra
    algorithms = [ChessAI.ALGORITHM_WITH_PRUNING, ChessAI.ALGORITHM_WITHOUT_PRUNING]
    depth_levels = [1, 2, 3, 4]  # Cẩn thận với độ sâu > 4, có thể mất nhiều thời gian
    repetitions = 3
    
    if specific_position:
        # Tạo một vị trí cụ thể để kiểm tra
        # Ví dụ: Tình huống cuối game đơn giản
        game_state = GameState()
        # Đặt bàn cờ vào một vị trí cụ thể
        game_state.board = [
            ["--", "--", "--", "--", "bK", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "wK", "wQ", "--", "--"]
        ]
        game_state.white_to_move = True
        game_state.updateCastleRights()
        
        # Chạy kiểm tra và tạo báo cáo cho vị trí cụ thể
        file_path = analyzer.generate_report(
            specific_position=game_state,
            position_description="Vị trí cuối game chiếu hậu",
            algorithms=algorithms,
            depth_levels=depth_levels,
            repetitions=repetitions
        )
    else:
        # Chạy kiểm tra và tạo báo cáo cho tất cả các vị trí chuẩn
        file_path = analyzer.generate_report(
            algorithms=algorithms,
            depth_levels=depth_levels,
            repetitions=repetitions
        )
    
    print(f"Đã tạo báo cáo hiệu suất tại: {file_path}")
    return file_path


if __name__ == "__main__":
    run_performance_test(specific_position=True) 