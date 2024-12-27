import re
import os
import csv
import json
import pandas as pd
from tqdm import tqdm
from sympy import sympify
import google.generativeai as genai
from symbolicAI import parse_equation_text, solve_polynomial, solve_sudoku_with_constraints

API_KEY = "........"
genai.configure(api_key=API_KEY)
 
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
    
    Nếu câu hỏi là sudoku, hãy trả về ma trận sudoku với mảng 2 chiều (dạng Python list of lists). KHÔNG ĐƯỢC GIẢI SUDOKU. Hãy chỉ trả về ma trận đầu vào.
    Ngược lại, nếu là phương trình thì phải trả về list coefficients là list có chứa các hệ số của vế trái và giá trị rhs là giá trị bên phải dấu bằng của phương trình
    
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
            # print(response.text.strip())
            cleaned_text = response_text.replace("```python", "").replace("```", "").strip()            
            lines = cleaned_text.split('\n')
            coefficients = eval(lines[0].strip())
            rhs = int(lines[1].strip())
            # print("Yeah1", coefficients)
            # print("YEAH2", rhs)
            solutions = solve_polynomial(coefficients, rhs)
            return {"solutions": solutions}
        except Exception as e:
            return {"error": str(e)}

    # else:
    #     return {"error": "Unsupported input format."}

# Prompt đầu vào từ người dùng

def main(input_data):
    # Nhận input từ người dùng    
    prompt = generate_prompt(input_data)        

    try:
        # Trích xuất nội dung từ response
        response = model.generate_content(prompt)
        parsed_data = response._result.candidates[0].content.parts[0].text
    except AttributeError as e:
        print(f"Lỗi khi trích xuất response: {e}")
        return
    
    result = solve_input(response)

    return result

def stringToMatrix(input):
    id = 0
    sudoku = []    
    for i in range(9):
        r = []
        for j in range(9):
            r.append(int(input[id]))
            id += 1
        
        sudoku.append(r)
    
    return str(sudoku)

def test_sudoku():
    chunk_size = 100
    chunks = []    
    def count_lines_in_file(filename):
        with open(filename, 'r') as file:
            return sum(1 for line in file)
    
    lines = count_lines_in_file('sudoku.csv')
    with tqdm(total=min(100, lines - 1), desc="Reading file") as pbar:
        for chunk in pd.read_csv('sudoku.csv', chunksize=chunk_size):
            chunks.append(chunk)
            pbar.update(chunk.shape[0])
            break  # Dừng lại sau khi đọc 1 chunk

    df = pd.concat(chunks, ignore_index=True)

    print(f"File được đọc thành công! Tổng số dòng: {len(df)}")

    ok, test = 0, len(df)
    for t in tqdm(range(min(len(df), test)), desc=f"Test Sudoku từ testcase 0 đến testcase {len(df)}"):
        try: 
            # input_data = input()
            input_data = "\nGiải sudoku " + stringToMatrix(df['puzzle'][t])
            res = main(input_data)
            tempRes = ""
            
            for i in res['solved_sudoku']:
                for j in i:
                    tempRes += str(j)
            
            ok += (tempRes == df['solution'][t])
        except:
            ok += 0

    print(f"Tỉ lệ chính xác khi chạy test từ 0 đến {test} là: {ok / test}")
    print(f"Số lượng test: {test}")

    if lines <= 11:
        return 
    
    j = 10
    while j <= lines:
        ok = 0
        for t in tqdm(range(j - 10, j), desc=f"Test Sudoku từ testcase {j - 10} đến testcase {j - 1}"):
            try: 
                # input_data = input()
                input_data = "\nGiải sudoku " + stringToMatrix(df['puzzle'][t])
                res = main(input_data)
                tempRes = ""
                
                for i in res['solved_sudoku']:
                    for jj in i:
                        tempRes += str(jj)
                
                temp = ""
                ok += (tempRes == df['solution'][t])
            except:
                ok += 0
        print(f"Tỉ lệ chính xác khi chạy test từ {j - 10} đến {j - 1} là: {ok / 10}")
        j += 10
    
    # print("Kết quả:")
    # print(res)
    
def test_equation(test_file):
    equations = []
    answers = []
    
    with open(test_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            equation = row[0].strip()
            answer = row[1].strip()
            equations.append(equation)    
            answers.append([sympify(expr.strip()) for expr in answer[1:-1].split(',')])           
    
    ok = 0
    for i in tqdm(range(0, min(len(answers), len(equations))), desc="Đang Xử Lý", unit="test"):
        try: 
            input_data = "\nGiải " + equations[i]
            # print(input_data)
            res = main(input_data)
            
            check1 = set()
            check2 = set()
            for x in res['solutions']:
                check1.add(x)
            
            for x in answers[i]:
                check2.add(x)
                       
            ok += (check1 == check2)
        except:
            ok += 0
        
    print(f"Tỉ lệ chính xác: {ok / len(answers)}")
    print(f"Số lượng testcase: {len(answers)}")
        
def test_all():
    querys = []
    answers = []
    with open('tonghop.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            query = row[0].strip()
            answer = row[1].strip()
            querys.append(query)
            answers.append([sympify(expr.strip()) for expr in answer[1:-1].split(',')])  
            
    ok = 0
    for i in tqdm(range(0, min(len(answers), 30)), desc="Đang Xử Lý", unit="test"):
        try: 
            input_data = "\nGiải " + querys[i]
            # print(input_data)
            res = main(input_data)
            
            check1 = set()
            check2 = set()
            for x in res['solutions']:
                check1.add(x)
            
            for x in answers[i]:
                check2.add(x)
                         
            ok += (check1 == check2)
        except:
            ok += 0
        
    print(f"Tỉ lệ chính xác: {ok / len(answers)}")
    print(f"Số lượng testcase: {len(answers)}")
    
if __name__ == "__main__":
    print("Nhập bài toán (phương trình bậc 2, bậc 3 hoặc ma trận Sudoku):")
    try: 
        input_data = input()
        res = main(input_data)
        # print(res)
        print("Kết quả:")
        try:
            print(res['solved_sudoku'])
        except:
            print(res['solutions'])
    except:
        print(res['errors'])
