import customtkinter as ctk
from tkinter import messagebox
import threading
from ..meal_planner_core import MealPlanner
from .single_date_tab import SingleDateTab
from .multi_date_tab import MultiDateTab
# ... 다른 탭 임포트 ...
# from ..utils import gui_utils

class MealPlannerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        # ... (윈도우 설정) ...

        self.meal_planner = MealPlanner()
        # ... (초기화 로직) ...

        # 메인 앱에서 제공할 메소드들 딕셔너리 (탭 클래스에 전달)
        self.shared_methods = {
            'show_suggestions': self.show_suggestions,
            'use_template': self.use_template,
            'add_meal_thread': self.add_meal_thread,
            'save_as_template': self.save_as_template,
            # ... (다른 탭들과 공유해야 하는 메소드들) ...
        }

        self.create_ui()

    def create_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 탭 추가 및 각 탭 프레임 인스턴스 생성
        tab_single = self.tabview.add("단일 날짜 식단")
        SingleDateTab(tab_single, self.meal_planner, self.shared_methods).pack(fill="both", expand=True)

        tab_multi = self.tabview.add("여러 날짜 식단")
        MultiDateTab(tab_multi, self.meal_planner, self.shared_methods).pack(fill="both", expand=True)

        # ... (다른 탭들 생성) ...

        self.tabview.set("단일 날짜 식단") # 시작 탭 설정

    # --- 메인 앱 레벨의 메소드들 (탭 클래스에서 호출됨) ---
    def show_suggestions(self, meal_type, entry_widget):
        # ... (추천 메뉴 창 띄우는 로직) ...
        # 선택 시 entry_widget.insert(0, suggestion)

    def use_template(self, target_entries):
        # ... (템플릿 선택 창 띄우고 target_entries에 적용하는 로직) ...

    def add_meal_thread(self, date_obj, meal_plan):
        threading.Thread(target=self._add_meal_worker, args=(date_obj, meal_plan)).start()

    def _add_meal_worker(self, date_obj, meal_plan):
        success = self.meal_planner.add_meal_plan(date_obj, meal_plan)
        self.after(0, lambda: self.on_meal_add_complete(success))

    def on_meal_add_complete(self, success):
        if success:
            messagebox.showinfo("완료", "식단이 성공적으로 추가되었습니다.")
            # 필요시 관련 탭의 입력창 초기화 호출 (메소드 전달 필요)
        else:
            messagebox.showerror("오류", "식단 추가 중 오류가 발생했습니다.")

    def save_as_template(self, meal_plan):
        # ... (템플릿 저장 창 띄우는 로직) ...

    # ... (다른 공유 메소드들) ...