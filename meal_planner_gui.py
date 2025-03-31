import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
import datetime
import threading
import os
from datetime import date, timedelta
from meal_planner_core import MealPlanner

# 다크모드 설정
ctk.set_appearance_mode("System")  # 시스템 설정 따름 (다크/라이트)
ctk.set_default_color_theme("blue")  # 기본 색상 테마 (blue, dark-blue, green)

class MealPlannerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 윈도우 설정
        self.title("식단 플래너")
        self.geometry("900x600")
        self.minsize(800, 550)
        
        # 프레임 추가
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 백엔드 로직 초기화
        self.meal_planner = MealPlanner()
        self.initialize_meal_planner()
        
        # GUI 컴포넌트 초기화
        self.selected_date = date.today()
        self.selected_dates = []
        self.current_meal_plan = {}
        
        # UI 요소 생성
        self.create_ui()
        
    def initialize_meal_planner(self):
        """백엔드 MealPlanner 객체 초기화"""
        # 로딩 표시
        loading_window = ctk.CTkToplevel(self)
        loading_window.title("로딩 중")
        loading_window.geometry("300x100")
        loading_window.grab_set()  # 모달 창으로 설정
        
        loading_label = ctk.CTkLabel(loading_window, text="Google Calendar API 연결 중...", font=("Arial", 14))
        loading_label.pack(pady=20)
        
        # 백그라운드 스레드에서 초기화 진행
        def initialize_thread():
            success = self.meal_planner.initialize()
            loading_window.after(0, lambda: self.finish_initialization(loading_window, success))
        
        threading.Thread(target=initialize_thread).start()
        
    def finish_initialization(self, loading_window, success):
        """초기화 완료 후 처리"""
        loading_window.destroy()
        
        if not success:
            messagebox.showerror("오류", "Google Calendar API 연결에 실패했습니다.\n자격 증명을 확인하세요.")
            self.destroy()  # 앱 종료
        
    def create_ui(self):
        """메인 UI 생성"""
        # 탭뷰 생성
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # 탭 추가
        self.tabview.add("단일 날짜 식단")
        self.tabview.add("여러 날짜 식단")
        self.tabview.add("반복 식단")
        self.tabview.add("식단 조회")
        self.tabview.add("템플릿 관리")
        self.tabview.add("설정")
        
        # 각 탭 설정
        self.setup_single_date_tab()
        self.setup_multi_date_tab()
        self.setup_recurring_tab()
        self.setup_view_tab()
        self.setup_template_tab()
        self.setup_settings_tab()
    
    def setup_single_date_tab(self):
        """단일 날짜 식단 추가 탭 설정"""
        tab = self.tabview.tab("단일 날짜 식단")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # 왼쪽: 캘린더 프레임
        left_frame = ctk.CTkFrame(tab)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # 캘린더 타이틀
        calendar_title = ctk.CTkLabel(left_frame, text="날짜 선택", font=("Arial", 16, "bold"))
        calendar_title.pack(pady=10)
        
        # 캘린더 (기본 Tkinter Calendar 사용)
        cal_frame = tk.Frame(left_frame)
        cal_frame.pack(pady=10, fill="both", expand=True)
        
        self.calendar = Calendar(cal_frame, selectmode="day", date_pattern="yyyy-mm-dd")
        self.calendar.pack(fill="both", expand=True)
        self.calendar.bind("<<CalendarSelected>>", self.on_date_selected)
        
        # 오른쪽: 입력 프레임
        right_frame = ctk.CTkFrame(tab)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        
        # 입력 폼 타이틀
        form_title = ctk.CTkLabel(right_frame, text="식단 정보 입력", font=("Arial", 16, "bold"))
        form_title.grid(row=0, column=0, pady=10)
        
        # 선택된 날짜 표시
        self.selected_date_label = ctk.CTkLabel(right_frame, text=f"선택된 날짜: {self.selected_date.strftime('%Y-%m-%d')}")
        self.selected_date_label.grid(row=1, column=0, pady=5)
        
        # 식단 입력 프레임
        meal_frame = ctk.CTkFrame(right_frame)
        meal_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # 식단 입력 필드들
        self.meal_entries = {}
        
        for i, meal_type in enumerate(self.meal_planner.meal_times.keys()):
            meal_label = ctk.CTkLabel(meal_frame, text=f"{meal_type}:")
            meal_label.grid(row=i, column=0, padx=10, pady=10, sticky="w")
            
            meal_entry = ctk.CTkEntry(meal_frame, width=200)
            meal_entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            
            # 추천 버튼 (기록에서 가져오기)
            suggestion_btn = ctk.CTkButton(meal_frame, text="추천", width=60, 
                                          command=lambda t=meal_type: self.show_suggestions(t))
            suggestion_btn.grid(row=i, column=2, padx=5, pady=10)
            
            self.meal_entries[meal_type] = meal_entry
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(right_frame)
        button_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        # 템플릿 사용 버튼
        template_btn = ctk.CTkButton(button_frame, text="템플릿 사용", command=self.use_template)
        template_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # 식단 추가 버튼
        add_btn = ctk.CTkButton(button_frame, text="식단 추가", command=self.add_single_meal)
        add_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # 초기화 버튼
        clear_btn = ctk.CTkButton(button_frame, text="초기화", command=self.clear_entries)
        clear_btn.grid(row=0, column=2, padx=10, pady=10)
    
    def on_date_selected(self, event=None):
        """날짜 선택 이벤트 처리"""
        selected_date_str = self.calendar.get_date()
        self.selected_date = datetime.datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        self.selected_date_label.configure(text=f"선택된 날짜: {self.selected_date.strftime('%Y-%m-%d')}")
    
    def show_suggestions(self, meal_type):
        """특정 식사에 대한 추천 메뉴 표시"""
        history = self.meal_planner.load_menu_history()
        suggestions = history[meal_type]
        
        if not suggestions:
            messagebox.showinfo("추천 메뉴", "저장된 추천 메뉴가 없습니다.")
            return
        
        # 추천 메뉴 선택 창
        suggestion_window = ctk.CTkToplevel(self)
        suggestion_window.title(f"{meal_type} 추천 메뉴")
        suggestion_window.geometry("300x300")
        suggestion_window.grab_set()  # 모달 창으로 설정
        
        suggestion_label = ctk.CTkLabel(suggestion_window, text=f"{meal_type} 추천 메뉴", font=("Arial", 14, "bold"))
        suggestion_label.pack(pady=10)
        
        # 스크롤 가능한 프레임
        scroll_frame = ctk.CTkScrollableFrame(suggestion_window, width=250, height=200)
        scroll_frame.pack(pady=10, fill="both", expand=True)
        
        # 추천 메뉴 버튼
        for suggestion in suggestions:
            suggestion_btn = ctk.CTkButton(scroll_frame, text=suggestion, 
                                          command=lambda s=suggestion: self.select_suggestion(meal_type, s, suggestion_window))
            suggestion_btn.pack(pady=5, fill="x")
        
        # 취소 버튼
        cancel_btn = ctk.CTkButton(suggestion_window, text="취소", command=suggestion_window.destroy)
        cancel_btn.pack(pady=10)
    
    def select_suggestion(self, meal_type, suggestion, window):
        """추천 메뉴 선택"""
        self.meal_entries[meal_type].delete(0, "end")
        self.meal_entries[meal_type].insert(0, suggestion)
        window.destroy()
    
    def use_template(self):
        """템플릿 사용 기능"""
        templates = self.meal_planner.get_templates_list()
        
        if not templates:
            messagebox.showinfo("템플릿", "저장된 템플릿이 없습니다.")
            return
        
        # 템플릿 선택 창
        template_window = ctk.CTkToplevel(self)
        template_window.title("템플릿 선택")
        template_window.geometry("300x300")
        template_window.grab_set()  # 모달 창으로 설정
        
        template_label = ctk.CTkLabel(template_window, text="템플릿 선택", font=("Arial", 14, "bold"))
        template_label.pack(pady=10)
        
        # 스크롤 가능한 프레임
        scroll_frame = ctk.CTkScrollableFrame(template_window, width=250, height=200)
        scroll_frame.pack(pady=10, fill="both", expand=True)
        
        # 템플릿 버튼
        for template_name in templates:
            template_btn = ctk.CTkButton(scroll_frame, text=template_name, 
                                        command=lambda t=template_name: self.select_template(t, template_window))
            template_btn.pack(pady=5, fill="x")
        
        # 취소 버튼
        cancel_btn = ctk.CTkButton(template_window, text="취소", command=template_window.destroy)
        cancel_btn.pack(pady=10)
    
    def select_template(self, template_name, window):
        """템플릿 선택"""
        template = self.meal_planner.load_meal_template(template_name)
        
        if template:
            # 입력 창에 템플릿 내용 적용
            self.clear_entries()
            for meal_type, meal_name in template.items():
                if meal_type in self.meal_entries:
                    self.meal_entries[meal_type].insert(0, meal_name)
        
        window.destroy()
    
    def clear_entries(self):
        """입력창 초기화"""
        for entry in self.meal_entries.values():
            entry.delete(0, "end")
    
    def add_single_meal(self):
        """단일 날짜 식단 추가"""
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
            # 백그라운드 스레드에서 식단 추가
            threading.Thread(target=self.add_meal_thread, args=(self.selected_date, meal_plan)).start()
            
            # 템플릿 저장 여부 확인
            save_template = messagebox.askyesno("템플릿 저장", "이 식단을 템플릿으로 저장하시겠습니까?")
            
            if save_template:
                self.save_as_template(meal_plan)
    
    def add_meal_thread(self, date_obj, meal_plan):
        """백그라운드 스레드에서 식단 추가"""
        success = self.meal_planner.add_meal_plan(date_obj, meal_plan)
        
        # UI 업데이트는 메인 스레드에서 해야 함
        self.after(0, lambda: self.on_meal_add_complete(success))
    
    def on_meal_add_complete(self, success):
        """식단 추가 완료 처리"""
        if success:
            messagebox.showinfo("완료", "식단이 성공적으로 추가되었습니다.")
            self.clear_entries()
        else:
            messagebox.showerror("오류", "식단 추가 중 오류가 발생했습니다.")
    
    def save_as_template(self, meal_plan):
        """현재 식단을 템플릿으로 저장"""
        # 템플릿 이름 입력 창
        template_window = ctk.CTkToplevel(self)
        template_window.title("템플릿 저장")
        template_window.geometry("300x150")
        template_window.grab_set()  # 모달 창으로 설정
        
        # 입력 프레임
        input_frame = ctk.CTkFrame(template_window)
        input_frame.pack(pady=10, fill="both", expand=True, padx=10)
        
        # 템플릿 이름 입력
        name_label = ctk.CTkLabel(input_frame, text="템플릿 이름:")
        name_label.pack(pady=5, anchor="w")
        
        name_entry = ctk.CTkEntry(input_frame, width=250)
        name_entry.pack(pady=5, fill="x")
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(template_window)
        button_frame.pack(pady=10, fill="x", padx=10)
        
        # 저장 및 취소 버튼
        save_btn = ctk.CTkButton(button_frame, text="저장", 
                                 command=lambda: self.save_template_with_name(name_entry.get(), meal_plan, template_window))
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = ctk.CTkButton(button_frame, text="취소", command=template_window.destroy)
        cancel_btn.pack(side="right", padx=5)
    
    def save_template_with_name(self, template_name, meal_plan, window):
        """템플릿 저장 처리"""
        if not template_name.strip():
            messagebox.showwarning("입력 오류", "템플릿 이름을 입력하세요.", parent=window)
            return
        
        success = self.meal_planner.save_meal_template(template_name, meal_plan)
        
        if success:
            messagebox.showinfo("완료", f"'{template_name}' 템플릿이 저장되었습니다.")
            window.destroy()
    
    def setup_multi_date_tab(self):
        """여러 날짜 식단 추가 탭 설정"""
        tab = self.tabview.tab("여러 날짜 식단")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # 상단 프레임: 날짜 선택
        date_frame = ctk.CTkFrame(tab)
        date_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        date_frame.grid_columnconfigure(0, weight=1)
        
        date_title = ctk.CTkLabel(date_frame, text="여러 날짜 선택", font=("Arial", 16, "bold"))
        date_title.grid(row=0, column=0, pady=10)
        
        # 날짜 선택 옵션
        option_frame = ctk.CTkFrame(date_frame)
        option_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # 라디오 버튼으로 날짜 선택 방식 선택
        self.date_selection_var = ctk.StringVar(value="range")
        
        range_radio = ctk.CTkRadioButton(option_frame, text="날짜 범위 선택", 
                                        variable=self.date_selection_var, value="range")
        range_radio.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        individual_radio = ctk.CTkRadioButton(option_frame, text="개별 날짜 선택", 
                                            variable=self.date_selection_var, value="individual")
        individual_radio.grid(row=0, column=1, padx=20, pady=10, sticky="w")
        
        # 날짜 범위 선택 프레임
        range_select_frame = ctk.CTkFrame(date_frame)
        range_select_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        start_label = ctk.CTkLabel(range_select_frame, text="시작 날짜:")
        start_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.start_date_entry = ctk.CTkEntry(range_select_frame, width=100)
        self.start_date_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.start_date_entry.insert(0, self.selected_date.strftime('%Y-%m-%d'))
        
        start_date_btn = ctk.CTkButton(range_select_frame, text="선택", width=60,
                                    command=lambda: self.show_date_picker(self.start_date_entry))
        start_date_btn.grid(row=0, column=2, padx=5, pady=10)
        
        end_label = ctk.CTkLabel(range_select_frame, text="종료 날짜:")
        end_label.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        self.end_date_entry = ctk.CTkEntry(range_select_frame, width=100)
        self.end_date_entry.grid(row=0, column=4, padx=10, pady=10, sticky="w")
        tomorrow = self.selected_date + datetime.timedelta(days=1)
        self.end_date_entry.insert(0, tomorrow.strftime('%Y-%m-%d'))
        
        end_date_btn = ctk.CTkButton(range_select_frame, text="선택", width=60,
                                    command=lambda: self.show_date_picker(self.end_date_entry))
        end_date_btn.grid(row=0, column=5, padx=5, pady=10)
        
        # 개별 날짜 선택 프레임
        individual_frame = ctk.CTkFrame(date_frame)
        individual_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        add_date_btn = ctk.CTkButton(individual_frame, text="날짜 추가", 
                                    command=self.add_individual_date)
        add_date_btn.grid(row=0, column=0, padx=10, pady=10)
        
        remove_date_btn = ctk.CTkButton(individual_frame, text="날짜 제거", 
                                    command=self.remove_individual_date)
        remove_date_btn.grid(row=0, column=1, padx=10, pady=10)
        
        clear_dates_btn = ctk.CTkButton(individual_frame, text="모두 지우기", 
                                    command=self.clear_individual_dates)
        clear_dates_btn.grid(row=0, column=2, padx=10, pady=10)
        
        # 선택된 날짜 목록 (리스트박스)
        dates_label = ctk.CTkLabel(individual_frame, text="선택된 날짜:")
        dates_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        dates_frame = ctk.CTkFrame(individual_frame)
        dates_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        
        # Tkinter Listbox 사용 (CTk는 리스트박스 없음)
        self.dates_listbox = tk.Listbox(dates_frame, height=5, width=30)
        self.dates_listbox.pack(side="left", fill="both", expand=True)
        
        # 스크롤바 추가
        scrollbar = tk.Scrollbar(dates_frame, orient="vertical")
        scrollbar.config(command=self.dates_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.dates_listbox.config(yscrollcommand=scrollbar.set)
        
        # 하단 프레임: 식단 입력
        meal_input_frame = ctk.CTkFrame(tab)
        meal_input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="new")
        
        meal_title = ctk.CTkLabel(meal_input_frame, text="식단 정보 입력", font=("Arial", 16, "bold"))
        meal_title.grid(row=0, column=0, pady=10)
        
        # 식단 입력 필드들
        multi_meal_frame = ctk.CTkFrame(meal_input_frame)
        multi_meal_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.multi_meal_entries = {}
        
        for i, meal_type in enumerate(self.meal_planner.meal_times.keys()):
            meal_label = ctk.CTkLabel(multi_meal_frame, text=f"{meal_type}:")
            meal_label.grid(row=i, column=0, padx=10, pady=10, sticky="w")
            
            meal_entry = ctk.CTkEntry(multi_meal_frame, width=200)
            meal_entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            
            # 추천 버튼 (기록에서 가져오기)
            suggestion_btn = ctk.CTkButton(multi_meal_frame, text="추천", width=60, 
                                        command=lambda t=meal_type: self.show_multi_suggestions(t))
            suggestion_btn.grid(row=i, column=2, padx=5, pady=10)
            
            self.multi_meal_entries[meal_type] = meal_entry
        
        # 버튼 프레임
        multi_button_frame = ctk.CTkFrame(meal_input_frame)
        multi_button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # 템플릿 사용 버튼
        multi_template_btn = ctk.CTkButton(multi_button_frame, text="템플릿 사용", 
                                        command=self.use_multi_template)
        multi_template_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # 식단 추가 버튼
        multi_add_btn = ctk.CTkButton(multi_button_frame, text="식단 추가", 
                                    command=self.add_multi_meal)
        multi_add_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # 초기화 버튼
        multi_clear_btn = ctk.CTkButton(multi_button_frame, text="초기화", 
                                    command=self.clear_multi_entries)
        multi_clear_btn.grid(row=0, column=2, padx=10, pady=10)

    def show_date_picker(self, entry_widget):
        """날짜 선택기 표시"""
        date_picker = ctk.CTkToplevel(self)
        date_picker.title("날짜 선택")
        date_picker.geometry("300x300")
        date_picker.grab_set()  # 모달 창으로 설정
        
        # 현재 입력된 날짜 또는 오늘 날짜
        try:
            current_date = datetime.datetime.strptime(entry_widget.get(), "%Y-%m-%d").date()
        except:
            current_date = datetime.date.today()
        
        # 캘린더 프레임
        cal_frame = tk.Frame(date_picker)
        cal_frame.pack(pady=10)
        
        cal = Calendar(cal_frame, selectmode="day", year=current_date.year, 
                    month=current_date.month, day=current_date.day, date_pattern="yyyy-mm-dd")
        cal.pack()
        
        # 선택 버튼
        select_btn = ctk.CTkButton(date_picker, text="선택", 
                                command=lambda: self.select_date_from_picker(cal, entry_widget, date_picker))
        select_btn.pack(pady=10)

    def select_date_from_picker(self, cal, entry_widget, window):
        """날짜 선택기에서 날짜 선택"""
        selected_date = cal.get_date()
        entry_widget.delete(0, "end")
        entry_widget.insert(0, selected_date)
        window.destroy()

    def add_individual_date(self):
        """개별 날짜 추가"""
        date_picker = ctk.CTkToplevel(self)
        date_picker.title("날짜 추가")
        date_picker.geometry("300x300")
        date_picker.grab_set()  # 모달 창으로 설정
        
        # 캘린더 프레임
        cal_frame = tk.Frame(date_picker)
        cal_frame.pack(pady=10)
        
        cal = Calendar(cal_frame, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack()
        
        # 선택 버튼
        select_btn = ctk.CTkButton(date_picker, text="추가", 
                                command=lambda: self.add_date_to_list(cal, date_picker))
        select_btn.pack(pady=10)

    def add_date_to_list(self, cal, window):
        """선택한 날짜를 목록에 추가"""
        selected_date_str = cal.get_date()
        
        # 이미 있는 날짜인지 확인
        for i in range(self.dates_listbox.size()):
            if self.dates_listbox.get(i) == selected_date_str:
                messagebox.showinfo("알림", "이미 선택된 날짜입니다.", parent=window)
                return
        
        # 날짜 목록에 추가
        self.dates_listbox.insert("end", selected_date_str)
        window.destroy()

    def remove_individual_date(self):
        """선택한 날짜 제거"""
        selected_indices = self.dates_listbox.curselection()
        
        if not selected_indices:
            messagebox.showinfo("알림", "제거할 날짜를 선택하세요.")
            return
        
        # 역순으로 제거 (인덱스 변화 방지)
        for i in sorted(selected_indices, reverse=True):
            self.dates_listbox.delete(i)

    def clear_individual_dates(self):
        """날짜 목록 모두 지우기"""
        self.dates_listbox.delete(0, "end")

    def show_multi_suggestions(self, meal_type):
        """여러 날짜 탭에서 추천 메뉴 표시"""
        # 단일 날짜 탭과 동일한 로직 사용
        self.show_suggestions(meal_type)
        
        # 다른 이름의 메소드로 구현했다면 수정 필요
        # (예: 단일 날짜 탭의 show_suggestions 메소드 참조)

    def use_multi_template(self):
        """여러 날짜 탭에서 템플릿 사용"""
        templates = self.meal_planner.get_templates_list()
        
        if not templates:
            messagebox.showinfo("템플릿", "저장된 템플릿이 없습니다.")
            return
        
        # 템플릿 선택 창
        template_window = ctk.CTkToplevel(self)
        template_window.title("템플릿 선택")
        template_window.geometry("300x300")
        template_window.grab_set()  # 모달 창으로 설정
        
        template_label = ctk.CTkLabel(template_window, text="템플릿 선택", font=("Arial", 14, "bold"))
        template_label.pack(pady=10)
        
        # 스크롤 가능한 프레임
        scroll_frame = ctk.CTkScrollableFrame(template_window, width=250, height=200)
        scroll_frame.pack(pady=10, fill="both", expand=True)
        
        # 템플릿 버튼
        for template_name in templates:
            template_btn = ctk.CTkButton(scroll_frame, text=template_name, 
                                        command=lambda t=template_name: self.select_multi_template(t, template_window))
            template_btn.pack(pady=5, fill="x")
        
        # 취소 버튼
        cancel_btn = ctk.CTkButton(template_window, text="취소", command=template_window.destroy)
        cancel_btn.pack(pady=10)

    def select_multi_template(self, template_name, window):
        """여러 날짜 탭에서 템플릿 선택"""
        template = self.meal_planner.load_meal_template(template_name)
        
        if template:
            # 입력 창에 템플릿 내용 적용
            self.clear_multi_entries()
            for meal_type, meal_name in template.items():
                if meal_type in self.multi_meal_entries:
                    self.multi_meal_entries[meal_type].insert(0, meal_name)
        
        window.destroy()

    def clear_multi_entries(self):
        """여러 날짜 탭의 입력창 초기화"""
        for entry in self.multi_meal_entries.values():
            entry.delete(0, "end")

    def add_multi_meal(self):
        """여러 날짜 식단 추가"""
        meal_plan = {}
        
        # 식단 정보 가져오기
        for meal_type, entry in self.multi_meal_entries.items():
            meal_name = entry.get().strip()
            if meal_name:
                meal_plan[meal_type] = meal_name
        
        if not meal_plan:
            messagebox.showwarning("입력 오류", "최소 하나 이상의 식단 정보를 입력하세요.")
            return
        
        # 날짜 정보 가져오기
        selected_dates = []
        
        if self.date_selection_var.get() == "range":
            # 날짜 범위
            try:
                start_date = datetime.datetime.strptime(self.start_date_entry.get(), "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(self.end_date_entry.get(), "%Y-%m-%d").date()
                
                if end_date < start_date:
                    messagebox.showwarning("입력 오류", "종료 날짜는 시작 날짜 이후여야 합니다.")
                    return
                
                # 날짜 범위 생성
                current_date = start_date
                while current_date <= end_date:
                    selected_dates.append(current_date)
                    current_date += datetime.timedelta(days=1)
                    
            except ValueError:
                messagebox.showwarning("입력 오류", "유효한 날짜 형식이 아닙니다. (YYYY-MM-DD)")
                return
        else:
            # 개별 날짜
            for i in range(self.dates_listbox.size()):
                date_str = self.dates_listbox.get(i)
                try:
                    date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    selected_dates.append(date_obj)
                except ValueError:
                    continue
        
        if not selected_dates:
            messagebox.showwarning("입력 오류", "최소 하나 이상의 날짜를 선택해야 합니다.")
            return
        
        # 확인 메시지
        dates_str = ", ".join([d.strftime("%Y-%m-%d") for d in selected_dates[:5]])
        if len(selected_dates) > 5:
            dates_str += f" 외 {len(selected_dates) - 5}일"
        
        message = f"다음 날짜에 식단을 추가합니다:\n{dates_str}\n\n"
        message += "다음 메뉴로 추가합니다:\n"
        for meal_type, meal_name in meal_plan.items():
            message += f"- {meal_type}: {meal_name}\n"
        
        confirm = messagebox.askyesno("확인", message + f"\n총 {len(selected_dates)}일의 식단을 추가하시겠습니까?")
        
        if confirm:
            # 백그라운드 스레드에서 식단 추가
            threading.Thread(target=self.add_multi_meal_thread, args=(selected_dates, meal_plan)).start()

    def add_multi_meal_thread(self, dates, meal_plan):
        """백그라운드 스레드에서 여러 날짜 식단 추가"""
        success = self.meal_planner.add_meal_plan_multiple_dates(dates, meal_plan)
        
        # UI 업데이트는 메인 스레드에서 해야 함
        self.after(0, lambda: self.on_multi_meal_add_complete(success, len(dates)))

    def on_multi_meal_add_complete(self, success, count):
        """여러 날짜 식단 추가 완료 처리"""
        if success:
            messagebox.showinfo("완료", f"{count}일 분량의 식단이 성공적으로 추가되었습니다.")
            self.clear_multi_entries()
            
            # 날짜 선택 초기화
            if self.date_selection_var.get() == "individual":
                self.clear_individual_dates()
                
        else:
            messagebox.showerror("오류", "식단 추가 중 오류가 발생했습니다.") 
        
    def setup_recurring_tab(self):
        """반복 식단 일정 추가 탭 설정"""
        tab = self.tabview.tab("반복 식단")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # 상단 프레임: 반복 설정
        recur_frame = ctk.CTkFrame(tab)
        recur_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        recur_frame.grid_columnconfigure(0, weight=1)
        
        recur_title = ctk.CTkLabel(recur_frame, text="반복 식단 설정", font=("Arial", 16, "bold"))
        recur_title.grid(row=0, column=0, pady=10)
        
        # 시작 날짜 선택
        start_date_frame = ctk.CTkFrame(recur_frame)
        start_date_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        start_date_label = ctk.CTkLabel(start_date_frame, text="시작 날짜:")
        start_date_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.recur_start_date_entry = ctk.CTkEntry(start_date_frame, width=100)
        self.recur_start_date_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.recur_start_date_entry.insert(0, self.selected_date.strftime('%Y-%m-%d'))
        
        start_date_btn = ctk.CTkButton(start_date_frame, text="선택", width=60,
                                    command=lambda: self.show_date_picker(self.recur_start_date_entry))
        start_date_btn.grid(row=0, column=2, padx=5, pady=10)
        
        # 반복 패턴 선택
        pattern_frame = ctk.CTkFrame(recur_frame)
        pattern_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        pattern_label = ctk.CTkLabel(pattern_frame, text="반복 패턴:")
        pattern_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.recur_pattern_var = ctk.StringVar(value="daily")
        
        daily_radio = ctk.CTkRadioButton(pattern_frame, text="매일", 
                                        variable=self.recur_pattern_var, value="daily",
                                        command=self.update_recur_options)
        daily_radio.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        weekly_radio = ctk.CTkRadioButton(pattern_frame, text="매주", 
                                        variable=self.recur_pattern_var, value="weekly",
                                        command=self.update_recur_options)
        weekly_radio.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        monthly_radio = ctk.CTkRadioButton(pattern_frame, text="매월", 
                                        variable=self.recur_pattern_var, value="monthly",
                                        command=self.update_recur_options)
        monthly_radio.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        # 요일 선택 프레임 (매주 패턴용)
        self.weekday_frame = ctk.CTkFrame(recur_frame)
        self.weekday_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.weekday_frame.grid_columnconfigure(0, weight=1)
        
        weekday_label = ctk.CTkLabel(self.weekday_frame, text="요일 선택:")
        weekday_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # 요일 체크박스
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        self.weekday_vars = {}
        
        for i, day in enumerate(weekdays):
            var = ctk.BooleanVar(value=False)
            checkbox = ctk.CTkCheckBox(self.weekday_frame, text=day, variable=var, 
                                    onvalue=True, offvalue=False)
            checkbox.grid(row=0, column=i+1, padx=5, pady=5, sticky="w")
            self.weekday_vars[day] = var
        
        # 종료 설정 프레임
        end_frame = ctk.CTkFrame(recur_frame)
        end_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
        end_label = ctk.CTkLabel(end_frame, text="종료 설정:")
        end_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.end_type_var = ctk.StringVar(value="never")
        
        never_radio = ctk.CTkRadioButton(end_frame, text="종료 없음", 
                                        variable=self.end_type_var, value="never",
                                        command=self.update_end_options)
        never_radio.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        count_radio = ctk.CTkRadioButton(end_frame, text="반복 횟수", 
                                        variable=self.end_type_var, value="count",
                                        command=self.update_end_options)
        count_radio.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        until_radio = ctk.CTkRadioButton(end_frame, text="종료 날짜", 
                                        variable=self.end_type_var, value="until",
                                        command=self.update_end_options)
        until_radio.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        
        # 반복 횟수 입력
        self.count_frame = ctk.CTkFrame(recur_frame)
        self.count_frame.grid(row=5, column=0, padx=10, pady=10, sticky="ew")
        
        count_label = ctk.CTkLabel(self.count_frame, text="반복 횟수:")
        count_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.count_entry = ctk.CTkEntry(self.count_frame, width=80)
        self.count_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.count_entry.insert(0, "10")
        
        # 종료 날짜 입력
        self.until_frame = ctk.CTkFrame(recur_frame)
        self.until_frame.grid(row=6, column=0, padx=10, pady=10, sticky="ew")
        
        until_label = ctk.CTkLabel(self.until_frame, text="종료 날짜:")
        until_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.until_entry = ctk.CTkEntry(self.until_frame, width=100)
        self.until_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        next_month = self.selected_date.replace(month=self.selected_date.month+1 if self.selected_date.month < 12 else 1,
                                            year=self.selected_date.year if self.selected_date.month < 12 else self.selected_date.year+1)
        self.until_entry.insert(0, next_month.strftime('%Y-%m-%d'))
        
        until_btn = ctk.CTkButton(self.until_frame, text="선택", width=60,
                                command=lambda: self.show_date_picker(self.until_entry))
        until_btn.grid(row=0, column=2, padx=5, pady=10)
        
        # 초기 상태 설정
        self.update_recur_options()
        self.update_end_options()
        
        # 하단 프레임: 식단 입력
        recur_meal_frame = ctk.CTkFrame(tab)
        recur_meal_frame.grid(row=1, column=0, padx=10, pady=10, sticky="new")
        
        meal_title = ctk.CTkLabel(recur_meal_frame, text="식단 정보 입력", font=("Arial", 16, "bold"))
        meal_title.grid(row=0, column=0, pady=10)
        
        # 식단 입력 필드들
        recur_input_frame = ctk.CTkFrame(recur_meal_frame)
        recur_input_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.recur_meal_entries = {}
        
        for i, meal_type in enumerate(self.meal_planner.meal_times.keys()):
            meal_label = ctk.CTkLabel(recur_input_frame, text=f"{meal_type}:")
            meal_label.grid(row=i, column=0, padx=10, pady=10, sticky="w")
            
            meal_entry = ctk.CTkEntry(recur_input_frame, width=200)
            meal_entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            
            # 추천 버튼 (기록에서 가져오기)
            suggestion_btn = ctk.CTkButton(recur_input_frame, text="추천", width=60, 
                                        command=lambda t=meal_type: self.show_recur_suggestions(t))
            suggestion_btn.grid(row=i, column=2, padx=5, pady=10)
            
            self.recur_meal_entries[meal_type] = meal_entry
        
        # 버튼 프레임
        recur_button_frame = ctk.CTkFrame(recur_meal_frame)
        recur_button_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        # 템플릿 사용 버튼
        recur_template_btn = ctk.CTkButton(recur_button_frame, text="템플릿 사용", 
                                        command=self.use_recur_template)
        recur_template_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # 식단 추가 버튼
        recur_add_btn = ctk.CTkButton(recur_button_frame, text="반복 일정 추가", 
                                    command=self.add_recurring_meal)
        recur_add_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # 초기화 버튼
        recur_clear_btn = ctk.CTkButton(recur_button_frame, text="초기화", 
                                    command=self.clear_recur_entries)
        recur_clear_btn.grid(row=0, column=2, padx=10, pady=10)

    def update_recur_options(self):
        """반복 패턴에 따른 UI 업데이트"""
        pattern = self.recur_pattern_var.get()
        
        if pattern == "weekly":
            self.weekday_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        else:
            self.weekday_frame.grid_forget()

    def update_end_options(self):
        """종료 설정에 따른 UI 업데이트"""
        end_type = self.end_type_var.get()
        
        if end_type == "count":
            self.count_frame.grid(row=5, column=0, padx=10, pady=10, sticky="ew")
            self.until_frame.grid_forget()
        elif end_type == "until":
            self.count_frame.grid_forget()
            self.until_frame.grid(row=6, column=0, padx=10, pady=10, sticky="ew")
        else:  # "never"
            self.count_frame.grid_forget()
            self.until_frame.grid_forget()

    def show_recur_suggestions(self, meal_type):
        """반복 식단 탭에서 추천 메뉴 표시"""
        # 단일 날짜 탭과 동일한 로직 사용
        self.show_suggestions(meal_type)

    def use_recur_template(self):
        """반복 식단 탭에서 템플릿 사용"""
        templates = self.meal_planner.get_templates_list()
        
        if not templates:
            messagebox.showinfo("템플릿", "저장된 템플릿이 없습니다.")
            return
        
        # 템플릿 선택 창
        template_window = ctk.CTkToplevel(self)
        template_window.title("템플릿 선택")
        template_window.geometry("300x300")
        template_window.grab_set()  # 모달 창으로 설정
        
        template_label = ctk.CTkLabel(template_window, text="템플릿 선택", font=("Arial", 14, "bold"))
        template_label.pack(pady=10)
        
        # 스크롤 가능한 프레임
        scroll_frame = ctk.CTkScrollableFrame(template_window, width=250, height=200)
        scroll_frame.pack(pady=10, fill="both", expand=True)
        
        # 템플릿 버튼
        for template_name in templates:
            template_btn = ctk.CTkButton(scroll_frame, text=template_name, 
                                        command=lambda t=template_name: self.select_recur_template(t, template_window))
            template_btn.pack(pady=5, fill="x")
        
        # 취소 버튼
        cancel_btn = ctk.CTkButton(template_window, text="취소", command=template_window.destroy)
        cancel_btn.pack(pady=10)

    def select_recur_template(self, template_name, window):
        """반복 식단 탭에서 템플릿 선택"""
        template = self.meal_planner.load_meal_template(template_name)
        
        if template:
            # 입력 창에 템플릿 내용 적용
            self.clear_recur_entries()
            for meal_type, meal_name in template.items():
                if meal_type in self.recur_meal_entries:
                    self.recur_meal_entries[meal_type].insert(0, meal_name)
        
        window.destroy()

    def clear_recur_entries(self):
        """반복 식단 탭의 입력창 초기화"""
        for entry in self.recur_meal_entries.values():
            entry.delete(0, "end")

    def add_recurring_meal(self):
        """반복 식단 일정 추가"""
        meal_plan = {}
        
        # 식단 정보 가져오기
        for meal_type, entry in self.recur_meal_entries.items():
            meal_name = entry.get().strip()
            if meal_name:
                meal_plan[meal_type] = meal_name
        
        if not meal_plan:
            messagebox.showwarning("입력 오류", "최소 하나 이상의 식단 정보를 입력하세요.")
            return
        
        # 시작 날짜 가져오기
        try:
            start_date = datetime.datetime.strptime(self.recur_start_date_entry.get(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("입력 오류", "유효한 시작 날짜 형식이 아닙니다. (YYYY-MM-DD)")
            return
        
        # 반복 패턴 생성
        pattern = self.recur_pattern_var.get()
        recurrence_rule = ""
        
        if pattern == "daily":
            recurrence_rule = "FREQ=DAILY"
        elif pattern == "weekly":
            # 선택된 요일 가져오기
            days_map = {"월": "MO", "화": "TU", "수": "WE", "목": "TH", "금": "FR", "토": "SA", "일": "SU"}
            selected_days = []
            
            for day, var in self.weekday_vars.items():
                if var.get():
                    selected_days.append(days_map[day])
            
            if not selected_days:
                messagebox.showwarning("입력 오류", "최소 하나 이상의 요일을 선택해야 합니다.")
                return
            
            recurrence_rule = f"FREQ=WEEKLY;BYDAY={','.join(selected_days)}"
        elif pattern == "monthly":
            # 같은 날짜에 매월 반복
            day_of_month = start_date.day
            recurrence_rule = f"FREQ=MONTHLY;BYMONTHDAY={day_of_month}"
        
        # 종료 조건 추가
        end_date = None
        end_type = self.end_type_var.get()
        
        if end_type == "count":
            try:
                count = int(self.count_entry.get())
                if count <= 0:
                    messagebox.showwarning("입력 오류", "반복 횟수는 양수여야 합니다.")
                    return
                recurrence_rule += f";COUNT={count}"
            except ValueError:
                messagebox.showwarning("입력 오류", "올바른 반복 횟수를 입력하세요.")
                return
        elif end_type == "until":
            try:
                end_date = datetime.datetime.strptime(self.until_entry.get(), "%Y-%m-%d").date()
                if end_date <= start_date:
                    messagebox.showwarning("입력 오류", "종료 날짜는 시작 날짜 이후여야 합니다.")
                    return
            except ValueError:
                messagebox.showwarning("입력 오류", "유효한 종료 날짜 형식이 아닙니다. (YYYY-MM-DD)")
                return
        
        # 확인 메시지
        message = f"다음 설정으로 반복 식단을 추가합니다:\n\n"
        message += f"시작 날짜: {start_date.strftime('%Y-%m-%d')}\n"
        
        if pattern == "daily":
            message += "반복: 매일\n"
        elif pattern == "weekly":
            days_korean = [day for day, var in self.weekday_vars.items() if var.get()]
            message += f"반복: 매주 {', '.join(days_korean)}요일\n"
        elif pattern == "monthly":
            message += f"반복: 매월 {start_date.day}일\n"
        
        if end_type == "count":
            message += f"종료: {self.count_entry.get()}회 반복 후\n"
        elif end_type == "until":
            message += f"종료: {end_date.strftime('%Y-%m-%d')}까지\n"
        else:
            message += "종료: 없음 (무기한)\n"
        
        message += "\n다음 메뉴로 추가합니다:\n"
        for meal_type, meal_name in meal_plan.items():
            message += f"- {meal_type}: {meal_name}\n"
        
        confirm = messagebox.askyesno("확인", message + "\n반복 일정을 추가하시겠습니까?")
        
        if confirm:
            # 백그라운드 스레드에서 식단 추가
            threading.Thread(target=self.add_recurring_meal_thread, 
                            args=(start_date, recurrence_rule, meal_plan, end_date)).start()

    def add_recurring_meal_thread(self, start_date, recurrence_rule, meal_plan, end_date):
        """백그라운드 스레드에서 반복 식단 추가"""
        success = self.meal_planner.add_recurring_meal_plan(start_date, recurrence_rule, meal_plan, end_date)
        
        # UI 업데이트는 메인 스레드에서 해야 함
        self.after(0, lambda: self.on_recurring_meal_add_complete(success))

    def on_recurring_meal_add_complete(self, success):
        """반복 식단 추가 완료 처리"""
        if success:
            messagebox.showinfo("완료", "반복 식단 일정이 성공적으로 추가되었습니다.")
            self.clear_recur_entries()
        else:
            messagebox.showerror("오류", "반복 식단 일정 추가 중 오류가 발생했습니다.") 
    
    def setup_view_tab(self):
        """식단 조회 탭 설정"""
        tab = self.tabview.tab("식단 조회")
        
        import tkinter as tk
        import datetime
        from tkcalendar import Calendar
        
        # 상단 프레임 (날짜 선택)
        date_frame = ctk.CTkFrame(tab)
        date_frame.pack(fill="x", padx=10, pady=10)
        
        # 날짜 선택 옵션
        ctk.CTkLabel(date_frame, text="조회 방법:").pack(side=tk.LEFT, padx=10)
        
        self.view_type_var = tk.StringVar(value="date")
        single_radio = ctk.CTkRadioButton(date_frame, text="특정 날짜", variable=self.view_type_var, value="date", 
                                        command=self.update_view_options)
        single_radio.pack(side=tk.LEFT, padx=10)
        
        range_radio = ctk.CTkRadioButton(date_frame, text="기간", variable=self.view_type_var, value="range", 
                                        command=self.update_view_options)
        range_radio.pack(side=tk.LEFT, padx=10)
        
        # 날짜 선택 프레임
        self.date_select_frame = ctk.CTkFrame(tab)
        self.date_select_frame.pack(fill="x", padx=10, pady=5)
        
        # 단일 날짜 선택 (기본)
        self.single_date_frame = ctk.CTkFrame(self.date_select_frame)
        self.single_date_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(self.single_date_frame, text="날짜 선택:").pack(side=tk.LEFT, padx=10)
        
        self.single_date_entry = ctk.CTkEntry(self.single_date_frame, width=100)
        self.single_date_entry.pack(side=tk.LEFT, padx=10)
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.single_date_entry.insert(0, today)
        
        date_btn = ctk.CTkButton(self.single_date_frame, text="선택", 
                                command=lambda: self.show_date_picker_view(self.single_date_entry))
        date_btn.pack(side=tk.LEFT, padx=10)
        
        # 날짜 범위 선택 (숨김 상태로 시작)
        self.range_date_frame = ctk.CTkFrame(self.date_select_frame)
        
        # 시작 날짜
        start_frame = ctk.CTkFrame(self.range_date_frame)
        start_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(start_frame, text="시작 날짜:").pack(side=tk.LEFT, padx=10)
        
        self.start_date_entry = ctk.CTkEntry(start_frame, width=100)
        self.start_date_entry.pack(side=tk.LEFT, padx=10)
        self.start_date_entry.insert(0, today)
        
        start_date_btn = ctk.CTkButton(start_frame, text="선택", 
                                    command=lambda: self.show_date_picker_view(self.start_date_entry))
        start_date_btn.pack(side=tk.LEFT, padx=10)
        
        # 종료 날짜
        end_frame = ctk.CTkFrame(self.range_date_frame)
        end_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(end_frame, text="종료 날짜:").pack(side=tk.LEFT, padx=10)
        
        self.end_date_entry = ctk.CTkEntry(end_frame, width=100)
        self.end_date_entry.pack(side=tk.LEFT, padx=10)
        self.end_date_entry.insert(0, today)
        
        end_date_btn = ctk.CTkButton(end_frame, text="선택", 
                                    command=lambda: self.show_date_picker_view(self.end_date_entry))
        end_date_btn.pack(side=tk.LEFT, padx=10)
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        view_btn = ctk.CTkButton(button_frame, text="식단 조회", command=self.view_meals)
        view_btn.pack(side=tk.LEFT, padx=10)
        
        refresh_btn = ctk.CTkButton(button_frame, text="새로고침", command=self.refresh_meals)
        refresh_btn.pack(side=tk.LEFT, padx=10)
        
        # 결과 표시 프레임
        result_frame = ctk.CTkFrame(tab)
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 결과 레이블
        result_label = ctk.CTkLabel(result_frame, text="식단 목록")
        result_label.pack(pady=5)
        
        # 스크롤 가능한 텍스트 영역
        self.result_text = ctk.CTkTextbox(result_frame, wrap="word")
        self.result_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.result_text.configure(state="disabled")  # 읽기 전용

    def update_view_options(self):
        """조회 방법에 따라 UI 업데이트"""
        if self.view_type_var.get() == "date":
            self.range_date_frame.pack_forget()
            self.single_date_frame.pack(fill="x", pady=5)
        else:
            self.single_date_frame.pack_forget()
            self.range_date_frame.pack(fill="x", pady=5)

    def show_date_picker_view(self, entry_widget):
        """날짜 선택기 표시"""
        import tkinter as tk
        from tkcalendar import Calendar
        import datetime
        
        # 현재 날짜 가져오기 (입력 필드에서)
        try:
            current_date = datetime.datetime.strptime(entry_widget.get(), "%Y-%m-%d").date()
        except ValueError:
            current_date = datetime.date.today()
        
        # 날짜 선택 창
        picker_window = tk.Toplevel(self)
        picker_window.title("날짜 선택")
        picker_window.geometry("300x300")
        picker_window.resizable(False, False)
        picker_window.transient(self)  # 부모 창에 종속
        picker_window.grab_set()  # 모달 창으로 설정
        
        # 날짜 선택 위젯
        cal = Calendar(picker_window, selectmode="day", year=current_date.year, 
                    month=current_date.month, day=current_date.day)
        cal.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 확인 버튼
        def confirm_date():
            selected_date = cal.selection_get().strftime("%Y-%m-%d")
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, selected_date)
            picker_window.destroy()
        
        confirm_btn = ctk.CTkButton(picker_window, text="확인", command=confirm_date)
        confirm_btn.pack(pady=10)

    def view_meals(self):
        """식단 조회 실행"""
        import datetime
        import threading
        
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", "조회 중...\n")
        self.result_text.configure(state="disabled")
        
        # 날짜 정보 가져오기
        try:
            if self.view_type_var.get() == "date":
                start_date = datetime.datetime.strptime(self.single_date_entry.get(), "%Y-%m-%d").date()
                end_date = start_date
            else:
                start_date = datetime.datetime.strptime(self.start_date_entry.get(), "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(self.end_date_entry.get(), "%Y-%m-%d").date()
                
                if end_date < start_date:
                    from tkinter import messagebox
                    messagebox.showerror("오류", "종료 날짜는 시작 날짜 이후여야 합니다.")
                    self.result_text.configure(state="normal")
                    self.result_text.delete("1.0", "end")
                    self.result_text.configure(state="disabled")
                    return
        except ValueError:
            from tkinter import messagebox
            messagebox.showerror("오류", "올바른 날짜 형식이 아닙니다. (YYYY-MM-DD)")
            self.result_text.configure(state="normal")
            self.result_text.delete("1.0", "end")
            self.result_text.configure(state="disabled")
            return
        
        # 백그라운드에서 데이터 가져오기
        def fetch_data():
            events = self.meal_planner.list_meal_events(start_date, end_date)
            self.update_result_text(events, start_date, end_date)
        
        thread = threading.Thread(target=fetch_data)
        thread.daemon = True
        thread.start()

    def update_result_text(self, events, start_date, end_date):
        """결과 텍스트 업데이트"""
        import tkinter as tk
        
        # GUI 업데이트는 메인 스레드에서 해야 함
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        
        if not events:
            if start_date == end_date:
                self.result_text.insert("end", f"{start_date} 날짜에 등록된 식단이 없습니다.")
            else:
                self.result_text.insert("end", f"{start_date}부터 {end_date}까지 등록된 식단이 없습니다.")
        else:
            if start_date == end_date:
                self.result_text.insert("end", f"{start_date} 날짜의 식단 목록:\n\n")
            else:
                self.result_text.insert("end", f"{start_date}부터 {end_date}까지의 식단 목록:\n\n")
            
            current_date = None
            for event in events:
                event_time = event["time"]
                event_date = event_time.date()
                
                # 날짜가 바뀌면 날짜 구분선 추가
                if current_date != event_date:
                    if current_date is not None:
                        self.result_text.insert("end", "\n")
                    self.result_text.insert("end", f"--- {event_date} ---\n", "date_header")
                    current_date = event_date
                
                # 이벤트 정보 표시
                self.result_text.insert("end", f"{event_time.strftime('%H:%M')} - {event['summary']}\n")
        
        self.result_text.configure(state="disabled")
        
        # 텍스트 태그 설정
        self.result_text.tag_config("date_header", foreground="#1F77B4")

    def refresh_meals(self):
        """식단 목록 새로고침"""
        self.view_meals() 
    
    def setup_template_tab(self):
        """템플릿 관리 탭 설정"""
        tab = self.tabview.tab("템플릿 관리")
        
        import tkinter as tk
        from tkinter import ttk, messagebox
        
        # 상단 프레임 (템플릿 목록)
        list_frame = ctk.CTkFrame(tab)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 템플릿 목록 레이블
        list_label = ctk.CTkLabel(list_frame, text="템플릿 목록", font=("", 16, "bold"))
        list_label.pack(pady=5)
        
        # 템플릿 리스트와 스크롤바 프레임
        list_container = ctk.CTkFrame(list_frame)
        list_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 템플릿 리스트 (Treeview 사용)
        columns = ('name', 'breakfast', 'lunch', 'dinner')
        self.template_tree = ttk.Treeview(list_container, columns=columns, show='headings', selectmode='browse')
        
        # 열 설정
        self.template_tree.heading('name', text='템플릿 이름')
        self.template_tree.heading('breakfast', text='아침')
        self.template_tree.heading('lunch', text='점심')
        self.template_tree.heading('dinner', text='저녁')
        
        # 열 너비
        self.template_tree.column('name', width=150, anchor=tk.W)
        self.template_tree.column('breakfast', width=150, anchor=tk.W)
        self.template_tree.column('lunch', width=150, anchor=tk.W)
        self.template_tree.column('dinner', width=150, anchor=tk.W)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(list_container, orient='vertical', command=self.template_tree.yview)
        self.template_tree.configure(yscrollcommand=scrollbar.set)
        
        # 위젯 배치
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.template_tree.pack(side=tk.LEFT, fill="both", expand=True)
        
        # 새로고침 버튼
        refresh_btn = ctk.CTkButton(list_frame, text="새로고침", command=self.load_templates)
        refresh_btn.pack(pady=10)
        
        # 하단 프레임 (액션 버튼)
        action_frame = ctk.CTkFrame(tab)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        # 버튼들
        create_btn = ctk.CTkButton(action_frame, text="새 템플릿 만들기", command=self.create_template)
        create_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        delete_btn = ctk.CTkButton(action_frame, text="선택한 템플릿 삭제", command=self.delete_template)
        delete_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        # 템플릿 목록 로드
        self.load_templates()

    def load_templates(self):
        """템플릿 목록 로드"""
        # 기존 항목 삭제
        for item in self.template_tree.get_children():
            self.template_tree.delete(item)
        
        # 템플릿 가져오기
        templates = self.meal_planner.load_meal_template()
        if not templates:
            return
        
        # Treeview에 추가
        for name, meals in templates.items():
            breakfast = meals.get('아침', '')
            lunch = meals.get('점심', '')
            dinner = meals.get('저녁', '')
            
            self.template_tree.insert('', tk.END, values=(name, breakfast, lunch, dinner))

    def create_template(self):
        """새 템플릿 생성"""
        import tkinter as tk
        from tkinter import messagebox
        
        # 템플릿 생성 창
        create_window = tk.Toplevel(self)
        create_window.title("새 템플릿 만들기")
        create_window.geometry("400x300")
        create_window.resizable(False, False)
        create_window.transient(self)  # 부모 창에 종속
        create_window.grab_set()  # 모달 창으로 설정
        
        # 폼 프레임
        form_frame = ctk.CTkFrame(create_window)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 템플릿 이름
        name_frame = ctk.CTkFrame(form_frame)
        name_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(name_frame, text="템플릿 이름:").pack(side=tk.LEFT, padx=10)
        
        name_entry = ctk.CTkEntry(name_frame, width=200)
        name_entry.pack(side=tk.LEFT, padx=10)
        
        # 메뉴 입력 필드
        meal_types = ['아침', '점심', '저녁']
        meal_entries = {}
        
        for meal_type in meal_types:
            meal_frame = ctk.CTkFrame(form_frame)
            meal_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(meal_frame, text=f"{meal_type}:").pack(side=tk.LEFT, padx=10)
            
            meal_entry = ctk.CTkEntry(meal_frame, width=200)
            meal_entry.pack(side=tk.LEFT, padx=10)
            
            meal_entries[meal_type] = meal_entry
            
            # 자동완성 버튼
            suggestion_btn = ctk.CTkButton(meal_frame, text="추천", 
                                        command=lambda t=meal_type, e=meal_entry: self.show_template_suggestions(t, e))
            suggestion_btn.pack(side=tk.LEFT, padx=5)
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(fill="x", pady=10)
        
        # 저장 버튼
        def save_template():
            template_name = name_entry.get().strip()
            if not template_name:
                messagebox.showerror("오류", "템플릿 이름을 입력하세요.")
                return
            
            # 메뉴 정보 수집
            meal_plan = {}
            for meal_type, entry in meal_entries.items():
                meal_name = entry.get().strip()
                if meal_name:
                    meal_plan[meal_type] = meal_name
            
            if not meal_plan:
                messagebox.showerror("오류", "최소한 하나의 식단 정보를 입력하세요.")
                return
            
            # 템플릿 저장
            if self.meal_planner.save_meal_template(template_name, meal_plan):
                messagebox.showinfo("완료", f"'{template_name}' 템플릿이 저장되었습니다.")
                create_window.destroy()
                self.load_templates()  # 목록 새로고침
        
        save_btn = ctk.CTkButton(button_frame, text="저장", command=save_template)
        save_btn.pack(side=tk.RIGHT, padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="취소", command=create_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=10)

    def delete_template(self):
        """선택한 템플릿 삭제"""
        from tkinter import messagebox
        
        # 선택한 항목 확인
        selected_item = self.template_tree.selection()
        if not selected_item:
            messagebox.showinfo("알림", "삭제할 템플릿을 선택하세요.")
            return
        
        # 템플릿 이름 가져오기
        item_values = self.template_tree.item(selected_item[0], 'values')
        template_name = item_values[0]
        
        # 삭제 확인
        confirm = messagebox.askyesno("확인", f"'{template_name}' 템플릿을 삭제하시겠습니까?")
        if not confirm:
            return
        
        # 템플릿 삭제
        if self.meal_planner.delete_template(template_name):
            # 목록에서 제거
            self.template_tree.delete(selected_item)
            messagebox.showinfo("완료", f"'{template_name}' 템플릿이 삭제되었습니다.")

    def show_template_suggestions(self, meal_type, entry_widget):
        """메뉴 추천 표시"""
        import tkinter as tk
        
        # 메뉴 히스토리 가져오기
        menu_history = self.meal_planner.load_menu_history()
        suggestions = menu_history.get(meal_type, [])
        
        if not suggestions:
            from tkinter import messagebox
            messagebox.showinfo("알림", f"저장된 {meal_type} 추천 메뉴가 없습니다.")
            return
        
        # 추천 창
        suggestion_window = tk.Toplevel(self)
        suggestion_window.title(f"{meal_type} 추천 메뉴")
        suggestion_window.geometry("300x300")
        suggestion_window.resizable(False, False)
        suggestion_window.transient(self)  # 부모 창에 종속
        suggestion_window.grab_set()  # 모달 창으로 설정
        
        # 추천 목록
        list_frame = ctk.CTkFrame(suggestion_window)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for i, suggestion in enumerate(suggestions[:10]):  # 최대 10개
            button = ctk.CTkButton(
                list_frame, 
                text=suggestion,
                command=lambda s=suggestion: select_suggestion(s)
            )
            button.pack(fill="x", pady=2)
        
        # 선택 함수
        def select_suggestion(suggestion):
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, suggestion)
            suggestion_window.destroy() 
    
    def setup_settings_tab(self):
        """설정 탭 설정"""
        tab = self.tabview.tab("설정")
        
        import tkinter as tk
        from tkinter import messagebox
        
        # 식사 시간 설정 프레임
        time_frame = ctk.CTkFrame(tab)
        time_frame.pack(fill="x", padx=20, pady=20)
        
        # 프레임 제목
        time_label = ctk.CTkLabel(time_frame, text="식사 시간 설정", font=("", 16, "bold"))
        time_label.pack(pady=10)
        
        # 현재 설정 표시 및 변경 UI
        meal_frames = {}
        time_entries = {}
        
        for meal_type in self.meal_planner.meal_times.keys():
            meal_frame = ctk.CTkFrame(time_frame)
            meal_frame.pack(fill="x", pady=5)
            
            # 식사 종류 레이블
            ctk.CTkLabel(meal_frame, text=f"{meal_type}:", width=80).pack(side=tk.LEFT, padx=10)
            
            # 현재 시간 가져오기
            current_hour, current_minute = self.meal_planner.meal_times[meal_type]
            
            # 시간 입력 필드
            hour_var = tk.StringVar(value=str(current_hour))
            hour_entry = ctk.CTkEntry(meal_frame, width=50, textvariable=hour_var)
            hour_entry.pack(side=tk.LEFT, padx=5)
            
            ctk.CTkLabel(meal_frame, text=":").pack(side=tk.LEFT)
            
            minute_var = tk.StringVar(value=f"{current_minute:02d}")
            minute_entry = ctk.CTkEntry(meal_frame, width=50, textvariable=minute_var)
            minute_entry.pack(side=tk.LEFT, padx=5)
            
            # 정보 저장
            meal_frames[meal_type] = meal_frame
            time_entries[meal_type] = (hour_entry, minute_entry)
        
        # 저장 버튼
        save_time_btn = ctk.CTkButton(time_frame, text="시간 설정 저장", 
                                    command=lambda: self.save_meal_times(time_entries))
        save_time_btn.pack(pady=10)
        
        # 구분선
        separator = ctk.CTkFrame(tab, height=2, fg_color="gray70")
        separator.pack(fill="x", padx=20, pady=10)
        
        # 식사 기간 설정 프레임
        duration_frame = ctk.CTkFrame(tab)
        duration_frame.pack(fill="x", padx=20, pady=20)
        
        # 프레임 제목
        duration_label = ctk.CTkLabel(duration_frame, text="식사 기간 설정", font=("", 16, "bold"))
        duration_label.pack(pady=10)
        
        # 현재 기간 표시
        current_duration = ctk.CTkLabel(duration_frame, 
                                    text=f"현재 설정: {self.meal_planner.event_duration_hours}시간")
        current_duration.pack(pady=5)
        
        # 기간 입력 프레임
        input_frame = ctk.CTkFrame(duration_frame)
        input_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(input_frame, text="새 기간 (시간):").pack(side=tk.LEFT, padx=10)
        
        # 기간 입력 필드
        duration_var = tk.StringVar(value=str(self.meal_planner.event_duration_hours))
        duration_entry = ctk.CTkEntry(input_frame, width=100, textvariable=duration_var)
        duration_entry.pack(side=tk.LEFT, padx=10)
        
        # 저장 버튼
        save_duration_btn = ctk.CTkButton(duration_frame, text="기간 설정 저장", 
                                        command=lambda: self.save_event_duration(duration_entry, current_duration))
        save_duration_btn.pack(pady=10)
        
        # 구분선
        separator2 = ctk.CTkFrame(tab, height=2, fg_color="gray70")
        separator2.pack(fill="x", padx=20, pady=10)
        
        # 기타 설정 프레임
        other_frame = ctk.CTkFrame(tab)
        other_frame.pack(fill="x", padx=20, pady=20)
        
        # 프레임 제목
        other_label = ctk.CTkLabel(other_frame, text="기타 설정", font=("", 16, "bold"))
        other_label.pack(pady=10)
        
        # UI 테마 설정
        theme_frame = ctk.CTkFrame(other_frame)
        theme_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(theme_frame, text="UI 테마:").pack(side=tk.LEFT, padx=10)
        
        # 테마 선택 (시스템, 라이트, 다크)
        themes = ["시스템", "라이트", "다크"]
        theme_var = tk.StringVar(value=self.get_current_theme())
        theme_dropdown = ctk.CTkOptionMenu(theme_frame, values=themes, variable=theme_var,
                                        command=self.change_theme)
        theme_dropdown.pack(side=tk.LEFT, padx=10)
        
        # 앱 정보 프레임
        info_frame = ctk.CTkFrame(tab)
        info_frame.pack(fill="x", padx=20, pady=20)
        
        # 프레임 제목
        info_label = ctk.CTkLabel(info_frame, text="애플리케이션 정보", font=("", 16, "bold"))
        info_label.pack(pady=10)
        
        # 앱 정보 표시
        ctk.CTkLabel(info_frame, text="식단 플래너 v1.0").pack(pady=2)
        ctk.CTkLabel(info_frame, text="Google Calendar API 연동").pack(pady=2)
        
        # GitHub 링크 버튼
        github_btn = ctk.CTkButton(info_frame, text="GitHub 저장소", 
                                command=lambda: self.open_url("https://github.com/user/meal-planner"))
        github_btn.pack(pady=10)

    def save_meal_times(self, time_entries):
        """식사 시간 설정 저장"""
        from tkinter import messagebox
        
        for meal_type, (hour_entry, minute_entry) in time_entries.items():
            try:
                hour = int(hour_entry.get())
                minute = int(minute_entry.get())
                
                if 0 <= hour < 24 and 0 <= minute < 60:
                    self.meal_planner.update_meal_time(meal_type, hour, minute)
                else:
                    messagebox.showerror("오류", f"{meal_type}: 올바른 시간 형식이 아닙니다. (0-23시, 0-59분)")
                    return
            except ValueError:
                messagebox.showerror("오류", f"{meal_type}: 올바른 숫자를 입력하세요.")
                return
        
        messagebox.showinfo("완료", "식사 시간이 업데이트되었습니다.")

    def save_event_duration(self, duration_entry, label_widget):
        """식사 기간 설정 저장"""
        from tkinter import messagebox
        
        try:
            duration = float(duration_entry.get())
            if duration > 0:
                if self.meal_planner.update_event_duration(duration):
                    # 레이블 업데이트
                    label_widget.configure(text=f"현재 설정: {self.meal_planner.event_duration_hours}시간")
                    messagebox.showinfo("완료", f"식사 기간이 {duration}시간으로 변경되었습니다.")
            else:
                messagebox.showerror("오류", "식사 기간은 0보다 커야 합니다.")
        except ValueError:
            messagebox.showerror("오류", "올바른 숫자를 입력하세요.")

    def get_current_theme(self):
        """현재 테마 가져오기"""
        appearance_mode = ctk.get_appearance_mode()
        
        if appearance_mode == "Dark":
            return "다크"
        elif appearance_mode == "Light":
            return "라이트"
        else:
            return "시스템"

    def change_theme(self, theme):
        """테마 변경"""
        if theme == "다크":
            ctk.set_appearance_mode("Dark")
        elif theme == "라이트":
            ctk.set_appearance_mode("Light")
        else:  # 시스템
            ctk.set_appearance_mode("System")

    def open_url(self, url):
        """URL 열기"""
        import webbrowser
        webbrowser.open(url) 