import customtkinter as ctk
import tkinter as tk
from datetime import date, timedelta
import datetime
from tkinter import messagebox
import threading

class ViewTab(ctk.CTkFrame):
    def __init__(self, master, planner_core, main_app_methods):
        super().__init__(master)
        self.planner_core = planner_core
        self.main_app_methods = main_app_methods
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_widgets()
    
    def create_widgets(self):
        # 메인 프레임
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        # 제목
        title_label = ctk.CTkLabel(main_frame, text="식단 조회", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=10)
        
        # 옵션 프레임
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # 조회 유형
        self.view_type_var = ctk.StringVar(value="기간별")
        view_type_label = ctk.CTkLabel(options_frame, text="조회 유형:")
        view_type_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        view_types = ["기간별", "특정 날짜", "오늘"]
        view_type_menu = ctk.CTkOptionMenu(options_frame, values=view_types, 
                                          variable=self.view_type_var,
                                          command=self.update_view_options)
        view_type_menu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # 옵션 프레임 (동적 변경됨)
        self.view_options_frame = ctk.CTkFrame(main_frame)
        self.view_options_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        # 초기 설정 - 기간별
        self.setup_period_options()
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        # 조회 버튼
        view_btn = ctk.CTkButton(button_frame, text="조회", command=self.view_meals)
        view_btn.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        
        # 결과 프레임
        result_frame = ctk.CTkFrame(main_frame)
        result_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(0, weight=1)
        
        # 결과 텍스트 위젯 (스크롤바 포함)
        self.result_text = ctk.CTkTextbox(result_frame, wrap="word")
        self.result_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.result_text.configure(state="disabled")
        
        # 결과 프레임이 늘어날 수 있도록 행 가중치 설정
        main_frame.grid_rowconfigure(4, weight=1)
    
    def setup_period_options(self):
        """기간별 조회 옵션 설정"""
        # 기존 옵션 프레임의 모든 위젯 제거
        for widget in self.view_options_frame.winfo_children():
            widget.destroy()
        
        # 기간 선택 프레임
        period_frame = ctk.CTkFrame(self.view_options_frame)
        period_frame.pack(padx=10, pady=10, fill="x")
        
        # 시작 날짜
        start_label = ctk.CTkLabel(period_frame, text="시작 날짜:")
        start_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.start_date_entry = ctk.CTkEntry(period_frame, width=150)
        self.start_date_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.start_date_entry.insert(0, (date.today() - timedelta(days=7)).strftime("%Y-%m-%d"))
        
        start_date_btn = ctk.CTkButton(period_frame, text="선택", width=40,
                                      command=lambda: self.main_app_methods['show_date_picker_view'](self.start_date_entry))
        start_date_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # 종료 날짜
        end_label = ctk.CTkLabel(period_frame, text="종료 날짜:")
        end_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.end_date_entry = ctk.CTkEntry(period_frame, width=150)
        self.end_date_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.end_date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        end_date_btn = ctk.CTkButton(period_frame, text="선택", width=40,
                                    command=lambda: self.main_app_methods['show_date_picker_view'](self.end_date_entry))
        end_date_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # 빠른 선택 프레임
        quick_frame = ctk.CTkFrame(self.view_options_frame)
        quick_frame.pack(padx=10, pady=5, fill="x")
        
        quick_label = ctk.CTkLabel(quick_frame, text="빠른 선택:")
        quick_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # 빠른 선택 버튼들
        today_btn = ctk.CTkButton(quick_frame, text="오늘", width=80,
                                 command=lambda: self.set_quick_period(0))
        today_btn.grid(row=0, column=1, padx=5, pady=5)
        
        week_btn = ctk.CTkButton(quick_frame, text="1주일", width=80,
                                command=lambda: self.set_quick_period(7))
        week_btn.grid(row=0, column=2, padx=5, pady=5)
        
        month_btn = ctk.CTkButton(quick_frame, text="1개월", width=80,
                                 command=lambda: self.set_quick_period(30))
        month_btn.grid(row=0, column=3, padx=5, pady=5)
        
        three_month_btn = ctk.CTkButton(quick_frame, text="3개월", width=80,
                                       command=lambda: self.set_quick_period(90))
        three_month_btn.grid(row=0, column=4, padx=5, pady=5)
    
    def setup_specific_date_options(self):
        """특정 날짜 조회 옵션 설정"""
        # 기존 옵션 프레임의 모든 위젯 제거
        for widget in self.view_options_frame.winfo_children():
            widget.destroy()
        
        # 날짜 선택 프레임
        date_frame = ctk.CTkFrame(self.view_options_frame)
        date_frame.pack(padx=10, pady=10, fill="x")
        
        date_label = ctk.CTkLabel(date_frame, text="날짜:")
        date_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.specific_date_entry = ctk.CTkEntry(date_frame, width=150)
        self.specific_date_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.specific_date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        date_btn = ctk.CTkButton(date_frame, text="선택", width=40,
                                command=lambda: self.main_app_methods['show_date_picker_view'](self.specific_date_entry))
        date_btn.grid(row=0, column=2, padx=5, pady=5)
    
    def setup_today_options(self):
        """오늘 조회 옵션 설정"""
        # 기존 옵션 프레임의 모든 위젯 제거
        for widget in self.view_options_frame.winfo_children():
            widget.destroy()
        
        # 간단한 설명만 표시
        today_label = ctk.CTkLabel(
            self.view_options_frame, 
            text=f"오늘 ({date.today().strftime('%Y-%m-%d')})의 식단을 조회합니다."
        )
        today_label.pack(pady=10)
    
    def update_view_options(self, event=None):
        """조회 유형에 따라 옵션 업데이트"""
        view_type = self.view_type_var.get()
        
        if view_type == "기간별":
            self.setup_period_options()
        elif view_type == "특정 날짜":
            self.setup_specific_date_options()
        else:  # 오늘
            self.setup_today_options()
    
    def set_quick_period(self, days):
        """빠른 기간 설정"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        self.end_date_entry.delete(0, "end")
        self.end_date_entry.insert(0, end_date.strftime("%Y-%m-%d"))
        
        self.start_date_entry.delete(0, "end")
        self.start_date_entry.insert(0, start_date.strftime("%Y-%m-%d"))
    
    def view_meals(self):
        """식단 조회"""
        view_type = self.view_type_var.get()
        
        # 조회 파라미터 설정
        if view_type == "기간별":
            try:
                start_date_str = self.start_date_entry.get().strip()
                end_date_str = self.end_date_entry.get().strip()
                
                if not start_date_str or not end_date_str:
                    messagebox.showwarning("입력 오류", "시작 날짜와 종료 날짜를 모두 입력하세요.")
                    return
                
                start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
                
                if start_date > end_date:
                    messagebox.showwarning("입력 오류", "종료 날짜는 시작 날짜보다 같거나 뒤여야 합니다.")
                    return
            except ValueError:
                messagebox.showwarning("입력 오류", "올바른 날짜 형식이 아닙니다. YYYY-MM-DD 형식으로 입력하세요.")
                return
        
        elif view_type == "특정 날짜":
            try:
                date_str = self.specific_date_entry.get().strip()
                
                if not date_str:
                    messagebox.showwarning("입력 오류", "날짜를 입력하세요.")
                    return
                
                specific_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                start_date = specific_date
                end_date = specific_date
            except ValueError:
                messagebox.showwarning("입력 오류", "올바른 날짜 형식이 아닙니다. YYYY-MM-DD 형식으로 입력하세요.")
                return
        
        else:  # 오늘
            start_date = date.today()
            end_date = start_date
        
        # 로딩 메시지 표시
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "식단 정보를 불러오는 중입니다...")
        self.result_text.configure(state="disabled")
        
        # 백그라운드 스레드에서 조회
        threading.Thread(target=self.fetch_data, args=(start_date, end_date)).start()
    
    def fetch_data(self, start_date, end_date):
        """백그라운드에서 데이터 조회"""
        events = self.planner_core.view_meal_plans(start_date, end_date)
        self.after(0, lambda: self.update_result_text(events, start_date, end_date))
    
    def update_result_text(self, events, start_date, end_date):
        """결과 텍스트 업데이트"""
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        
        # 제목 추가
        if start_date == end_date:
            self.result_text.insert("end", f"📅 {start_date.strftime('%Y년 %m월 %d일')} 식단 목록\n\n")
        else:
            self.result_text.insert("end", f"📅 {start_date.strftime('%Y년 %m월 %d일')} ~ {end_date.strftime('%Y년 %m월 %d일')} 식단 목록\n\n")
        
        if not events:
            self.result_text.insert("end", "조회된 식단이 없습니다.")
        else:
            # 결과를 날짜별로 정렬
            sorted_events = sorted(events, key=lambda e: e['start']['dateTime'])
            
            current_date = None
            
            for event in sorted_events:
                # 이벤트 시작 시간 파싱
                event_datetime = datetime.datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                event_date = event_datetime.date()
                
                # 새로운 날짜면 날짜 헤더 추가
                if current_date != event_date:
                    current_date = event_date
                    
                    weekday_kr = ["월", "화", "수", "목", "금", "토", "일"][current_date.weekday()]
                    date_header = f"\n🗓️ {current_date.strftime('%Y년 %m월 %d일')} ({weekday_kr})\n"
                    self.result_text.insert("end", date_header)
                    self.result_text.insert("end", "-" * 50 + "\n")
                
                # 식사 시간 추출
                meal_time = event['summary'].split(' - ')[0]
                
                # 식단 내용 추출
                meal_content = event['summary'].split(' - ')[1] if ' - ' in event['summary'] else event['summary']
                
                # 시간 형식 변환 (HH:MM)
                time_str = event_datetime.strftime("%H:%M")
                
                # 식단 정보 추가
                self.result_text.insert("end", f"⏰ {time_str} - [{meal_time}] {meal_content}\n")
        
        # 스크롤 맨 위로
        self.result_text.configure(state="disabled")
        self.result_text.see("1.0")
