import re
import os
import json
import pandas as pd
from tqdm import tqdm
import google.generativeai as genai
from symbolicAI import parse_equation_text, solve_polynomial, solve_sudoku_with_constraints

# genai.configure(api_key="AIzaSyBn8T5HqQuQfJlfEQSXW5k6fYjqPnc8ZOM")
genai.configure(api_key="AIzaSyDvXPvJ06_yqoNWLzV2kX1xFIaVQjDBmeU")
 
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
                # print("YEAH", sudoku_array)
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

    return (result)

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

if __name__ == "__main__":
    chunk_size = 100
    chunks = []    
    with tqdm(total=100, desc="Reading file") as pbar:  # Tổng là 100 vì chỉ đọc 100 dòng
        for chunk in pd.read_csv('sudoku.csv', chunksize=chunk_size):
            chunks.append(chunk)
            pbar.update(chunk.shape[0])
            break  # Dừng lại sau khi đọc 1 chunk

    df = pd.concat(chunks, ignore_index=True)

    print(f"File được đọc thành công! Tổng số dòng: {len(df)}")

    ok, test = 0, 100
    # print("Nhập bài toán (phương trình bậc 2, bậc 3 hoặc ma trận Sudoku):")
    for t in tqdm(range(min(len(df), test)), desc="Test Sudoku từ testcase 0 đến testcase 99"):
        try: 
            # input_data = input()
            input_data = "\nGiải sudoku " + stringToMatrix(df['puzzle'][t])
            # input_data = "\nGiải sudoku " + "[[5,3,0,0,7,0,0,0,0],[6,0,0,1,9,5,0,0,0],[0,9,8,0,0,0,0,6,0],[8,0,0,0,6,0,0,0,3],[4,0,0,8,0,3,0,0,1],[7,0,0,0,2,0,0,0,6],[0,6,0,0,0,0,2,8,0],[0,0,0,4,1,9,0,0,5],[0,0,0,0,8,0,0,7,9]]"
            res = main(input_data)
            tempRes = ""
            
            for i in res['solved_sudoku']:
                for j in i:
                    tempRes += str(j)
            
            temp = ""
            ok += (tempRes == df['solution'][t])
            # ok += (tempRes == "534678912672195348198342567859761423426853791713924856961537284287419635345286179")
        except:
            ok += 0

    print(f"Tỉ lệ chính xác khi chạy test từ 0 đến 99 là: {ok / test}")
    print(f"Số lượng test: {test}")

    j = 10
    while j <= 100:
        ok = 0
        for t in tqdm(range(j - 10, j), desc=f"Test Sudoku từ testcase {j - 10} đến testcase {j - 1}"):
            try: 
                # input_data = input()
                input_data = "\nGiải sudoku " + stringToMatrix(df['puzzle'][t])
                # input_data = "\nGiải sudoku " + "[[5,3,0,0,7,0,0,0,0],[6,0,0,1,9,5,0,0,0],[0,9,8,0,0,0,0,6,0],[8,0,0,0,6,0,0,0,3],[4,0,0,8,0,3,0,0,1],[7,0,0,0,2,0,0,0,6],[0,6,0,0,0,0,2,8,0],[0,0,0,4,1,9,0,0,5],[0,0,0,0,8,0,0,7,9]]"
                res = main(input_data)
                tempRes = ""
                
                for i in res['solved_sudoku']:
                    for jj in i:
                        tempRes += str(jj)
                
                temp = ""
                ok += (tempRes == df['solution'][t])
                # ok += (tempRes == "534678912672195348198342567859761423426853791713924856961537284287419635345286179")
            except:
                ok += 0
        print(f"Tỉ lệ chính xác khi chạy test từ {j - 10} đến {j - 1} là: {ok / 10}")
        j += 10
    
    # print("Kết quả:")
    # print(res)