from constraint import Problem, AllDifferentConstraint
from sympy import symbols, parse_expr, Eq, solve, sympify, roots, solve_poly_system
import re

# Phân tích phương trình từ văn bản
def parse_equation_text(text):
    """
    Phân tích phương trình bậc n từ chuỗi văn bản.
    Trả về hệ số và vế phải.
    """
    match = re.match(r'phương trình bậc (\d+): (.+)', text.lower())
    if not match:
        raise ValueError("Không tìm thấy phương trình hợp lệ trong văn bản.")

    degree = int(match.group(1))
    equation = match.group(2)

    # Tách vế trái và vế phải
    if "=" in equation:
        lhs, rhs = equation.split("=")
    else:
        lhs, rhs = equation, "0"

    # Phân tích biểu thức
    lhs_expr = parse_expr(lhs.strip())
    rhs_expr = parse_expr(rhs.strip())

    # Tìm hệ số từ biểu thức
    x = symbols('x')
    coefficients = [lhs_expr.coeff(x, i) for i in range(degree, -1, -1)]
    return coefficients, rhs_expr

def solve_polynomial(coefficients, rhs):
    """
    Giải phương trình bậc n với hệ số và vế phải.
    """
    # print("Hệ số:", coefficients)
    # print("Vế phải:", rhs)
    
    x = symbols('x')

    # Tạo biểu thức Poly từ hệ số
    degree = len(coefficients) - 1
    poly_expr = sum(c * x**(degree - i) for i, c in enumerate(coefficients))

    # Tạo phương trình bậc n = 0
    equation = Eq(poly_expr, 0)

    # Giải phương trình
    solutions = solve(equation, x)

    return solutions

# Giải Sudoku
def solve_sudoku_with_constraints(grid):
    """
    Giải Sudoku sử dụng python-constraint.
    """
    problem = Problem()

    # Tạo các biến: mỗi ô trên lưới là một biến
    variables = [(row, col) for row in range(9) for col in range(9)]
    problem.addVariables(variables, range(1, 10))  # Miền giá trị là 1 đến 9

    # Thêm ràng buộc: các ô trong hàng phải khác nhau
    for row in range(9):
        problem.addConstraint(AllDifferentConstraint(), [(row, col) for col in range(9)])

    # Thêm ràng buộc: các ô trong cột phải khác nhau
    for col in range(9):
        problem.addConstraint(AllDifferentConstraint(), [(row, col) for row in range(9)])

    # Thêm ràng buộc: các ô trong khối 3x3 phải khác nhau
    for block_row in range(3):
        for block_col in range(3):
            block = [(row, col) for row in range(block_row * 3, (block_row + 1) * 3)
                               for col in range(block_col * 3, (block_col + 1) * 3)]
            problem.addConstraint(AllDifferentConstraint(), block)

    # Thêm các giá trị cố định từ đầu vào
    for row in range(9):
        for col in range(9):
            if grid[row][col] != 0:
                problem.addConstraint(lambda var, val=grid[row][col]: var == val, [(row, col)])

    # Giải bài toán
    solution = problem.getSolution()
    
    if solution:
        solved_grid = [[solution[(row, col)] for col in range(9)] for row in range(9)]
        return solved_grid
    else:
        return None

# Chương trình chính
if __name__ == "__main__":
    # 1. Giải phương trình bậc 2
    print("Giải phương trình bậc 2: x^2 - 5x + 6 = 0")
    coefficients, rhs = parse_equation_text("Phương trình bậc 2: x**2 - 5*x + 6 = 0")
    solutions = solve_polynomial(coefficients, rhs)
    print("Nghiệm:", solutions)

    # 2. Giải Sudoku
    print("\nGiải Sudoku:")
    sudoku_grid = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    print("Sudoku ban đầu:")
    for row in sudoku_grid:
        print(row)

    solved = solve_sudoku_with_constraints(sudoku_grid)
    if solved:
        print("\nSudoku đã giải:")
        for row in solved:
            print(row)
    else:
        print("\nKhông có lời giải cho Sudoku!")