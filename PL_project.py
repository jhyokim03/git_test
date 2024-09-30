import tkinter as tk
from tkinter import messagebox
import requests
import json
import random
from PIL import Image, ImageTk

# 실시간 기온 API 설정
city = "Seoul"
apikey = "3a6593ed8571ebd6def0df987167baef"
lang = "kr"

api = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={apikey}&lang={lang}&units=metric"
result = requests.get(api)
data = json.loads(result.text)
print(data)
temp_value = float(data["main"]["feels_like"])  # 현재 체감 온도 불러오기
description = str(data["weather"][0]["description"])  # 날씨 상태 불러오기
print(description)

#옷 입력창 최적화
def create_label_entry(parent, label_text):
    label = tk.Label(parent, text=label_text)
    label.pack()
    entry = tk.Entry(parent)
    entry.pack()
    return entry

#옷 정보 입력창 gui
def input_clothes():
    input_window = tk.Toplevel(window)
    input_window.title("옷 정보 입력")

    # 옷 정보 입력을 위한 위젯 생성
    name_entry = create_label_entry(input_window, "옷 이름:")
    category_entry = create_label_entry(input_window, "상의/하의:")
    fit_entry = create_label_entry(input_window, "핏을 입력하세요:")
    
    tk.Label(input_window, text="색상을 선택하세요:").pack()
    color_var = tk.StringVar()
    
    tk.Radiobutton(input_window, text="연한 웜톤", variable=color_var, value="연한 웜톤").pack()
    tk.Radiobutton(input_window, text="진한 웜톤", variable=color_var, value="진한 웜톤").pack()
    tk.Radiobutton(input_window, text="연한 쿨톤", variable=color_var, value="연한 쿨톤").pack()
    tk.Radiobutton(input_window, text="진한 쿨톤", variable=color_var, value="진한 쿨톤").pack()
    tk.Radiobutton(input_window, text="흰색 계열", variable=color_var, value="흰색 계열").pack()    
    tk.Radiobutton(input_window, text="검은색 계열", variable=color_var, value="검은색 계열").pack()    

    tk.Label(input_window, text="룩을 선택하세요:").pack()
    look_vars = {look: tk.IntVar() for look in ["캐쥬얼", "힙", "댄디", "데일리룩", "스포츠"]}
    for look, var in look_vars.items():
        tk.Checkbutton(input_window, text=look, variable=var).pack()
    
    tk.Label(input_window, text="적합한 온도 범위:").pack()
    temp_var = tk.StringVar()
    tk.Radiobutton(input_window, text="23도 이하", variable=temp_var, value="23도 이하").pack()
    tk.Radiobutton(input_window, text="23도 이상", variable=temp_var, value="23도 이상").pack()
    
    image_entry = create_label_entry(input_window, "이미지 경로를 입력하세요:")

    tk.Button(input_window, text="저장", command=lambda: save_clothes(name_entry.get(), category_entry.get(), fit_entry.get(), color_var, look_vars, temp_var.get(), image_entry.get())).pack()

#옷 정보 파일에 저장
def save_clothes(name, category, fit, color, look_vars, temp, image_path):
    selected_looks = [look for look, var in look_vars.items() if var.get() == 1]
    if not selected_looks:
        messagebox.showerror("오류", "적어도 하나의 룩을 선택해야 합니다.")
        return
    
    looks_str = '/'.join(selected_looks)
    image_path = image_path.strip('"')  # 이미지 경로에서 따옴표 제거
    with open("Clothes Information.txt", "a", encoding="utf-8") as file:
        file.write(f"{name},{category},{fit},{color.get()},{looks_str},{temp},{image_path}\n")
    messagebox.showinfo("알림", "옷 정보가 저장되었습니다.")

#옷 추천창 열기
def recommend_clothes():
    recommend_window = tk.Toplevel(window) #새로운 Toplevel 창 생성
    recommend_window.title("옷 추천")
    
    tk.Label(recommend_window, text="원하는 룩을 선택하세요:").pack()
    look_vars = {look: tk.IntVar() for look in ["캐쥬얼", "힙", "댄디", "데일리룩", "스포츠"]} 
#IntVar 객체창 열고 옷 스타일 목록("캐쥬얼", "힙", "댄디", "데일리룩", "스포츠")을 키로 하고, 각 스타일에 대한 IntVar 객체를 값으로 하는 딕셔너리 #그냥 tkinter 구성하는 거
    for look, var in look_vars.items(): #키 벨류 값 한번에 가져오기
        tk.Checkbutton(recommend_window, text=look, variable=var).pack()
    
    tk.Button(recommend_window, text="추천 받기", command=lambda: get_recommendations(look_vars)).pack()

