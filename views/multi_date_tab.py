import customtkinter as ctk
import tkinter as tk
from tkcalendar import Calendar
import datetime
from tkinter import messagebox
from datetime import date

class MultiDateTab(ctk.CTkFrame):
    def __init__(self, master, planner_core, main_app_methods):
        super().__init__(master)
        self.planner_core = planner_core
        self.main_app_methods = main_app_methods
        
        # 변수 초기화
        self.selected_dates = []
        self.meal_entries = {}
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_widgets()
    
    def create_widgets(self):
        # 왼쪽: 날짜 목록 프레임
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # 타이틀
        list_title = ctk.CTkLabel(left_frame, text="날짜 목록", font=("Arial", 16, "bold"))
        list_title.pack(pady=10)
        
        # 날짜 추가 프레임
        add_date_frame = ctk.CTkFrame(left_frame)
        add_date_frame.pack(padx=10, pady=10, fill="x")
        
        # 여러 가지 추가 방법 (범위/개별)
        self.add_method_var = ctk.StringVar(value="개별 날짜")
        add_method_label = ctk.CTkLabel(add_date_frame, text="추가 방법:")
        add_method_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        add_methods = ["개별 날짜", "날짜 범위"]
        add_method_menu = ctk.CTkOptionMenu(add_date_frame, values=add_methods, 
                                           variable=self.add_method_var,
                                           command=self.update_add_frame)
        add_method_menu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # 날짜 선택 프레임 (동적 변경됨)
        self.date_selection_frame = ctk.CTkFrame(left_frame)
        self.date_selection_frame.pack(padx=10, pady=10, fill="x")
        
        # 초기 프레임 설정
        self.setup_individual_date_frame()
        
        # 날짜 목록 프레임
        dates_frame = ctk.CTkFrame(left_frame)
        dates_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        dates_label = ctk.CTkLabel(dates_frame, text="선택된 날짜:")
        dates_label.pack(pady=5, anchor="w")
        
        # 날짜 목록 (스크롤 가능)
        dates_scroll = ctk.CTkScrollableFrame(dates_frame, width=200, height=200)
        dates_scroll.pack(pady=5, fill="both", expand=True)
        
        self.dates_listbox = tk.Listbox(dates_scroll, width=20, height=10)
        self.dates_listbox.pack(fill="both", expand=True)
        
        # 날짜 제거 버튼
        remove_btn = ctk.CTkButton(dates_frame, text="선택 날짜 제거", 
                                  command=self.remove_individual_date)
        remove_btn.pack(pady=5, fill="x")
        
        clear_btn = ctk.CTkButton(dates_frame, text="모든 날짜 제거", 
                                 command=self.clear_individual_dates)
        clear_btn.pack(pady=5, fill="x")
        
        # 오른쪽: 입력 프레임
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        
        # 입력 폼 타이틀
        form_title = ctk.CTkLabel(right_frame, text="식단 정보 입력", font=("Arial", 16, "bold"))
        form_title.grid(row=0, column=0, pady=10)
        
        # 선택된 날짜 갯수 표시
        self.date_count_label = ctk.CTkLabel(right_frame, text="선택된 날짜: 0개")
        self.date_count_label.grid(row=1, column=0, pady=5)
        
        # 식단 입력 프레임
        meal_frame = ctk.CTkFrame(right_frame)
        meal_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # 식단 입력 필드들
        for i, meal_type in enumerate(self.planner_core.meal_times.keys()):
            meal_label = ctk.CTkLabel(meal_frame, text=f"{meal_type}:")
            meal_label.grid(row=i, column=0, padx=10, pady=10, sticky="w")
            
            meal_entry = ctk.CTkEntry(meal_frame, width=200)
            meal_entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            
            # 추천 버튼 (기록에서 가져오기)
            suggestion_btn = ctk.CTkButton(meal_frame, text="추천", width=60, 
                                          command=lambda t=meal_type: self.main_app_methods['show_suggestions'](t, self.meal_entries[t]))
            suggestion_btn.grid(row=i, column=2, padx=5, pady=10)
            
            self.meal_entries[meal_type] = meal_entry
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(right_frame)
        button_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        # 템플릿 사용 버튼
        template_btn = ctk.CTkButton(button_frame, text="템플릿 사용", 
                                     command=self.use_template)
        template_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # 식단 추가 버튼
        add_btn = ctk.CTkButton(button_frame, text="식단 추가", 
                               command=self.add_multi_meal)
        add_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # 초기화 버튼
        clear_btn = ctk.CTkButton(button_frame, text="입력 초기화", 
                                 command=self.clear_entries)
        clear_btn.grid(row=0, column=2, padx=10, pady=10)
    
    def update_add_frame(self, event=None):
        """추가 방법에 따라 프레임 업데이트"""
        method = self.add_method_var.get()
        
        # 기존 프레임의 모든 위젯 제거
        for widget in self.date_selection_frame.winfo_children():
            widget.destroy()
        
        if method == "개별 날짜":
            self.setup_individual_date_frame()
        else:  # 날짜 범위
            self.setup_range_date_frame()
    
    def setup_individual_date_frame(self):
        """개별 날짜 추가 프레임 설정"""
        # 날짜 선택 필드
        date_label = ctk.CTkLabel(self.date_selection_frame, text="날짜:")
        date_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.individual_date_entry = ctk.CTkEntry(self.date_selection_frame, width=150)
        self.individual_date_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.individual_date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        date_picker_btn = ctk.CTkButton(self.date_selection_frame, text="선택", width=40, 
                                       command=lambda: self.main_app_methods['show_date_picker'](self.individual_date_entry))
        date_picker_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # 날짜 추가 버튼
        add_date_btn = ctk.CTkButton(self.date_selection_frame, text="추가", 
                                    command=self.add_individual_date)
        add_date_btn.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
    
    def setup_range_date_frame(self):
        """날짜 범위 추가 프레임 설정"""
        # 시작 날짜
        start_label = ctk.CTkLabel(self.date_selection_frame, text="시작 날짜:")
        start_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.start_date_entry = ctk.CTkEntry(self.date_selection_frame, width=150)
        self.start_date_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.start_date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        start_picker_btn = ctk.CTkButton(self.date_selection_frame, text="선택", width=40, 
                                        command=lambda: self.main_app_methods['show_date_picker'](self.start_date_entry))
        start_picker_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # 종료 날짜
        end_label = ctk.CTkLabel(self.date_selection_frame, text="종료 날짜:")
        end_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.end_date_entry = ctk.CTkEntry(self.date_selection_frame, width=150)
        self.end_date_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.end_date_entry.insert(0, (date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d"))
        
        end_picker_btn = ctk.CTkButton(self.date_selection_frame, text="선택", width=40, 
                                      command=lambda: self.main_app_methods['show_date_picker'](self.end_date_entry))
        end_picker_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # 제외할 요일 선택
        exclude_label = ctk.CTkLabel(self.date_selection_frame, text="제외할 요일:")
        exclude_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        exclude_frame = ctk.CTkFrame(self.date_selection_frame)
        exclude_frame.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        
        days = ["월", "화", "수", "목", "금", "토", "일"]
        self.exclude_vars = []
        
        for i, day in enumerate(days):
            var = tk.IntVar(value=0)
            self.exclude_vars.append(var)
            
            checkbox = ctk.CTkCheckBox(exclude_frame, text=day, variable=var, width=40, checkbox_width=16)
            checkbox.grid(row=0, column=i, padx=5, pady=5)
        
        # 날짜 추가 버튼
        add_range_btn = ctk.CTkButton(self.date_selection_frame, text="범위 추가", 
                                     command=self.add_date_range)
        add_range_btn.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
    
    def add_individual_date(self):
        """개별 날짜 추가"""
        try:
            date_str = self.individual_date_entry.get().strip()
            if not date_str:
                messagebox.showwarning("입력 오류", "날짜를 입력하세요.")
                return
            
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # 이미 목록에 있는지 확인
            date_str_formatted = date_obj.strftime("%Y-%m-%d")
            if date_str_formatted in self.selected_dates:
                messagebox.showinfo("알림", "이미 선택된 날짜입니다.")
                return
            
            # 목록에 추가
            self.selected_dates.append(date_str_formatted)
            self.dates_listbox.insert(tk.END, date_str_formatted)
            
            # 라벨 업데이트
            self.date_count_label.configure(text=f"선택된 날짜: {len(self.selected_dates)}개")
        except ValueError:
            messagebox.showwarning("입력 오류", "올바른 날짜 형식이 아닙니다. YYYY-MM-DD 형식으로 입력하세요.")
    
    def add_date_range(self):
        """날짜 범위 추가"""
        try:
            start_str = self.start_date_entry.get().strip()
            end_str = self.end_date_entry.get().strip()
            
            if not start_str or not end_str:
                messagebox.showwarning("입력 오류", "시작 날짜와 종료 날짜를 모두 입력하세요.")
                return
            
            start_date = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_str, "%Y-%m-%d").date()
            
            if start_date > end_date:
                messagebox.showwarning("입력 오류", "종료 날짜는 시작 날짜보다 같거나 뒤여야 합니다.")
                return
            
            # 제외할 요일 (0: 월요일, 6: 일요일)
            excluded_days = [i for i, var in enumerate(self.exclude_vars) if var.get() == 1]
            
            # 날짜 범위 생성 및 추가
            current_date = start_date
            added_count = 0
            
            while current_date <= end_date:
                # 요일 확인 (월요일=0, 일요일=6)
                weekday = current_date.weekday()
                
                if weekday not in excluded_days:
                    date_str = current_date.strftime("%Y-%m-%d")
                    if date_str not in self.selected_dates:
                        self.selected_dates.append(date_str)
                        self.dates_listbox.insert(tk.END, date_str)
                        added_count += 1
                
                current_date += datetime.timedelta(days=1)
            
            # 라벨 업데이트
            self.date_count_label.configure(text=f"선택된 날짜: {len(self.selected_dates)}개")
            
            messagebox.showinfo("완료", f"{added_count}개의 날짜가 추가되었습니다.")
        except ValueError:
            messagebox.showwarning("입력 오류", "올바른 날짜 형식이 아닙니다. YYYY-MM-DD 형식으로 입력하세요.")
    
    def remove_individual_date(self):
        """선택한 날짜 제거"""
        selected_indices = self.dates_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("알림", "제거할 날짜를 선택하세요.")
            return
        
        # 역순으로 제거 (인덱스 변화 방지)
        for i in sorted(selected_indices, reverse=True):
            date_str = self.dates_listbox.get(i)
            self.dates_listbox.delete(i)
            self.selected_dates.remove(date_str)
        
        # 라벨 업데이트
        self.date_count_label.configure(text=f"선택된 날짜: {len(self.selected_dates)}개")
    
    def clear_individual_dates(self):
        """모든 날짜 제거"""
        self.dates_listbox.delete(0, tk.END)
        self.selected_dates = []
        
        # 라벨 업데이트
        self.date_count_label.configure(text="선택된 날짜: 0개")
    
    def use_template(self):
        """템플릿 사용"""
        self.main_app_methods['use_template'](self.meal_entries)
    
    def clear_entries(self):
        """입력 필드 초기화"""
        for entry in self.meal_entries.values():
            entry.delete(0, "end")
    
    def add_multi_meal(self):
        """여러 날짜에 식단 추가"""
        if not self.selected_dates:
            messagebox.showwarning("입력 오류", "최소 하나 이상의 날짜를 선택하세요.")
            return
        
        meal_plan = {}
        for meal_type, entry in self.meal_entries.items():
            meal_name = entry.get().strip()
            if meal_name:
                meal_plan[meal_type] = meal_name
        
        if not meal_plan:
            messagebox.showwarning("입력 오류", "최소 하나 이상의 식단 정보를 입력하세요.")
            return
        
        # 확인 메시지
        date_count = len(self.selected_dates)
        message = f"{date_count}개의 날짜에 다음 식단을 추가합니다:\n\n"
        for meal_type, meal_name in meal_plan.items():
            message += f"- {meal_type}: {meal_name}\n"
        
        confirm = messagebox.askyesno("확인", message + "\n추가하시겠습니까?")
        
        if confirm:
            # 날짜 객체 변환
            date_objects = []
            for date_str in self.selected_dates:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                date_objects.append(date_obj)
            
            # 메인 앱의 추가 스레드 호출
            self.main_app_methods['add_multi_meal_thread'](date_objects, meal_plan)
            
            # 템플릿 저장 여부 확인
            save_template = messagebox.askyesno("템플릿 저장", "이 식단을 템플릿으로 저장하시겠습니까?")
            if save_template:
                self.main_app_methods['save_as_template'](meal_plan)
