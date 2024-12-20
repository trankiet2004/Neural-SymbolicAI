def is_valid_sudoku(board):
    """
    Kiểm tra xem một bảng Sudoku có hợp lệ hay không.

    :param board: List[List[int]] - Bảng Sudoku 9x9 (danh sách lồng nhau).
    :return: bool - True nếu bảng hợp lệ, False nếu không hợp lệ.
    """
    # Kiểm tra kích thước của bảng
    if len(board) != 9 or any(len(row) != 9 for row in board):
        return False

    # Hàm kiểm tra một danh sách có chứa các số từ 1 đến 9 mà không bị lặp
    def is_valid_group(group):
        nums = [num for num in group if num != 0]  # Bỏ qua số 0 (ô trống)
        return len(nums) == len(set(nums)) and all(1 <= num <= 9 for num in nums)

    # Kiểm tra từng hàng
    for row in board:
        if not is_valid_group(row):
            return False

    # Kiểm tra từng cột
    for col in range(9):
        if not is_valid_group([board[row][col] for row in range(9)]):
            return False

    # Kiểm tra từng ô vuông 3x3
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            box = [
                board[row][col]
                for row in range(box_row, box_row + 3)
                for col in range(box_col, box_col + 3)
            ]
            if not is_valid_group(box):
                return False

    return True

# Ví dụ sử dụng
sudoku_board = [[5, 3, 4, 6, 7, 8, 9, 1, 2], [6, 7, 2, 1, 9, 5, 3, 4, 8], [1, 9, 8, 3, 4, 2, 5, 6, 7], [8, 5, 9, 7, 6, 1, 4, 2, 3], [4, 2, 6, 8, 5, 3, 7, 9, 1], [7, 1, 3, 9, 2, 4, 8, 5, 6], [9, 6, 1, 5, 3, 7, 2, 8, 4], [2, 8, 7, 4, 1, 9, 6, 3, 5], [3, 4, 5, 2, 8, 6, 1, 7, 9]]

print(is_valid_sudoku(sudoku_board))  # Kết quả: True (nếu bảng hợp lệ)
