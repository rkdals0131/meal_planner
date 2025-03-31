import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import datetime
from datetime import date
import os

from ..meal_planner_core import MealPlanner
from .single_date_tab import SingleDateTab
from .multi_date_tab import MultiDateTab
from .recurring_tab import RecurringTab
from .view_tab import ViewTab
from .template_tab import TemplateTab
from .setting_tab import SettingTab

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
        
        # 탭 관련 변수 초기화
        self.tab_instances = {}

        # 메인 앱에서 제공할 메소드들 딕셔너리 (탭 클래스에 전달)
        self.shared_methods = {
            'show_suggestions': self.show_suggestions,
            'use_template': self.use_template,
            'add_meal_thread': self.add_meal_thread,
            'save_as_template': self.save_as_template,
            'show_date_picker': self.show_date_picker,
            'show_date_picker_view': self.show_date_picker_view,
            'add_multi_meal_thread': self.add_multi_meal_thread,
            'add_recurring_meal_thread': self.add_recurring_meal_thread,
            'load_templates': self.load_templates,
            'change_theme': self.change_theme,
            'open_url': self.open_url
        }
        
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
        
        # 탭 추가 및 각 탭 프레임 인스턴스 생성
        tab_names = [
            "단일 날짜 식단", "여러 날짜 식단", "반복 식단", 
            "식단 조회", "템플릿 관리", "설정"
        ]
        
        # 탭 생성
        for tab_name in tab_names:
            self.tabview.add(tab_name)
        
        # 각 탭에 해당 클래스 인스턴스 배치
        self.tab_instances["단일 날짜 식단"] = SingleDateTab(
            self.tabview.tab("단일 날짜 식단"), 
            self.meal_planner, 
            self.shared_methods
        )
        self.tab_instances["단일 날짜 식단"].pack(fill="both", expand=True)
        
        self.tab_instances["여러 날짜 식단"] = MultiDateTab(
            self.tabview.tab("여러 날짜 식단"), 
            self.meal_planner, 
            self.shared_methods
        )
        self.tab_instances["여러 날짜 식단"].pack(fill="both", expand=True)
        
        self.tab_instances["반복 식단"] = RecurringTab(
            self.tabview.tab("반복 식단"), 
            self.meal_planner, 
            self.shared_methods
        )
        self.tab_instances["반복 식단"].pack(fill="both", expand=True)
        
        self.tab_instances["식단 조회"] = ViewTab(
            self.tabview.tab("식단 조회"), 
            self.meal_planner, 
            self.shared_methods
        )
        self.tab_instances["식단 조회"].pack(fill="both", expand=True)
        
        self.tab_instances["템플릿 관리"] = TemplateTab(
            self.tabview.tab("템플릿 관리"), 
            self.meal_planner, 
            self.shared_methods
        )
        self.tab_instances["템플릿 관리"].pack(fill="both", expand=True)
        
        self.tab_instances["설정"] = SettingTab(
            self.tabview.tab("설정"), 
            self.meal_planner, 
            self.shared_methods
        )
        self.tab_instances["설정"].pack(fill="both", expand=True)
        
    # --- 공통 함수: 추천 메뉴 표시 ---
    def show_suggestions(self, meal_type, entry_widget=None):
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
            if entry_widget:
                suggestion_btn = ctk.CTkButton(scroll_frame, text=suggestion, 
                                              command=lambda s=suggestion: self.select_suggestion(meal_type, s, suggestion_window, entry_widget))
            else:
                suggestion_btn = ctk.CTkButton(scroll_frame, text=suggestion, 
                                              command=lambda s=suggestion: self.select_suggestion(meal_type, s, suggestion_window))
            suggestion_btn.pack(pady=5, fill="x")
        
        # 취소 버튼
        cancel_btn = ctk.CTkButton(suggestion_window, text="취소", command=suggestion_window.destroy)
        cancel_btn.pack(pady=10)
    
    def select_suggestion(self, meal_type, suggestion, window, entry_widget=None):
        """추천 메뉴 선택"""
        window.destroy()
        if entry_widget:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, suggestion)
    
    # --- 공통 함수: 템플릿 사용 ---
    def use_template(self, target_entries):
        """템플릿 선택하고 항목 채우기"""
        templates = self.meal_planner.load_templates()
        
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
        for template_name, template_data in templates.items():
            template_btn = ctk.CTkButton(scroll_frame, text=template_name, 
                                        command=lambda name=template_name, data=template_data: 
                                            self.select_template(name, data, template_window, target_entries))
            template_btn.pack(pady=5, fill="x")
        
        # 취소 버튼
        cancel_btn = ctk.CTkButton(template_window, text="취소", command=template_window.destroy)
        cancel_btn.pack(pady=10)
    
    def select_template(self, template_name, template_data, window, target_entries):
        """템플릿 선택 처리"""
        window.destroy()
        
        # 항목 채우기
        for meal_type, meal_name in template_data.items():
            if meal_type in target_entries:
                target_entries[meal_type].delete(0, "end")
                target_entries[meal_type].insert(0, meal_name)
    
    # --- 공통 함수: 식단 추가 ---
    def add_meal_thread(self, date_obj, meal_plan):
        """백그라운드 스레드에서 식단 추가 실행"""
        threading.Thread(target=self._add_meal_worker, args=(date_obj, meal_plan)).start()

    def _add_meal_worker(self, date_obj, meal_plan):
        """식단 추가 워커 스레드"""
        success = self.meal_planner.add_meal_plan(date_obj, meal_plan)
        self.after(0, lambda: self.on_meal_add_complete(success))
    
    def on_meal_add_complete(self, success):
        """식단 추가 완료 후 처리"""
        if success:
            messagebox.showinfo("완료", "식단이 성공적으로 추가되었습니다.")
        else:
            messagebox.showerror("오류", "식단 추가 중 오류가 발생했습니다.")
    
    # --- 공통 함수: 여러 날짜 식단 추가 ---
    def add_multi_meal_thread(self, dates, meal_plan):
        """백그라운드 스레드에서 여러 날짜 식단 추가 실행"""
        threading.Thread(target=self._add_multi_meal_worker, args=(dates, meal_plan)).start()
    
    def _add_multi_meal_worker(self, dates, meal_plan):
        """여러 날짜 식단 추가 워커 스레드"""
        success, count = self.meal_planner.add_multi_meal_plans(dates, meal_plan)
        self.after(0, lambda: self.on_multi_meal_add_complete(success, count))
    
    def on_multi_meal_add_complete(self, success, count):
        """여러 날짜 식단 추가 완료 후 처리"""
        if success:
            messagebox.showinfo("완료", f"{count}개의 식단이 성공적으로 추가되었습니다.")
        else:
            messagebox.showerror("오류", "식단 추가 중 오류가 발생했습니다.")
    
    # --- 공통 함수: 반복 식단 추가 ---
    def add_recurring_meal_thread(self, start_date, recurrence_rule, meal_plan, end_date=None):
        """백그라운드 스레드에서 반복 식단 추가 실행"""
        threading.Thread(target=self._add_recurring_meal_worker, 
                         args=(start_date, recurrence_rule, meal_plan, end_date)).start()
    
    def _add_recurring_meal_worker(self, start_date, recurrence_rule, meal_plan, end_date):
        """반복 식단 추가 워커 스레드"""
        success = self.meal_planner.add_recurring_meal_plan(start_date, recurrence_rule, meal_plan, end_date)
        self.after(0, lambda: self.on_recurring_meal_add_complete(success))
    
    def on_recurring_meal_add_complete(self, success):
        """반복 식단 추가 완료 후 처리"""
        if success:
            messagebox.showinfo("완료", "반복 식단이 성공적으로 추가되었습니다.")
        else:
            messagebox.showerror("오류", "식단 추가 중 오류가 발생했습니다.")
    
    # --- 공통 함수: 템플릿 저장 ---
    def save_as_template(self, meal_plan):
        """템플릿으로 저장"""
        if not meal_plan:
            messagebox.showwarning("입력 오류", "저장할 식단 정보가 없습니다.")
            return
        
        # 템플릿 이름 입력 창
        template_window = ctk.CTkToplevel(self)
        template_window.title("템플릿 저장")
        template_window.geometry("300x150")
        template_window.grab_set()  # 모달 창으로 설정
        
        template_label = ctk.CTkLabel(template_window, text="템플릿 이름 입력:", font=("Arial", 14))
        template_label.pack(pady=10)
        
        name_entry = ctk.CTkEntry(template_window, width=200)
        name_entry.pack(pady=10)
        name_entry.focus()  # 포커스 설정
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(template_window)
        button_frame.pack(pady=10)
        
        save_btn = ctk.CTkButton(button_frame, text="저장", 
                                 command=lambda: self.save_template_with_name(name_entry.get(), meal_plan, template_window))
        save_btn.grid(row=0, column=0, padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="취소", command=template_window.destroy)
        cancel_btn.grid(row=0, column=1, padx=10)
    
    def save_template_with_name(self, template_name, meal_plan, window):
        """이름 지정하여 템플릿 저장"""
        if not template_name.strip():
            messagebox.showwarning("입력 오류", "템플릿 이름을 입력하세요.")
            return
        
        success = self.meal_planner.save_template(template_name, meal_plan)
        window.destroy()
        
        if success:
            messagebox.showinfo("완료", "템플릿이 성공적으로 저장되었습니다.")
        else:
            messagebox.showerror("오류", "템플릿 저장에 실패했습니다.")
    
    # --- 공통 함수: 날짜 선택기 ---
    def show_date_picker(self, entry_widget):
        """날짜 선택 창 표시"""
        date_window = ctk.CTkToplevel(self)
        date_window.title("날짜 선택")
        date_window.geometry("300x300")
        date_window.grab_set()  # 모달 창으로 설정
        
        date_label = ctk.CTkLabel(date_window, text="날짜 선택", font=("Arial", 14, "bold"))
        date_label.pack(pady=10)
        
        # 캘린더 프레임
        cal_frame = tk.Frame(date_window)
        cal_frame.pack(pady=10)
        
        cal = Calendar(cal_frame, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack()
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(date_window)
        button_frame.pack(pady=10)
        
        select_btn = ctk.CTkButton(button_frame, text="선택", 
                                  command=lambda: self.select_date_from_picker(cal, entry_widget, date_window))
        select_btn.grid(row=0, column=0, padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="취소", command=date_window.destroy)
        cancel_btn.grid(row=0, column=1, padx=10)
    
    def select_date_from_picker(self, cal, entry_widget, window):
        """날짜 선택기에서 날짜 선택"""
        selected_date = cal.get_date()
        entry_widget.delete(0, "end")
        entry_widget.insert(0, selected_date)
        window.destroy()
    
    # --- 공통 함수: 조회 날짜 선택기 ---
    def show_date_picker_view(self, entry_widget):
        """조회용 날짜 선택 창 표시"""
        date_window = ctk.CTkToplevel(self)
        date_window.title("날짜 선택")
        date_window.geometry("300x300")
        date_window.grab_set()  # 모달 창으로 설정
        
        date_label = ctk.CTkLabel(date_window, text="날짜 선택", font=("Arial", 14, "bold"))
        date_label.pack(pady=10)
        
        # 캘린더 프레임
        cal_frame = tk.Frame(date_window)
        cal_frame.pack(pady=10)
        
        cal = Calendar(cal_frame, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack()
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(date_window)
        button_frame.pack(pady=10)
        
        def confirm_date():
            selected_date = cal.get_date()
            entry_widget.delete(0, "end")
            entry_widget.insert(0, selected_date)
            date_window.destroy()
        
        select_btn = ctk.CTkButton(button_frame, text="선택", command=confirm_date)
        select_btn.grid(row=0, column=0, padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="취소", command=date_window.destroy)
        cancel_btn.grid(row=0, column=1, padx=10)
    
    # --- 공통 함수: 템플릿 로드 ---
    def load_templates(self):
        """템플릿 로드"""
        return self.meal_planner.load_templates()
    
    # --- 설정 관련 함수 ---
    def get_current_theme(self):
        """현재 테마 반환"""
        return ctk.get_appearance_mode()
    
    def change_theme(self, theme):
        """테마 변경"""
        ctk.set_appearance_mode(theme)
    
    def open_url(self, url):
        """URL 열기"""
        import webbrowser
        webbrowser.open(url)