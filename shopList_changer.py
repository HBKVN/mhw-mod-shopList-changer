import psutil
import os
import time
import shutil
import tkinter as tk
from tkinter import filedialog
import tkinter.font as tkFont
import json

settings_file = "setting.json"
clicked = None

#라벨에 완료 띄우고 3초 뒤 지우기
def show_result():
    label.config(text="완료")
    root.after(3000, clear_label)

def clear_label():
    label.config(text="")

#json 읽고 개인 폴더 위치 알려주기
def load_setting():
    if os.path.exists(settings_file):
        with open(settings_file, "r") as file:
            setting = json.load(file)
        game_entry.insert(0, setting.get("game_folder", ""))
        shop_entry.insert(0, setting.get("shop_folder", ""))
        show_lists(None)
    else:
        create_settings_file()

#json 기본 설정으로 만들기
def create_settings_file():
    setting = {"game_folder":"", "shop_folder":""}
    with open(settings_file, "w") as file:
        json.dump(setting, file)

#게임폴더, 상점폴더를 창 띄워서 폴더찾기로 입력하기
def game_folder():
    folder_path = filedialog.askdirectory()
    game_entry.delete(0, tk.END)
    game_entry.insert(0, folder_path)

def shop_folder():
    folder_path = filedialog.askdirectory()
    shop_entry.delete(0, tk.END)
    shop_entry.insert(0, folder_path)
    show_lists(None)

#리스트박스 업데이트
def show_lists(event):
    folder_path = shop_entry.get()  # shop_entry를 사용하여 Entry의 내용을 가져옴
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        listbox.delete(0, tk.END)  # Listbox 내용 지우기
        contents = os.listdir(folder_path)
        listbox.insert(tk.END, 'default shop')
        for item in contents:
            listbox.insert(tk.END, item)

#적용
def apply():
    game_value = game_entry.get()#게임 폴더 위치
    shop_value = shop_entry.get()#상점 폴더 위치
    global mhw_value#몬헌 실행파일 위치
    mhw_value = os.path.join(game_value, "MonsterHunterWorld.exe")
    
    if os.path.exists(game_value):
        if os.path.exists(mhw_value):
            if os.path.exists(shop_value):
                #setting.json에 입력한 주소 저장
                setting = {"game_folder":game_value, "shop_folder":shop_value}
                with open(settings_file, "w") as file:
                    json.dump(setting, file)
                selected_index = listbox.curselection()
                if selected_index:
                    selected_item = listbox.get(selected_index[0])
                    facility = 'nativePC/common/facility'
                    facility = os.path.join(game_value, facility)
                    os.makedirs(facility, exist_ok=True)
                    shopList = 'shopList.slt'
                    shopList = os.path.join(facility, shopList)
                    if selected_item == "default shop":
                        #상점 지우기
                        try:
                            os.remove(shopList)
                            show_result()
                        except OSError as e:
                            if os.path.exists(shopList):
                                tk.messagebox.showerror("에러","뭐가 잘못됐는지 모름")
                            else:
                                show_result()
                    else:
                        #상점 복사하기
                        selected = os.path.join(shop_value, selected_item)
                        try:
                            # 파일을 대상 폴더로 복사
                            shutil.copy(selected, shopList)
                            show_result()
                        except FileNotFoundError:
                            tk.messagebox.showerror("에러","파일을 찾을 수 없습니다.")
                        except PermissionError:
                            tk.messagebox.showerror("에러","파일 복사 권한이 없습니다.")
                        except shutil.Error as e:
                            tk.messagebox.showerror("에러","파일 복사 중 오류가 발생했습니다.")
                else:
                    tk.messagebox.showerror("에러","상점 리스트 중 하나를 선택해주세요.")
            else:
                tk.messagebox.showerror("에러","없는 shoplist 폴더 위치입니다.")
        else:
            tk.messagebox.showerror("에러","몬헌 폴더 위치에 몬헌 실행파일이 없습니다.")
    else:
        tk.messagebox.showerror("에러","없는 몬헌 폴더 위치입니다.")

#적용 및 재시작
def restart():
    apply()
    #작업관리자의 프로세스 모두 읽기
    for process in psutil.process_iter():
        #실행 중인 프로세스 중 몬헌이 있다면
        if "MonsterHunterWorld.exe" in process.name():
            psutil.Process(process.pid).kill()
            time.sleep(2)
            break
    time.sleep(1)
    os.system(f' "{mhw_value}" ')
    

#root, frame 선언
root = tk.Tk()
root.title("몬헌 상점 변경")
root.geometry("435x300+500+500")
root.resizable(width=False,height=False)
default_font = tkFont.Font(family="맑은 고딕", size=11)

frame_left = tk.Frame(root)
frame_left.grid(row=0,column=0,padx=10,pady=10)

frame_right = tk.Frame(root)
frame_right.grid(row=0,column=1,padx=10,pady=10)

frame_apply = tk.Frame(frame_left)
frame_apply.grid(row=6,column=0)

#frame_left에 들어갈 것들 선언
game_label = tk.Label(frame_left, text="몬헌 폴더 위치", font=default_font)
game_entry = tk.Entry(frame_left, font=default_font)
game_found_button = tk.Button(frame_left, text="몬헌 폴더 찾기", font=default_font, command=game_folder)

shop_label = tk.Label(frame_left, text="상점 폴더 위치", font=default_font)
shop_entry = tk.Entry(frame_left, font=default_font)
shop_found_button = tk.Button(frame_left, text="상점 폴더 찾기", font=default_font, command=shop_folder)

start_button = tk.Button(frame_apply, text="적용 및 재시작", font=default_font, command=restart)
apply_button = tk.Button(frame_apply, text="적용", font=default_font, command=apply)

game_label.grid(row=0,column=0,sticky="w")
game_entry.grid(row=1,column=0,sticky="w")
game_found_button.grid(row=2,column=0,sticky="w")

shop_label.grid(row=3,column=0,sticky="w")
shop_entry.grid(row=4,column=0,sticky="w")
shop_found_button.grid(row=5,column=0,pady=10,sticky="w")

start_button.grid(row=0,column=1,padx=5)
apply_button.grid(row=0,column=0)

shop_entry.bind("<KeyRelease>", show_lists)

#frame_right에 들어갈 것들 선언
listbox_description = tk.Label(frame_right, text="리스트를 선택하세요(스크롤 가능)", font=default_font)
listbox = tk.Listbox(frame_right, font=default_font, width=28, height=10)

listbox_description.grid(row=0,column=0,sticky="w")
listbox.grid(row=1, column=0, sticky="w")

label = tk.Label(root, text="", font=default_font)
label.grid(row=1,column=0, columnspan=2)

#초기 선언
load_setting()

root.mainloop()
