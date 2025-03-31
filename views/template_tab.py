import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

class TemplateTab(ctk.CTkFrame):
    def __init__(self, master, planner_core, main_app_methods):
        super().__init__(master)
        self.planner_core = planner_core
        self.main_app_methods = main_app_methods
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_widgets()
        self.load_templates()
    
    def create_widgets(self):
        # 메인 프레임
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # 왼쪽: 템플릿 목록 프레임
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # 제목
        list_title = ctk.CTkLabel(left_frame, text="템플릿 목록", font=("Arial", 16, "bold"))
        list_title.pack(pady=10)
        
        # 템플릿 목록 (스크롤 가능)
        list_frame = ctk.CTkScrollableFrame(left_frame, width=200, height=400)
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.template_listbox = tk.Listbox(list_frame, width=25, height=20)
        self.template_listbox.pack(fill="both", expand=True)
        self.template_listbox.bind("<<ListboxSelect>>", self.on_template_select)
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(left_frame)
        button_frame.pack(padx=10, pady=10, fill="x")
        
        create_btn = ctk.CTkButton(button_frame, text="새 템플릿", command=self.create_template)
        create_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        delete_btn = ctk.CTkButton(button_frame, text="템플릿 삭제", command=self.delete_template)
        delete_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        refresh_btn = ctk.CTkButton(button_frame, text="새로고침", command=self.load_templates)
        refresh_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # 오른쪽: 템플릿 상세 프레임
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # 제목
        detail_title = ctk.CTkLabel(right_frame, text="템플릿 상세", font=("Arial", 16, "bold"))
        detail_title.pack(pady=10)
        
        # 선택된 템플릿 이름
        self.template_name_label = ctk.CTkLabel(right_frame, text="선택된 템플릿: 없음", font=("Arial", 14))
        self.template_name_label.pack(pady=5)
        
        # 템플릿 내용 프레임
        content_frame = ctk.CTkFrame(right_frame)
        content_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 템플릿 내용 스크롤 (meal_time: meal_name)
        content_scroll = ctk.CTkScrollableFrame(content_frame, width=400, height=300)
        content_scroll.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.content_frame = content_scroll
    
    def load_templates(self):
        """템플릿 목록 불러오기"""
        # 기존 목록 초기화
        self.template_listbox.delete(0, tk.END)
        
        # 템플릿 불러오기
        templates = self.planner_core.load_templates()
        
        if not templates:
            self.template_listbox.insert(tk.END, "저장된 템플릿 없음")
            return
        
        # 템플릿 이름 목록에 추가
        for template_name in templates.keys():
            self.template_listbox.insert(tk.END, template_name)
    
    def on_template_select(self, event=None):
        """템플릿 선택 시 상세 정보 표시"""
        selected_indices = self.template_listbox.curselection()
        if not selected_indices:
            return
        
        selected_template_name = self.template_listbox.get(selected_indices[0])
        
        # "저장된 템플릿 없음" 항목 선택 시 무시
        if selected_template_name == "저장된 템플릿 없음":
            return
        
        # 템플릿 데이터 가져오기
        templates = self.planner_core.load_templates()
        template_data = templates.get(selected_template_name, {})
        
        # 라벨 업데이트
        self.template_name_label.configure(text=f"선택된 템플릿: {selected_template_name}")
        
        # 기존 콘텐츠 프레임 내용 초기화
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 템플릿 데이터 표시
        for i, (meal_time, meal_name) in enumerate(template_data.items()):
            item_frame = ctk.CTkFrame(self.content_frame)
            item_frame.pack(padx=5, pady=5, fill="x")
            
            meal_label = ctk.CTkLabel(item_frame, text=f"{meal_time}:", width=80, anchor="w")
            meal_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            
            meal_value = ctk.CTkLabel(item_frame, text=meal_name, anchor="w")
            meal_value.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    
    def create_template(self):
        """새 템플릿 생성"""
        # 템플릿 생성 창
        create_window = ctk.CTkToplevel(self)
        create_window.title("새 템플릿 생성")
        create_window.geometry("500x500")
        create_window.grab_set()  # 모달 창으로 설정
        
        # 제목
        title_label = ctk.CTkLabel(create_window, text="새 템플릿 생성", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 템플릿 이름 입력
        name_frame = ctk.CTkFrame(create_window)
        name_frame.pack(padx=10, pady=10, fill="x")
        
        name_label = ctk.CTkLabel(name_frame, text="템플릿 이름:")
        name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        name_entry = ctk.CTkEntry(name_frame, width=300)
        name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # 식단 항목 입력 프레임
        items_frame = ctk.CTkScrollableFrame(create_window, width=450, height=300)
        items_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # 식단 항목 입력 필드들
        meal_entries = {}
        
        for i, meal_type in enumerate(self.planner_core.meal_times.keys()):
            item_frame = ctk.CTkFrame(items_frame)
            item_frame.pack(padx=5, pady=5, fill="x")
            
            meal_label = ctk.CTkLabel(item_frame, text=f"{meal_type}:", width=80, anchor="w")
            meal_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            
            meal_entry = ctk.CTkEntry(item_frame, width=250)
            meal_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            
            # 추천 버튼
            suggestion_btn = ctk.CTkButton(item_frame, text="추천", width=60,
                                          command=lambda t=meal_type, e=meal_entry: self.show_template_suggestions(t, e))
            suggestion_btn.grid(row=0, column=2, padx=5, pady=5)
            
            meal_entries[meal_type] = meal_entry
        
        # 버튼 프레임
        button_frame = ctk.CTkFrame(create_window)
        button_frame.pack(padx=10, pady=10, fill="x")
        
        save_btn = ctk.CTkButton(button_frame, text="저장", 
                                command=lambda: self.save_template(name_entry.get(), meal_entries, create_window))
        save_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        cancel_btn = ctk.CTkButton(button_frame, text="취소", command=create_window.destroy)
        cancel_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
    
    def save_template(self, name, meal_entries, window):
        """템플릿 저장"""
        if not name.strip():
            messagebox.showwarning("입력 오류", "템플릿 이름을 입력하세요.")
            return
        
        # 식단 정보 수집
        meal_plan = {}
        for meal_type, entry in meal_entries.items():
            meal_name = entry.get().strip()
            if meal_name:
                meal_plan[meal_type] = meal_name
        
        if not meal_plan:
            messagebox.showwarning("입력 오류", "최소 하나 이상의 식단 정보를 입력하세요.")
            return
        
        # 저장 확인
        confirm = messagebox.askyesno("확인", f"템플릿 '{name}'을(를) 저장하시겠습니까?")
        if not confirm:
            return
        
        # 백엔드에 저장
        success = self.planner_core.save_template(name, meal_plan)
        
        if success:
            messagebox.showinfo("완료", f"템플릿 '{name}'이(가) 저장되었습니다.")
            window.destroy()
            
            # 템플릿 목록 새로고침
            self.load_templates()
        else:
            messagebox.showerror("오류", "템플릿 저장에 실패했습니다.")
    
    def delete_template(self):
        """템플릿 삭제"""
        selected_indices = self.template_listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("알림", "삭제할 템플릿을 선택하세요.")
            return
        
        selected_template_name = self.template_listbox.get(selected_indices[0])
        
        # "저장된 템플릿 없음" 항목 선택 시 무시
        if selected_template_name == "저장된 템플릿 없음":
            return
        
        # 삭제 확인
        confirm = messagebox.askyesno("확인", f"템플릿 '{selected_template_name}'을(를) 삭제하시겠습니까?")
        if not confirm:
            return
        
        # 백엔드에서 삭제
        success = self.planner_core.delete_template(selected_template_name)
        
        if success:
            messagebox.showinfo("완료", f"템플릿 '{selected_template_name}'이(가) 삭제되었습니다.")
            
            # 템플릿 목록 새로고침
            self.load_templates()
            
            # 상세 정보 초기화
            self.template_name_label.configure(text="선택된 템플릿: 없음")
            for widget in self.content_frame.winfo_children():
                widget.destroy()
        else:
            messagebox.showerror("오류", "템플릿 삭제에 실패했습니다.")
    
    def show_template_suggestions(self, meal_type, entry_widget):
        """특정 식사에 대한 추천 메뉴 표시 (템플릿 생성용)"""
        history = self.planner_core.load_menu_history()
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
            def select_suggestion(s=suggestion):
                entry_widget.delete(0, "end")
                entry_widget.insert(0, s)
                suggestion_window.destroy()
            
            suggestion_btn = ctk.CTkButton(scroll_frame, text=suggestion, command=select_suggestion)
            suggestion_btn.pack(pady=5, fill="x")
        
        # 취소 버튼
        cancel_btn = ctk.CTkButton(suggestion_window, text="취소", command=suggestion_window.destroy)
        cancel_btn.pack(pady=10)
