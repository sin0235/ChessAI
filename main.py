"""
Điểm Khởi Đầu Trò Chơi Cờ Vua
-----------------------------
Chạy file này để bắt đầu ứng dụng cờ vua với menu lựa chọn chế độ chơi.
Có thể chạy với tham số -p hoặc --performance để thực hiện phân tích hiệu suất.
Sử dụng tham số -s hoặc --specific để chỉ định phân tích hiệu suất trên một vị trí cụ thể.
"""

import os
import sys
import traceback
import argparse


from src.ChessMenu import Menu
from src.PerformanceAnalyzer import run_performance_test

if __name__ == "__main__":
    # Tạo parser để xử lý tham số dòng lệnh
    parser = argparse.ArgumentParser(description='Ứng dụng cờ vua với tùy chọn phân tích hiệu suất.')
    parser.add_argument('-p', '--performance', action='store_true', 
                        help='Chạy phân tích hiệu suất các thuật toán AI')
    parser.add_argument('-s', '--specific', action='store_true',
                        help='Đánh giá hiệu suất dựa trên một vị trí cụ thể thay vì nhiều vị trí')
    
    args = parser.parse_args()
    
    # Nếu có tham số --performance, chạy phân tích hiệu suất0
    if args.performance:
        print("Bắt đầu phân tích hiệu suất các thuật toán AI...")
        
        # Kiểm tra xem có sử dụng vị trí cụ thể hay không
        file_path = run_performance_test(specific_position=args.specific)
        
        if args.specific:
            print("Đã phân tích hiệu suất trên một vị trí cụ thể.")
        else:
            print("Đã phân tích hiệu suất trên nhiều vị trí chuẩn.")
            
        print(f"Kết thúc phân tích. Kết quả đã được lưu vào: {file_path}")
        sys.exit()
    
    # Nếu không, chạy game bình thường
    # Khởi tạo và chạy menu
    menu = Menu()
    menu.run()
    # Thoát game sau khi menu đóng (khi người chơi đã chọn và chơi xong một chế độ)
    sys.exit()
