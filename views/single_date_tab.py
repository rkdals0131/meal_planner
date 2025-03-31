import customtkinter as ctk
import tkinter as tk
from tkcalendar import Calendar
import datetime
from tkinter import messagebox
import threading
# from ..meal_planner_core import MealPlanner # 필요시 백엔드 직접 접근
# from ..utils import gui_utils # 유틸리티 함수 사용

class SingleDateTab(ctk.CTkFrame):
    def __init__(self, master, planner_core, main_app_methods):
        super().__init__(master)
        self.planner_core = planner_core # 백엔드 로직 객체
        self.main_app_methods = main_app_methods # 메인 앱의 필요한 메소드 (예: show_suggestions)

        self.selected_date = datetime.date.today()
        self.meal_entries = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        # --- 왼쪽: 캘린더 프레임 ---
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        calendar_title = ctk.CTkLabel(left_frame, text="날짜 선택", font=("Arial", 16, "bold"))
        calendar_title.pack(pady=10)

        cal_frame = tk.Frame(left_frame) # tkcalendar는 tk.Frame 필요
        cal_frame.pack(pady=10, fill="both", expand=True)

        self.calendar = Calendar(cal_frame, selectmode="day", date_pattern="yyyy-mm-dd")
        self.calendar.pack(fill="both", expand=True)
        self.calendar.bind("<<CalendarSelected>>", self.on_date_selected)

        # --- 오른쪽: 입력 프레임 ---
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)

        form_title = ctk.CTkLabel(right_frame, text="식단 정보 입력", font=("Arial", 16, "bold"))
        form_title.grid(row=0, column=0, pady=10)

        self.selected_date_label = ctk.CTkLabel(right_frame, text=f"선택된 날짜: {self.selected_date.strftime('%Y-%m-%d')}")
        self.selected_date_label.grid(row=1, column=0, pady=5)

        meal_frame = ctk.CTkFrame(right_frame)
        meal_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        for i, meal_type in enumerate(self.planner_core.meal_times.keys()):
            meal_label = ctk.CTkLabel(meal_frame, text=f"{meal_type}:")
            meal_label.grid(row=i, column=0, padx=10, pady=10, sticky="w")

            meal_entry = ctk.CTkEntry(meal_frame, width=200)
            meal_entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")

            # 추천 버튼 (메인 앱의 메소드 호출하도록 수정 가능)
            suggestion_btn = ctk.CTkButton(meal_frame, text="추천", width=60,
                                        command=lambda t=meal_type: self.main_app_methods['show_suggestions'](t, self.meal_entries[t]))
            suggestion_btn.grid(row=i, column=2, padx=5, pady=10)

            self.meal_entries[meal_type] = meal_entry

        button_frame = ctk.CTkFrame(right_frame)
        button_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        template_btn = ctk.CTkButton(button_frame, text="템플릿 사용", command=self.use_template)
        template_btn.grid(row=0, column=0, padx=10, pady=10)

        add_btn = ctk.CTkButton(button_frame, text="식단 추가", command=self.add_single_meal)
        add_btn.grid(row=0, column=1, padx=10, pady=10)

        clear_btn = ctk.CTkButton(button_frame, text="초기화", command=self.clear_entries)
        clear_btn.grid(row=0, column=2, padx=10, pady=10)


    def on_date_selected(self, event=None):
        selected_date_str = self.calendar.get_date()
        self.selected_date = datetime.datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        self.selected_date_label.configure(text=f"선택된 날짜: {self.selected_date.strftime('%Y-%m-%d')}")

    def use_template(self):
        # 메인 앱의 템플릿 선택 메소드 호출
        self.main_app_methods['use_template'](self.meal_entries)

    def clear_entries(self):
        for entry in self.meal_entries.values():
            entry.delete(0, "end")

    def add_single_meal(self):
        meal_plan = {}
        for meal_type, entry in self.meal_entries.items():
            meal_name = entry.get().strip()
            if meal_name:
                meal_plan[meal_type] = meal_name

        if not meal_plan:
            messagebox.showwarning("입력 오류", "최소 하나 이상의 식단 정보를 입력하세요.")
            return

        # 확인 메시지
        message = f"{self.selected_date.strftime('%Y-%m-%d')} 날짜에 다음 식단을 추가합니다:\n\n"
        for meal_type, meal_name in meal_plan.items():
            message += f"- {meal_type}: {meal_name}\n"

        confirm = messagebox.askyesno("확인", message + "\n추가하시겠습니까?")

        if confirm:
            # 메인 앱의 추가 스레드 호출
            self.main_app_methods['add_meal_thread'](self.selected_date, meal_plan)

            # 템플릿 저장 여부 확인 (메인 앱 메소드 호출)
            save_template = messagebox.askyesno("템플릿 저장", "이 식단을 템플릿으로 저장하시겠습니까?")
            if save_template:
                 self.main_app_methods['save_as_template'](meal_plan)

    # ... (탭 내에서만 사용되는 다른 헬퍼 메소드들) ...