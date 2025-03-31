import customtkinter as ctk
import os
import sys
from views import MealPlannerGUI

def main():
    """메인 함수: 식단 플래너 애플리케이션 실행"""
    app = MealPlannerGUI()
    app.mainloop()

if __name__ == "__main__":
    # 필요한 디렉토리 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)  # 작업 디렉토리를 스크립트 위치로 변경
    
    try:
        main()
    except Exception as e:
        import traceback
        error_msg = f"오류 발생: {str(e)}\n\n{traceback.format_exc()}"
        
        # 에러 로그 저장
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(error_msg)
        
        print(error_msg)
        
        # GUI가 아직 실행되지 않았다면 메시지박스 대신 콘솔 출력
        if 'app' not in locals():
            print("애플리케이션 시작 중 오류가 발생했습니다.")
            print("error_log.txt 파일을 확인하세요.")
            sys.exit(1) 