#선택된 룩에 맞는 옷 종합적 추천
def get_recommendations(look_vars):
    """선택된 룩과 온도에 맞는 옷을 추천합니다."""
    selected_looks = [look for look, var in look_vars.items() if var.get() == 1]  #gpt 사용
    if not selected_looks:
        messagebox.showerror("오류", "적어도 하나의 룩을 선택해야 합니다.")
        return
    
    top_recommendations = []
    bottom_recommendations = []
    
    try:
        with open("Clothes Information.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        messagebox.showerror("오류", "Clothes Information.txt 파일을 찾을 수 없습니다.")
        return

    for line in lines:
        clothing_info = line.strip().split(',')
        if len(clothing_info) < 7:
            continue  # 데이터 형식이 잘못된 줄은 건너뜁니다
        
        name, category, fit, color, looks, temp_condition, image_path = clothing_info
        looks_list = looks.split('/')
        
        if bool(set(looks_list) & set(selected_looks)): #gpt 사용
            if (temp_condition == "23도 이하" and temp_value <= 23) or (temp_condition == "23도 이상" and temp_value > 23):
                if category == "상의":
                    top_recommendations.append((name, {"category": category, "fit": fit, "color": color, "look": looks, "temp_condition": temp_condition, "image_path": image_path}))
                elif category == "하의":
                    bottom_recommendations.append((name, {"category": category, "fit": fit, "color": color, "look": looks, "temp_condition": temp_condition, "image_path": image_path}))

    selected_top = match_weather_clothes(top_recommendations)
    selected_bottom = match_color_clothes(selected_top, bottom_recommendations)
    
    #상하의 출력 결과 표시
    messagebox.showinfo("상의 추천",selected_top)
    messagebox.showinfo("하의 추천",selected_bottom)

    if selected_top and selected_bottom:
        recommendation_window = tk.Toplevel(window)
        recommendation_window.title("추천된 옷")

        # 상의 이미지
        top_image_path = selected_top[1]["image_path"].strip('"').replace("\\", "\\\\")  # 따옴표 제거 및 경로 수정
        top_image = Image.open(top_image_path)
        top_image = top_image.resize((300, 300), Image.LANCZOS)
        top_photo = ImageTk.PhotoImage(top_image)
        top_image_label = tk.Label(recommendation_window, image=top_photo)
        top_image_label.image = top_photo  # 이미지 객체를 유지하기 위해 참조를 저장
        top_image_label.pack()

        # 하의 이미지
        bottom_image_path = selected_bottom[1]["image_path"].strip('"').replace("\\", "\\\\")  # 따옴표 제거 및 경로 수정
        bottom_image = Image.open(bottom_image_path)
        bottom_image = bottom_image.resize((300, 300), Image.LANCZOS)
        bottom_photo = ImageTk.PhotoImage(bottom_image)
        bottom_image_label = tk.Label(recommendation_window, image=bottom_photo)
        bottom_image_label.image = bottom_photo  # 이미지 객체를 유지하기 위해 참조를 저장
        bottom_image_label.pack()
        
    else:
        if not selected_top:
            messagebox.showinfo("상의 추천", "추천할 상의가 없습니다.")
        if not selected_bottom:
            messagebox.showinfo("하의 추천", "추천할 하의가 없습니다.")


def match_weather_clothes(top_recommendations):
    global description

    # 날씨가 맑을 때 색깔 있는 상의 추천 확률 높이기
    if description == "맑음":
        enhanced_tops = []
        for top in top_recommendations:
            top_color = top[1]["color"]
            enhanced_tops.append(top)
            if top_color in ["연한 웜톤", "진한 웜톤", "연한 쿨톤", "진한 쿨톤"]:
                enhanced_tops.append(top)  # 웜톤과 쿨톤 상의를 한 번 더 추가하여 확률을 높임

        return random.choice(enhanced_tops) 

    # 날씨가 맑지 않은 경우 무채색 상의 추천 확률 높이기
    else:
        enhanced_tops = []
        for top in top_recommendations:
            top_color = top[1]["color"]
            enhanced_tops.append(top)
            if top_color in ["흰색 계열", "검은색 계열"]:
                enhanced_tops.append(top)  # 무채색 계열 상의를 한 번 더 추가하여 확률을 높임

        return random.choice(enhanced_tops)
        
    
#상하의 색상 안정적으로 조합하기
def match_color_clothes(selected_top, bottom_recommendations):
    if selected_top:
        top_color = selected_top[1]["color"]
        for bottom in bottom_recommendations:
            bottom_color = bottom[1]["color"]
            if top_color == "연한 웜톤":
                if bottom_color != "진한 쿨톤":
                    return bottom
            elif top_color == "진한 웜톤":
                if bottom_color != "연한 쿨톤":
                    return bottom
            elif top_color == "연한 쿨톤":
                if bottom_color != "진한 쿨톤":
                    return bottom
            elif top_color == "진한 쿨톤":
                if bottom_color != "연한 웜톤":
                    return bottom
            elif top_color == "흰색 계열":
                if bottom_color != "흰색 계열":
                    return bottom
            elif top_color == "검은색 계열":
                if bottom_color != "검은색 계열":
                    return bottom
    return None

# 메인 Tkinter 윈도우 설정
window = tk.Tk()
window.title("옷 추천 시스템")

image_path = "C:\\Users\\jhyok\\OneDrive\\바탕 화면\\vs workplace\\pl_image.jpeg"
image = Image.open(image_path)
resized_image = image.resize((500, 500), Image.LANCZOS) #gpt 사용
photo = ImageTk.PhotoImage(resized_image)
image_label = tk.Label(window, image=photo)
image_label.image = photo  # 이미지 객체를 유지하기 위해 참조를 저장
image_label.pack()

# 버튼 생성
tk.Button(window, text="옷 입력", command=input_clothes).pack()
tk.Button(window, text="옷 추천", command=recommend_clothes).pack()

# 윈도우 설정
window.geometry("800x700+300+200")
window.resizable(True, False)

# 메인 루프 실행
window.mainloop()
