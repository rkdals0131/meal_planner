import customtkinter as ctk
import tkinter as tk
from tkcalendar import Calendar
import datetime
from tkinter import messagebox
from datetime import date

class RecurringTab(ctk.CTkFrame):
    def __init__(self, master, planner_core, main_app_methods):
        super().__init__(master)
        self.planner_core = planner_core
        self.main_app_methods = main_app_methods
        
        # 변수 초기화
        self.meal_entries = {}
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_widgets()
    
    def create_widgets(self):
        # 왼쪽: 반복 설정 프레임
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # 타이틀
        recur_title = ctk.CTkLabel(left_frame, text="반복 설정", font=("Arial", 16, "bold"))
        recur_title.pack(pady=10)
        
        # 시작 날짜 프레임
        start_date_frame = ctk.CTkFrame(left_frame)
        start_date_frame.pack(padx=10, pady=10, fill="x")
        
        start_label = ctk.CTkLabel(start_date_frame, text="시작 날짜:")
        start_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.start_date_entry = ctk.CTkEntry(start_date_frame, width=150)
        self.start_date_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.start_date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        start_picker_btn = ctk.CTkButton(start_date_frame, text="선택", width=40,
                                       command=lambda: self.main_app_methods['show_date_picker'](self.start_date_entry))
        start_picker_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # 반복 설정 프레임
        recur_frame = ctk.CTkFrame(left_frame)
        recur_frame.pack(padx=10, pady=10, fill="x")
        
        # 반복 유형
        recur_type_label = ctk.CTkLabel(recur_frame, text="반복 유형:")
        recur_type_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.recur_type_var = ctk.StringVar(value="매일")
        recur_types = ["매일", "매주", "매월", "매년"]
        recur_type_menu = ctk.CTkOptionMenu(recur_frame, values=recur_types, 
                                           variable=self.recur_type_var,
                                           command=self.update_recur_options)
        recur_type_menu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # 반복 옵션 프레임 (동적 변경됨)
        self.recur_options_frame = ctk.CTkFrame(recur_frame)
        self.recur_options_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        # 초기 옵션 설정 - 매일
        self.setup_daily_options()
        
        # 종료 설정 프레임
        end_frame = ctk.CTkFrame(left_frame)
        end_frame.pack(padx=10, pady=10, fill="x")
        
        end_label = ctk.CTkLabel(end_frame, text="종료 설정:")
        end_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.end_type_var = ctk.StringVar(value="날짜 지정")
        end_types = ["날짜 지정"]
        end_type_menu = ctk.CTkOptionMenu(end_frame, values=end_types, 
                                         variable=self.end_type_var,
                                         command=self.update_end_options)
        end_type_menu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # 종료 옵션 프레임 (동적 변경됨)
        self.end_options_frame = ctk.CTkFrame(end_frame)
        self.end_options_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        # 초기 종료 설정을 '날짜 지정'으로 설정
        self.setup_end_date_options()
        
        # 오른쪽: 입력 프레임
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        
        # 입력 폼 타이틀
        form_title = ctk.CTkLabel(right_frame, text="식단 정보 입력", font=("Arial", 16, "bold"))
        form_title.grid(row=0, column=0, pady=10)
        
        # 식단 입력 프레임
        meal_frame = ctk.CTkFrame(right_frame)
        meal_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
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
        button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # 템플릿 사용 버튼
        template_btn = ctk.CTkButton(button_frame, text="템플릿 사용", 
                                     command=self.use_template)
        template_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # 식단 추가 버튼
        add_btn = ctk.CTkButton(button_frame, text="반복 식단 추가", 
                               command=self.add_recurring_meal)
        add_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # 초기화 버튼
        clear_btn = ctk.CTkButton(button_frame, text="입력 초기화", 
                                 command=self.clear_entries)
        clear_btn.grid(row=0, column=2, padx=10, pady=10)
    
    def setup_daily_options(self):
        """매일 반복 옵션 설정"""
        # 기존 옵션 프레임의 모든 위젯 제거
        for widget in self.recur_options_frame.winfo_children():
            widget.destroy()
        
        # 매일 반복에는 특별한 옵션이 없으므로 간단한 설명만 표시
        daily_label = ctk.CTkLabel(self.recur_options_frame, text="매일 반복됩니다.")
        daily_label.pack(pady=5)
    
    def setup_weekly_options(self):
        """매주 반복 옵션 설정"""
        # 기존 옵션 프레임의 모든 위젯 제거
        for widget in self.recur_options_frame.winfo_children():
            widget.destroy()
        
        # 요일 선택
        days_label = ctk.CTkLabel(self.recur_options_frame, text="반복할 요일:")
        days_label.pack(pady=5, anchor="w")
        
        days_frame = ctk.CTkFrame(self.recur_options_frame)
        days_frame.pack(pady=5, fill="x")
        
        days = ["월", "화", "수", "목", "금", "토", "일"]
        self.weekly_day_vars = []
        
        for i, day in enumerate(days):
            var = tk.IntVar(value=0)
            self.weekly_day_vars.append(var)
            
            # 첫 번째 요일(오늘)은 기본 선택
            if i == date.today().weekday():
                var.set(1)
            
            checkbox = ctk.CTkCheckBox(days_frame, text=day, variable=var, width=40, checkbox_width=16)
            checkbox.grid(row=0, column=i, padx=5, pady=5)
    
    def setup_monthly_options(self):
        """매월 반복 옵션 설정"""
        # 기존 옵션 프레임의 모든 위젯 제거
        for widget in self.recur_options_frame.winfo_children():
            widget.destroy()
        
        # 월 반복 유형
        self.monthly_type_var = ctk.StringVar(value="날짜")
        types = ["날짜", "요일"]
        
        type_frame = ctk.CTkFrame(self.recur_options_frame)
        type_frame.pack(pady=5, fill="x")
        
        type_label = ctk.CTkLabel(type_frame, text="반복 기준:")
        type_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        type_menu = ctk.CTkOptionMenu(type_frame, values=types, 
                                     variable=self.monthly_type_var,
                                     command=self.update_monthly_options)
        type_menu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # 월 반복 옵션 프레임
        self.monthly_options_subframe = ctk.CTkFrame(self.recur_options_frame)
        self.monthly_options_subframe.pack(pady=5, fill="x")
        
        # 초기 옵션: 날짜 기준
        self.setup_monthly_date_options()
    
    def update_monthly_options(self, event=None):
        """월 반복 옵션 업데이트"""
        # 기존 옵션 프레임의 모든 위젯 제거
        for widget in self.monthly_options_subframe.winfo_children():
            widget.destroy()
        
        if self.monthly_type_var.get() == "날짜":
            self.setup_monthly_date_options()
        else:  # 요일
            self.setup_monthly_weekday_options()
    
    def setup_monthly_date_options(self):
        """월 반복 날짜 기준 옵션"""
        date_label = ctk.CTkLabel(self.monthly_options_subframe, text="매월 다음 날짜에 반복:")
        date_label.pack(pady=5, anchor="w")
        
        # 시작 날짜의 일(day)을 가져와서 기본값으로 설정
        default_day = date.today().day
        
        self.monthly_day_var = tk.IntVar(value=default_day)
        day_frame = ctk.CTkFrame(self.monthly_options_subframe)
        day_frame.pack(pady=5, fill="x")
        
        days = list(range(1, 32))
        day_menu = ctk.CTkOptionMenu(day_frame, values=[str(d) for d in days], 
                                    variable=self.monthly_day_var)
        day_menu.pack(side="left", padx=10)
        
        day_suffix = ctk.CTkLabel(day_frame, text="일")
        day_suffix.pack(side="left")
    
    def setup_monthly_weekday_options(self):
        """월 반복 요일 기준 옵션"""
        weekday_label = ctk.CTkLabel(self.monthly_options_subframe, text="매월 다음 요일에 반복:")
        weekday_label.pack(pady=5, anchor="w")
        
        # 현재 날짜의 주/요일 정보
        today = date.today()
        week_num = (today.day - 1) // 7 + 1
        weekday = today.weekday()
        
        weekday_frame = ctk.CTkFrame(self.monthly_options_subframe)
        weekday_frame.pack(pady=5, fill="x")
        
        # 주차 선택
        week_label = ctk.CTkLabel(weekday_frame, text="주차:")
        week_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        weeks = ["첫째", "둘째", "셋째", "넷째", "마지막"]
        self.monthly_week_var = ctk.StringVar(value=weeks[min(week_num-1, 4)])
        
        week_menu = ctk.CTkOptionMenu(weekday_frame, values=weeks, 
                                     variable=self.monthly_week_var)
        week_menu.grid(row=0, column=1, padx=5, pady=5)
        
        # 요일 선택
        days_label = ctk.CTkLabel(weekday_frame, text="요일:")
        days_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        days = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        self.monthly_weekday_var = ctk.StringVar(value=days[weekday])
        
        days_menu = ctk.CTkOptionMenu(weekday_frame, values=days, 
                                     variable=self.monthly_weekday_var)
        days_menu.grid(row=0, column=3, padx=5, pady=5)
    
    def setup_yearly_options(self):
        """매년 반복 옵션 설정"""
        # 기존 옵션 프레임의 모든 위젯 제거
        for widget in self.recur_options_frame.winfo_children():
            widget.destroy()
        
        yearly_label = ctk.CTkLabel(self.recur_options_frame, text="매년 같은 날짜에 반복됩니다.")
        yearly_label.pack(pady=5)
        
        # 오늘 날짜 표시
        today = date.today()
        date_label = ctk.CTkLabel(self.recur_options_frame, 
                                 text=f"({today.month}월 {today.day}일)")
        date_label.pack(pady=5)
    
    def update_recur_options(self, event=None):
        """반복 유형에 따라 옵션 업데이트"""
        recur_type = self.recur_type_var.get()
        
        if recur_type == "매일":
            self.setup_daily_options()
        elif recur_type == "매주":
            self.setup_weekly_options()
        elif recur_type == "매월":
            self.setup_monthly_options()
        elif recur_type == "매년":
            self.setup_yearly_options()
    
    def update_end_options(self, event=None):
        """종료 설정 옵션 업데이트"""
        # 기존 옵션 프레임의 모든 위젯 제거
        for widget in self.end_options_frame.winfo_children():
            widget.destroy()
        
        # 날짜 지정 옵션 설정
        self.setup_end_date_options()
    
    def setup_end_date_options(self):
        """종료 날짜 지정 옵션 설정"""
        end_date_frame = ctk.CTkFrame(self.end_options_frame)
        end_date_frame.pack(pady=5, fill="x")
        
        end_date_label = ctk.CTkLabel(end_date_frame, text="종료 날짜:")
        end_date_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # 기본값으로 시작일로부터 1년 후 날짜 설정
        default_end_date = date.today() + datetime.timedelta(days=365)
        
        self.end_date_entry = ctk.CTkEntry(end_date_frame, width=150)
        self.end_date_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.end_date_entry.insert(0, default_end_date.strftime("%Y-%m-%d"))
        
        end_picker_btn = ctk.CTkButton(end_date_frame, text="선택", width=40,
                                     command=lambda: self.main_app_methods['show_date_picker'](self.end_date_entry))
        end_picker_btn.grid(row=0, column=2, padx=5, pady=5)
    
    def use_template(self):
        """템플릿 사용"""
        self.main_app_methods['use_template'](self.meal_entries)
    
    def clear_entries(self):
        """입력 필드 초기화"""
        for entry in self.meal_entries.values():
            entry.delete(0, "end")
    
    def get_recurrence_rule(self):
        """반복 규칙 생성"""
        recur_type = self.recur_type_var.get()
        
        if recur_type == "매일":
            return "RRULE:FREQ=DAILY"
        
        elif recur_type == "매주":
            # 선택된 요일 확인
            selected_days = []
            weekdays = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
            
            for i, var in enumerate(self.weekly_day_vars):
                if var.get() == 1:
                    selected_days.append(weekdays[i])
            
            if not selected_days:
                messagebox.showwarning("입력 오류", "최소 하나 이상의 요일을 선택하세요.")
                return None
            
            return f"RRULE:FREQ=WEEKLY;BYDAY={','.join(selected_days)}"
        
        elif recur_type == "매월":
            monthly_type = self.monthly_type_var.get()
            
            if monthly_type == "날짜":
                day = self.monthly_day_var.get()
                return f"RRULE:FREQ=MONTHLY;BYMONTHDAY={day}"
            else:  # 요일
                week = self.monthly_week_var.get()
                weekday = self.monthly_weekday_var.get()
                
                # 주차 변환
                week_map = {"첫째": "1", "둘째": "2", "셋째": "3", "넷째": "4", "마지막": "-1"}
                week_num = week_map[week]
                
                # 요일 변환
                weekday_map = {
                    "월요일": "MO", "화요일": "TU", "수요일": "WE", "목요일": "TH",
                    "금요일": "FR", "토요일": "SA", "일요일": "SU"
                }
                weekday_code = weekday_map[weekday]
                
                return f"RRULE:FREQ=MONTHLY;BYDAY={week_num}{weekday_code}"
        
        elif recur_type == "매년":
            start_date = datetime.datetime.strptime(self.start_date_entry.get(), "%Y-%m-%d").date()
            return f"RRULE:FREQ=YEARLY;BYMONTH={start_date.month};BYMONTHDAY={start_date.day}"
    
    def add_recurring_meal(self):
        """반복 식단 추가"""
        # 시작 날짜 확인
        try:
            start_date_str = self.start_date_entry.get().strip()
            if not start_date_str:
                messagebox.showwarning("입력 오류", "시작 날짜를 입력하세요.")
                return
            
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("입력 오류", "올바른 날짜 형식이 아닙니다. YYYY-MM-DD 형식으로 입력하세요.")
            return
        
        # 종료 날짜 확인 (항상 필요)
        try:
            end_date_str = self.end_date_entry.get().strip()
            if not end_date_str:
                messagebox.showwarning("입력 오류", "종료 날짜를 입력하세요.")
                return
            
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            
            if end_date <= start_date:
                messagebox.showwarning("입력 오류", "종료 날짜는 시작 날짜보다 뒤여야 합니다.")
                return
        except ValueError:
            messagebox.showwarning("입력 오류", "올바른 날짜 형식이 아닙니다. YYYY-MM-DD 형식으로 입력하세요.")
            return
        
        # 반복 규칙 생성
        recurrence_rule = self.get_recurrence_rule()
        if not recurrence_rule:
            return  # 오류 메시지는 get_recurrence_rule에서 표시
        
        # 식단 정보 확인
        meal_plan = {}
        for meal_type, entry in self.meal_entries.items():
            meal_name = entry.get().strip()
            if meal_name:
                meal_plan[meal_type] = meal_name
        
        if not meal_plan:
            messagebox.showwarning("입력 오류", "최소 하나 이상의 식단 정보를 입력하세요.")
            return
        
        # 확인 메시지
        recur_type = self.recur_type_var.get()
        
        message = f"{start_date.strftime('%Y-%m-%d')}부터 {end_date.strftime('%Y-%m-%d')}까지 {recur_type} 반복으로\n"
        message += "다음 식단을 추가합니다:\n\n"
        
        for meal_type, meal_name in meal_plan.items():
            message += f"- {meal_type}: {meal_name}\n"
        
        confirm = messagebox.askyesno("확인", message + "\n추가하시겠습니까?")
        
        if confirm:
            # 메인 앱의 추가 스레드 호출
            self.main_app_methods['add_recurring_meal_thread'](start_date, recurrence_rule, meal_plan, end_date)
            
            # 템플릿 저장 여부 확인
            save_template = messagebox.askyesno("템플릿 저장", "이 식단을 템플릿으로 저장하시겠습니까?")
            if save_template:
                self.main_app_methods['save_as_template'](meal_plan)
