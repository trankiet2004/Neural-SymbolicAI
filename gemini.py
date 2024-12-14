import os
import google.generativeai as genai
from symbolicAI import parse_equation_text, solve_polynomial, solve_sudoku_with_constraints
import json
import re

genai.configure(api_key="AIzaSyBn8T5HqQuQfJlfEQSXW5k6fYjqPnc8ZOM")

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
    # Tạo prompt xử lý cả phương trình và Sudoku
    prompt = f"""
    Dựa trên nội dung sau đây:
    {input_text}
    Nếu đề bài là giải phương trình, hãy trả về kết quả giống sympy với cấu trúc sau:
    coefficients
    rhs
    Lưu ý: Chỉ trả về nội dung các số hoặc ma trận, không thêm bất kì kí hiệu hay thông tin thừa nào cả.
    
    Nếu câu hỏi là sudoku, hãy trả về ma trận sudoku với mảng 2 chiều (dạng Python list of lists).
    
    Lưu ý: Chỉ trả về nội dung file hoặc ma trận, không thêm bất kì kí hiệu hay thông tin thừa nào cả.
    """
    return prompt

def process_sudoku_response(response_text):
    """
    Chuyển đổi kết quả trả về từ mô hình thành mảng 2 chiều Python.
    """
    # Loại bỏ các ký tự không cần thiết (nếu có)
    cleaned_response = response_text.strip()
    # Chuyển đổi thành Python list
    cleaned_response = cleaned_response.replace("_", "0")  # Chuyển ký hiệu '_' thành số 0
    sudoku_array = eval(cleaned_response)  # Chuyển đổi từ chuỗi thành mảng 2 chiều
    return sudoku_array

# Nhận dạng đầu vào

def classify_and_extract(response_text):
    """
    Phân loại response và trích xuất dữ liệu phù hợp (Sudoku hoặc phương trình).
    """
    # Loại bỏ dấu ```python và ``` nếu có
    cleaned_text = re.sub(r"```(?:python)?", "", response_text.strip()).strip()
    
    # Kiểm tra xem có phải mảng 2 chiều (Sudoku) hay không
    if re.match(r"\[\[.*?\]\]", cleaned_text, re.DOTALL):
        try:
            # Là Sudoku, chuyển đổi chuỗi thành mảng 2 chiều
            sudoku_array = eval(cleaned_text)
            if isinstance(sudoku_array, list) and all(isinstance(row, list) for row in sudoku_array):
                return "sudoku", sudoku_array
            else:
                return "error", {"message": "Mảng Sudoku không hợp lệ."}
        except Exception as e:
            return "error", {"message": f"Lỗi khi chuyển đổi Sudoku: {e}"}
    
    # Kiểm tra xem có phải phương trình không
    else:
        return "equation", "none"
    
    # Không phân loại được
    return "unknown", None

# Giải bài toán theo loại

def solve_input(response):
    """
    Trích xuất dữ liệu từ response và phân loại.
    """
    # Trích xuất nội dung từ response
    response_text = response._result.candidates[0].content.parts[0].text
    # Phân loại và xử lý dữ liệu
    input_type, data = classify_and_extract(response_text)
    
    if input_type == "sudoku":
        try:
            solved = solve_sudoku_with_constraints(data)
            if solved:
                return {"solved_sudoku": solved}
            else:
                return {"error": "No solution found for the Sudoku."}
        except Exception as e:
            return {"error": str(e)}
    
    # elif input_type == "equation":
    else:
        try:
            # print(response.text)
            cleaned_text = re.sub(r"```(?:python)?", "", response.text.strip()).strip()
            matches = re.findall(r"\[.*?\]", cleaned_text)
            coefficients = eval(matches[0])
            try:
                rhs = eval(matches[1])
            except:
                rhs = (matches)
            # print("Yeah1", coefficients)
            # print("YEAH2", rhs)
            solutions = solve_polynomial(coefficients, rhs)
            return {"solutions": solutions}
        except Exception as e:
            return {"error": str(e)}    

    # else:
    #     return {"error": "Unsupported input format."}

# Prompt đầu vào từ người dùng

def main():
    print("Nhập bài toán (phương trình bậc 2, bậc 3 hoặc ma trận Sudoku):")
    # Nhận input từ người dùng
    input_data = input()
    prompt = generate_prompt(input_data)
    response = model.generate_content(prompt)

    try:
        # Trích xuất nội dung từ response
        parsed_data = response._result.candidates[0].content.parts[0].text
    except AttributeError as e:
        print(f"Lỗi khi trích xuất response: {e}")
        return

    result = solve_input(response)

    print("Kết quả:")
    print(result)

if __name__ == "__main__":
    main()