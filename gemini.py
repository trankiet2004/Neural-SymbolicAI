import os
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

chat_session = model.start_chat(
  history=[
  ]
)
def generate_prompt(input_text):
    # Prompt yêu cầu định dạng JSON
    prompt = f"""
    Dựa trên nội dung sau đây:
    {input_text}
    Nếu đề bài là giải phương trình, hãy trả về kết quả giống sympy với cấu trúc sau:
    coefficients
    rhs
    Lưu ý: Chỉ trả về nội dung các số hoặc ma trận, không thêm bất kì kí hiệu hay thông tin thừa nào cả.
    
    Nếu câu hỏi là sudoku, hãy trả về ma trận sudoku.
    
    Lưu ý: Chỉ trả về nội dung file hoặc ma trận, không thêm bất kì kí hiệu hay thông tin thừa nào cả(kể cả ```json).
    """
    return prompt
question = input()
prompt  = generate_prompt(question)
response = model.generate_content(prompt)

# print(response.text)
print(response.text)