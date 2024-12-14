import re
from sympy import symbols, parse_expr
from constraint import Problem, AllDifferentConstraint
import google.generativeai as genai

genai.configure(api_key="AIzaSyBn8T5HqQuQfJlfEQSXW5k6fYjqPnc8ZOM")

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
)
def generate_prompt(input_text):
    # Prompt yêu cầu định dạng JSON
    question = f"""
    Dựa trên nội dung sau đây:
    {input_text}
    Nếu đề bài là giải phương trình, hãy trả về:
    phuong trinh bac ... : ...
    
    Nếu câu hỏi là sudoku, hãy trả về ma trận sudoku.
    
    Lưu ý: Chỉ trả về nội dung file hoặc ma trận, không thêm bất kì kí hiệu hay thông tin thừa nào cả(kể cả ```json).
    """
    prompt  = generate_prompt(question)
    response = model.generate_content(prompt)
    return prompt


# Hàm phân tích phương trình
def parse_equation_text(text):
    """
    Phân tích phương trình bậc n từ chuỗi văn bản.
    Trả về hệ số và vế phải.
    """
    match = re.match(r'(\d+): (.+)', text.lower())
    if not match:
        raise ValueError("Không tìm thấy phương trình hợp lệ trong văn bản.")

    degree = int(match.group(1))
    equation = match.group(2)

    # Thay thế dấu mũ ^ thành **
    equation = equation.replace("^", "**")

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

# Hàm giải phương trình bậc n
def solve_polynomial(coefficients, rhs):
    """
    Giải phương trình bậc n với hệ số và vế phải.
    """
    problem = Problem()
    problem.addVariable("x", range(-1000, 1001))  # Miền giá trị giả định

    # Thêm ràng buộc
    def polynomial_constraint(x):
        return sum(c * x**i for i, c in enumerate(reversed(coefficients))) == rhs

    problem.addConstraint(polynomial_constraint, ["x"])
    solutions = problem.getSolutions()
    return [s["x"] for s in solutions]

# Hàm giải Sudoku
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
    print("Nhập bài toán của bạn (Phương trình hoặc Sudoku):")
    user_input = input().strip()

    try:
        # Chuyển văn bản tự nhiên thành logic với GPT
        logic_input = generate_prompt(user_input)

        # Nếu là phương trình
        if "phương trình bậc" in logic_input.lower():
            coefficients, rhs = parse_equation_text(logic_input)
            solutions = solve_polynomial(coefficients, rhs)
            print("Nghiệm của phương trình là:", solutions)

        # Nếu là Sudoku
        elif "sudoku" in logic_input.lower():
            print("Nhập các hàng của lưới Sudoku (các số cách nhau bởi dấu cách, 0 là ô trống):")
            sudoku_grid = []
            for _ in range(9):
                row = input().strip().split()
                sudoku_grid.append([int(num) for num in row])

            print("\nSudoku ban đầu:")
            for row in sudoku_grid:
                print(row)

            solved = solve_sudoku_with_constraints(sudoku_grid)
            if solved:
                print("\nSudoku đã giải:")
                for row in solved:
                    print(row)
            else:
                print("\nKhông có lời giải cho Sudoku!")
        else:
            print("Không thể nhận diện bài toán.")
    except Exception as e:
        print("Lỗi:", e)
