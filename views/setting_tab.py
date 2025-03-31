import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import datetime

class SettingTab(ctk.CTkFrame):
    def __init__(self, master, planner_core, main_app_methods):
        super().__init__(master)
        self.planner_core = planner_core
        self.main_app_methods = main_app_methods
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_widgets()
    
    def create_widgets(self):
        # 메인 프레임
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        # 제목
        title_label = ctk.CTkLabel(main_frame, text="설정", font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, pady=(10, 20))
        
        # 식사 시간 설정
        meal_time_frame = ctk.CTkFrame(main_frame)
        meal_time_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        meal_time_label = ctk.CTkLabel(meal_time_frame, text="식사 시간 설정", font=("Arial", 16, "bold"))
        meal_time_label.grid(row=0, column=0, columnspan=3, pady=10, sticky="w")
        
        help_text = ctk.CTkLabel(meal_time_frame, text="식사 종류별 Google 캘린더 이벤트 시간을 설정합니다.")
        help_text.grid(row=1, column=0, columnspan=3, pady=5, sticky="w")
        
        # 식사 시간 입력 필드
        self.time_entries = {}
        
        for i, (meal_type, time_str) in enumerate(self.planner_core.meal_times.items(), start=2):
            hour, minute = map(int, time_str.split(':'))
            
            meal_label = ctk.CTkLabel(meal_time_frame, text=f"{meal_type}:", width=80, anchor="w")
            meal_label.grid(row=i, column=0, padx=10, pady=8, sticky="w")
            
            hour_var = tk.StringVar(value=str(hour).zfill(2))
            hour_menu = ctk.CTkOptionMenu(
                meal_time_frame, 
                values=[str(h).zfill(2) for h in range(24)],
                variable=hour_var,
                width=60
            )
            hour_menu.grid(row=i, column=1, padx=5, pady=8)
            
            colon_label = ctk.CTkLabel(meal_time_frame, text=":")
            colon_label.grid(row=i, column=2, pady=8)
            
            minute_var = tk.StringVar(value=str(minute).zfill(2))
            minute_menu = ctk.CTkOptionMenu(
                meal_time_frame, 
                values=[str(m).zfill(2) for m in range(0, 60, 5)],
                variable=minute_var,
                width=60
            )
            minute_menu.grid(row=i, column=3, padx=5, pady=8)
            
            self.time_entries[meal_type] = (hour_var, minute_var)
        
        # 저장 버튼
        save_time_btn = ctk.CTkButton(meal_time_frame, text="시간 설정 저장", 
                                     command=self.save_meal_times)
        save_time_btn.grid(row=len(self.planner_core.meal_times)+2, column=0, columnspan=4, 
                          padx=10, pady=15, sticky="ew")
        
        # 이벤트 설정
        event_frame = ctk.CTkFrame(main_frame)
        event_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        event_label = ctk.CTkLabel(event_frame, text="이벤트 설정", font=("Arial", 16, "bold"))
        event_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")
        
        # 이벤트 지속 시간
        duration_label = ctk.CTkLabel(event_frame, text="이벤트 지속 시간(분):")
        duration_label.grid(row=1, column=0, padx=10, pady=8, sticky="w")
        
        self.duration_var = tk.StringVar(value=str(self.planner_core.event_duration))
        duration_entry = ctk.CTkEntry(event_frame, width=100, textvariable=self.duration_var)
        duration_entry.grid(row=1, column=1, padx=10, pady=8, sticky="w")
        
        # 지속 시간 설명
        duration_desc = ctk.CTkLabel(event_frame, text="")
        duration_desc.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.update_duration_description(self.duration_var.get(), duration_desc)
        
        # 저장 버튼
        save_duration_btn = ctk.CTkButton(event_frame, text="지속 시간 저장", 
                                         command=lambda: self.save_event_duration(duration_entry, duration_desc))
        save_duration_btn.grid(row=3, column=0, columnspan=2, padx=10, pady=15, sticky="ew")
        
        # 테마 설정
        theme_frame = ctk.CTkFrame(main_frame)
        theme_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        theme_label = ctk.CTkLabel(theme_frame, text="테마 설정", font=("Arial", 16, "bold"))
        theme_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")
        
        # 현재 테마
        current_theme = self.main_app_methods['get_current_theme']()
        
        theme_type_label = ctk.CTkLabel(theme_frame, text="테마:")
        theme_type_label.grid(row=1, column=0, padx=10, pady=8, sticky="w")
        
        self.theme_var = ctk.StringVar(value=current_theme)
        themes = ["System", "Light", "Dark"]
        theme_menu = ctk.CTkOptionMenu(
            theme_frame, 
            values=themes,
            variable=self.theme_var,
            command=self.change_theme
        )
        theme_menu.grid(row=1, column=1, padx=10, pady=8, sticky="w")
        
        # 정보 프레임
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
        info_label = ctk.CTkLabel(info_frame, text="정보", font=("Arial", 16, "bold"))
        info_label.grid(row=0, column=0, pady=10, sticky="w")
        
        # 버전 정보
        version_label = ctk.CTkLabel(info_frame, text="식단 플래너 v1.0")
        version_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # 저작권 정보
        copyright_label = ctk.CTkLabel(info_frame, text="© 2023 Copyright")
        copyright_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        # 도움말 링크
        help_btn = ctk.CTkButton(info_frame, text="도움말", 
                              command=lambda: self.main_app_methods['open_url']("https://github.com/username/meal-planner"))
        help_btn.grid(row=3, column=0, padx=10, pady=10, sticky="w")
    
    def save_meal_times(self):
        """식사 시간 설정 저장"""
        new_meal_times = {}
        
        for meal_type, (hour_var, minute_var) in self.time_entries.items():
            try:
                hour = int(hour_var.get())
                minute = int(minute_var.get())
                
                if not (0 <= hour < 24 and 0 <= minute < 60):
                    messagebox.showwarning("입력 오류", f"{meal_type} 시간이 올바르지 않습니다.")
                    return
                
                time_str = f"{hour:02d}:{minute:02d}"
                new_meal_times[meal_type] = time_str
                
            except ValueError:
                messagebox.showwarning("입력 오류", f"{meal_type} 시간이 올바르지 않습니다.")
                return
        
        # 백엔드에 저장
        success = self.planner_core.update_meal_times(new_meal_times)
        
        if success:
            messagebox.showinfo("완료", "식사 시간 설정이 저장되었습니다.")
        else:
            messagebox.showerror("오류", "설정 저장에 실패했습니다.")
    
    def save_event_duration(self, duration_entry, label_widget):
        """이벤트 지속 시간 저장"""
        try:
            duration = int(duration_entry.get())
            
            if duration <= 0:
                messagebox.showwarning("입력 오류", "지속 시간은 양수여야 합니다.")
                return
            
            # 백엔드에 저장
            success = self.planner_core.update_event_duration(duration)
            
            if success:
                messagebox.showinfo("완료", "이벤트 지속 시간이 저장되었습니다.")
                self.update_duration_description(duration, label_widget)
            else:
                messagebox.showerror("오류", "설정 저장에 실패했습니다.")
                
        except ValueError:
            messagebox.showwarning("입력 오류", "올바른 숫자를 입력하세요.")
    
    def update_duration_description(self, duration_str, label_widget):
        """지속 시간 설명 업데이트"""
        try:
            duration = int(duration_str)
            
            if duration > 0:
                example_time = datetime.datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
                end_time = example_time + datetime.timedelta(minutes=duration)
                
                description = (f"예시: 점심 12:00에 식단 추가 시 "
                              f"12:00 ~ {end_time.strftime('%H:%M')} 일정으로 등록")
                label_widget.configure(text=description)
            else:
                label_widget.configure(text="")
                
        except ValueError:
            label_widget.configure(text="")
    
    def change_theme(self, theme_name):
        """테마 변경"""
        self.main_app_methods['change_theme'](theme_name)
