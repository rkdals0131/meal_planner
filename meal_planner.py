import datetime
import os.path
# import pytz # Python 3.9 이상은 from zoneinfo import ZoneInfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import json
import os
import calendar

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- 설정 ---
# Google Calendar API 접근 범위. 수정이 필요하면 'readonly'를 제거.
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = os.environ.get('GOOGLE_CREDENTIALS_FILE', 'client_secret.json')
TOKEN_FILE = 'token.json'           # 생성될 토큰 파일 경로
TARGET_CALENDAR_NAME = '식단'      # 일정을 추가할 캘린더 이름
TIMEZONE = 'Asia/Seoul'            # 시간대 설정

# 식사 시간 설정 (시, 분)
MEAL_TIMES = {
    '아침': (8, 0),
    '점심': (12, 0),
    '저녁': (19, 0),
}
EVENT_DURATION_HOURS = 1 # 각 식사 일정의 지속 시간 (시간 단위)

# --- 함수 정의 ---

def get_calendar_service():
    """Google Calendar API 서비스 객체를 인증하고 반환합니다."""
    creds = None
    # token.json 파일이 있으면 사용자 인증 정보를 저장합니다.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    # 유효한 인증 정보가 없으면 사용자가 로그인하도록 합니다.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"토큰 갱신 중 오류 발생: {e}")
                # 토큰 갱신 실패 시 기존 토큰 삭제 후 재시도
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                return get_calendar_service() # 재귀 호출로 재시도
        else:
            # credentials.json 파일이 있는지 확인
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"오류: '{CREDENTIALS_FILE}' 파일을 찾을 수 없습니다.")
                print("Google Cloud Platform에서 OAuth 2.0 클라이언트 ID를 생성하고 JSON 파일을 다운로드하세요.")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0) # port=0: 사용 가능한 포트 자동 선택

        # 다음 실행을 위해 인증 정보를 저장합니다.
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        print("Google Calendar API 서비스 생성 완료.")
        return service
    except HttpError as error:
        print(f'서비스 생성 중 오류 발생: {error}')
        return None
    except Exception as e:
        print(f'알 수 없는 오류 발생: {e}')
        return None


def find_calendar_id(service, calendar_name):
    """주어진 이름의 캘린더 ID를 찾습니다."""
    if not service:
        return None
    try:
        print(f"'{calendar_name}' 캘린더 ID 찾는 중...")
        calendar_list = service.calendarList().list().execute()
        for calendar_list_entry in calendar_list.get('items', []):
            if calendar_list_entry.get('summary') == calendar_name:
                calendar_id = calendar_list_entry['id']
                print(f"'{calendar_name}' 캘린더 찾음 (ID: {calendar_id})")
                return calendar_id
        print(f"오류: '{calendar_name}' 캘린더를 찾을 수 없습니다. 캘린더 이름을 확인하거나 캘린더를 생성하세요.")
        return None
    except HttpError as error:
        print(f"캘린더 목록 조회 중 오류 발생: {error}")
        return None

def create_event(service, calendar_id, meal_type, meal_name, target_date):
    """주어진 정보로 캘린더에 이벤트를 생성합니다."""
    if not service or not calendar_id:
        print("오류: 서비스 또는 캘린더 ID가 유효하지 않아 이벤트를 생성할 수 없습니다.")
        return

    hour, minute = MEAL_TIMES[meal_type]

    # 시간대 객체 생성
    try:
        tz = ZoneInfo(TIMEZONE)
    except ZoneInfoNotFoundError:
        print(f"오류: 알 수 없는 시간대 '{TIMEZONE}'. 올바른 시간대 이름을 사용하세요.")
        return

    # 시작 시간 설정 (날짜와 시간 결합)
    start_dt = datetime.datetime.combine(target_date, datetime.time(hour, minute), tzinfo=tz)
    
    # 종료 시간 설정
    end_dt = start_dt + datetime.timedelta(hours=EVENT_DURATION_HOURS)

    event = {
        'summary': f'{meal_type}: {meal_name}',
        'description': f'오늘의 {meal_type} 식단: {meal_name}',
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': TIMEZONE,
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': TIMEZONE,
        },
    }

    try:
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"'{created_event['summary']}' 이벤트 생성됨: {created_event.get('htmlLink')}")
    except HttpError as error:
        print(f"'{meal_type}' 이벤트 생성 중 오류 발생: {error}")
    except Exception as e:
        print(f"'{meal_type}' 이벤트 생성 중 알 수 없는 오류: {e}")

def save_meal_template(name, meals):
    """자주 사용하는 식단 템플릿 저장"""
    templates_file = 'meal_templates.json'
    templates = {}
    
    if os.path.exists(templates_file):
        with open(templates_file, 'r', encoding='utf-8') as f:
            templates = json.load(f)
    
    templates[name] = meals
    
    with open(templates_file, 'w', encoding='utf-8') as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)
    
    print(f"'{name}' 템플릿이 저장되었습니다.")

def load_meal_template():
    """저장된 식단 템플릿 불러오기"""
    templates_file = 'meal_templates.json'
    if not os.path.exists(templates_file):
        print("저장된 템플릿이 없습니다.")
        return None
        
    with open(templates_file, 'r', encoding='utf-8') as f:
        templates = json.load(f)
    
    if not templates:
        print("저장된 템플릿이 없습니다.")
        return None
        
    print("\n===== 템플릿 목록 =====")
    template_names = list(templates.keys())
    for i, name in enumerate(template_names, 1):
        print(f"{i}. {name}")
    print("0. 취소")
    
    try:
        choice = int(input("\n사용할 템플릿 번호를 선택하세요: "))
        if choice == 0:
            return None
            
        if 1 <= choice <= len(template_names):
            selected_template = template_names[choice-1]
            return templates[selected_template]
        else:
            print("올바른 번호를 입력하세요.")
            return None
    except ValueError:
        print("숫자를 입력하세요.")
        return None

def list_meal_events(service, calendar_id, start_date, end_date=None):
    """특정 기간의 식단 일정 조회"""
    if not end_date:
        end_date = start_date
    
    # 시작일과 종료일 설정
    tz = ZoneInfo(TIMEZONE)
    start_datetime = datetime.datetime.combine(start_date, datetime.time.min, tzinfo=tz)
    end_datetime = datetime.datetime.combine(end_date, datetime.time.max, tzinfo=tz)
    
    # API 호출 형식으로 변환
    timeMin = start_datetime.isoformat()
    timeMax = end_datetime.isoformat()
    
    try:
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=timeMin,
            timeMax=timeMax,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            print(f"{start_date}부터 {end_date}까지 등록된 식단이 없습니다.")
            return
            
        for event in events:
            start = event['start'].get('dateTime')
            event_time = datetime.datetime.fromisoformat(start)
            print(f"{event_time.strftime('%Y-%m-%d %H:%M')} - {event['summary']}")
            
    except HttpError as error:
        print(f"일정 조회 중 오류 발생: {error}")

def show_ascii_header():
    """아스키 아트로 헤더 표시"""
    print("""
╭──────────────────────────────────────────────╮
│                                              │
│            🍴  식단 플래너  🍴               │
│                                              │
╰──────────────────────────────────────────────╯
    """)

def show_main_menu():
    """메인 메뉴 표시"""
    show_ascii_header()
    print("""
╭─────────────── 메인 메뉴 ───────────────╮
│                                         │
│  1. 단일 날짜 식단 추가                 │
│  2. 여러 날짜 식단 추가                 │
│  3. 반복 식단 일정 추가                 │
│  4. 식단 조회하기                       │
│  5. 식단 템플릿 관리                    │
│  6. 설정                                │
│  0. 종료                                │
│                                         │
╰─────────────────────────────────────────╯
    """)
    
    choice = input("\n원하는 메뉴를 선택하세요: ")
    return choice

def add_meal_plan(service, calendar_id):
    """식단 추가 메뉴"""
    print("\n===== 식단 추가하기 =====")
    print("(뒤로 가려면 'back' 입력)")
    
    # 날짜 입력
    while True:
        date_str = input("\n날짜를 입력하세요 (YYYY-MM-DD): ")
        if date_str.lower() == 'back':
            return
        
        try:
            target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            break
        except ValueError:
            print("잘못된 날짜 형식입니다. YYYY-MM-DD 형식으로 입력해주세요.")
    
    # 식단 템플릿 사용 여부 확인
    use_template = input("저장된 템플릿을 사용하시겠습니까? (y/n): ").lower() == 'y'
    meal_plan = {}
    
    if use_template:
        template = load_meal_template()
        if template:
            meal_plan = template
    
    # 템플릿을 사용하지 않거나 템플릿이 없는 경우 직접 입력
    if not meal_plan:
        for meal_type in MEAL_TIMES.keys():
            while True:
                meal_name = input(f"{meal_type} 메뉴를 입력하세요 (건너뛰기: Enter, 뒤로: 'back'): ")
                if meal_name.lower() == 'back':
                    return
                if meal_name:
                    meal_plan[meal_type] = meal_name
                break
    
    # 입력 확인
    if not meal_plan:
        print("입력된 식단 정보가 없습니다.")
        return
    
    print(f"\n{target_date} 날짜에 다음 식단 일정을 추가합니다:")
    for meal_type, meal_name in meal_plan.items():
        print(f"- {meal_type}: {meal_name}")
    
    confirm = input("\n일정을 추가하시겠습니까? (y/n): ")
    if confirm.lower() == 'y':
        for meal_type, meal_name in meal_plan.items():
            create_event(service, calendar_id, meal_type, meal_name, target_date)
        print("\n모든 식단 일정이 추가되었습니다.")
        
        # 템플릿 저장 여부 확인
        save_as_template = input("이 식단을 템플릿으로 저장하시겠습니까? (y/n): ")
        if save_as_template.lower() == 'y':
            template_name = input("템플릿 이름을 입력하세요: ")
            if template_name:
                save_meal_template(template_name, meal_plan)
    else:
        print("\n일정 추가가 취소되었습니다.")

def view_meal_plans(service, calendar_id):
    """식단 조회 메뉴"""
    print("\n===== 식단 조회하기 =====")
    print("(뒤로 가려면 'back' 입력)")
    
    while True:
        print("\n조회 방법 선택:")
        print("1. 특정 날짜 조회")
        print("2. 기간 조회")
        print("0. 뒤로 가기")
        
        choice = input("\n선택: ")
        
        if choice == '0' or choice.lower() == 'back':
            return
            
        if choice == '1':
            date_str = input("조회할 날짜를 입력하세요 (YYYY-MM-DD): ")
            if date_str.lower() == 'back':
                return
                
            try:
                target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                list_meal_events(service, calendar_id, target_date)
            except ValueError:
                print("잘못된 날짜 형식입니다.")
                
        elif choice == '2':
            start_str = input("시작 날짜를 입력하세요 (YYYY-MM-DD): ")
            if start_str.lower() == 'back':
                return
                
            end_str = input("종료 날짜를 입력하세요 (YYYY-MM-DD): ")
            if end_str.lower() == 'back':
                return
                
            try:
                start_date = datetime.datetime.strptime(start_str, '%Y-%m-%d').date()
                end_date = datetime.datetime.strptime(end_str, '%Y-%m-%d').date()
                list_meal_events(service, calendar_id, start_date, end_date)
            except ValueError:
                print("잘못된 날짜 형식입니다.")
        else:
            print("올바른 메뉴를 선택해주세요.")

def manage_templates():
    """식단 템플릿 관리 메뉴"""
    while True:
        print("\n===== 식단 템플릿 관리 =====")
        print("1. 템플릿 목록 보기")
        print("2. 새 템플릿 만들기")
        print("3. 템플릿 삭제하기")
        print("0. 뒤로 가기")
        
        choice = input("\n선택: ")
        
        if choice == '0' or choice.lower() == 'back':
            return
            
        if choice == '1':
            list_templates()
        elif choice == '2':
            create_new_template()
        elif choice == '3':
            delete_template()
        else:
            print("올바른 메뉴를 선택해주세요.")

def list_templates():
    """템플릿 목록 표시"""
    templates_file = 'meal_templates.json'
    if not os.path.exists(templates_file):
        print("저장된 템플릿이 없습니다.")
        return
        
    with open(templates_file, 'r', encoding='utf-8') as f:
        templates = json.load(f)
    
    if not templates:
        print("저장된 템플릿이 없습니다.")
        return
        
    print("\n===== 템플릿 목록 =====")
    for name, meals in templates.items():
        print(f"\n* {name}")
        for meal_type, menu in meals.items():
            print(f"  - {meal_type}: {menu}")
    
    input("\n계속하려면 Enter 키를 누르세요...")

def create_new_template():
    """새 템플릿 생성"""
    template_name = input("\n템플릿 이름을 입력하세요: ")
    if not template_name:
        print("템플릿 이름이 필요합니다.")
        return
        
    meal_plan = {}
    for meal_type in MEAL_TIMES.keys():
        meal_name = input(f"{meal_type} 메뉴를 입력하세요: ")
        if meal_name:
            meal_plan[meal_type] = meal_name
    
    if not meal_plan:
        print("최소한 하나의 식단 정보가 필요합니다.")
        return
        
    save_meal_template(template_name, meal_plan)
    print(f"'{template_name}' 템플릿이 생성되었습니다.")

def delete_template():
    """템플릿 삭제"""
    templates_file = 'meal_templates.json'
    if not os.path.exists(templates_file):
        print("저장된 템플릿이 없습니다.")
        return
        
    with open(templates_file, 'r', encoding='utf-8') as f:
        templates = json.load(f)
    
    if not templates:
        print("저장된 템플릿이 없습니다.")
        return
        
    print("\n삭제할 템플릿 선택:")
    template_names = list(templates.keys())
    for i, name in enumerate(template_names, 1):
        print(f"{i}. {name}")
    print("0. 취소")
    
    try:
        choice = int(input("\n선택: "))
        if choice == 0:
            return
            
        if 1 <= choice <= len(template_names):
            template_to_delete = template_names[choice-1]
            confirm = input(f"'{template_to_delete}' 템플릿을 삭제하시겠습니까? (y/n): ")
            
            if confirm.lower() == 'y':
                del templates[template_to_delete]
                with open(templates_file, 'w', encoding='utf-8') as f:
                    json.dump(templates, f, ensure_ascii=False, indent=2)
                print(f"'{template_to_delete}' 템플릿이 삭제되었습니다.")
        else:
            print("올바른 번호를 입력하세요.")
    except ValueError:
        print("숫자를 입력하세요.")

def settings_menu():
    """설정 메뉴"""
    global MEAL_TIMES
    
    while True:
        print("\n===== 설정 =====")
        print("1. 식사 시간 설정")
        print("2. 식사 기간 설정")
        print("0. 뒤로 가기")
        
        choice = input("\n선택: ")
        
        if choice == '0' or choice.lower() == 'back':
            return
            
        if choice == '1':
            print("\n현재 식사 시간:")
            for meal, (hour, minute) in MEAL_TIMES.items():
                print(f"{meal}: {hour:02d}:{minute:02d}")
                
            meal_to_change = input("\n변경할 식사를 선택하세요 (아침/점심/저녁): ")
            if meal_to_change in MEAL_TIMES:
                try:
                    time_str = input(f"{meal_to_change} 시간을 입력하세요 (HH:MM): ")
                    hour, minute = map(int, time_str.split(':'))
                    if 0 <= hour < 24 and 0 <= minute < 60:
                        MEAL_TIMES[meal_to_change] = (hour, minute)
                        print(f"{meal_to_change} 시간이 {hour:02d}:{minute:02d}로 변경되었습니다.")
                    else:
                        print("올바른 시간 형식이 아닙니다.")
                except ValueError:
                    print("올바른 시간 형식이 아닙니다.")
            else:
                print("올바른 식사 이름이 아닙니다.")
                
        elif choice == '2':
            global EVENT_DURATION_HOURS
            print(f"\n현재 식사 기간: {EVENT_DURATION_HOURS}시간")
            
            try:
                duration = float(input("새 식사 기간을 입력하세요 (시간 단위): "))
                if duration > 0:
                    EVENT_DURATION_HOURS = duration
                    print(f"식사 기간이 {EVENT_DURATION_HOURS}시간으로 변경되었습니다.")
                else:
                    print("식사 기간은 0보다 커야 합니다.")
            except ValueError:
                print("올바른 숫자를 입력하세요.")
        else:
            print("올바른 메뉴를 선택해주세요.")

def display_calendar(year, month):
    """달력을 표시하고 날짜를 선택받습니다."""
    # calendar 모듈의 달력 가져오기
    cal = calendar.monthcalendar(year, month)
    
    # 달력 헤더 출력
    month_name = calendar.month_name[month]
    header = f"{month_name} {year}"
    print(f"\n{header.center(20)}")
    print("Mo Tu We Th Fr Sa Su")
    
    # 날짜 출력
    for week in cal:
        week_str = ""
        for day in week:
            if day == 0:
                week_str += "   "
            else:
                week_str += f"{day:2d} "
        print(week_str)
    
    # 날짜 선택
    while True:
        try:
            day = input("\n날짜를 선택하세요 (1-31, 이전 달: p, 다음 달: n, 취소: c): ")
            
            if day.lower() == 'c':
                return None
            elif day.lower() == 'p':
                # 이전 달로 이동
                if month == 1:
                    return display_calendar(year - 1, 12)
                else:
                    return display_calendar(year, month - 1)
            elif day.lower() == 'n':
                # 다음 달로 이동
                if month == 12:
                    return display_calendar(year + 1, 1)
                else:
                    return display_calendar(year, month + 1)
            
            day = int(day)
            # 선택한 날짜가 유효한지 확인
            valid_days = [d for week in cal for d in week if d != 0]
            if day in valid_days:
                return datetime.date(year, month, day)
            else:
                print("유효하지 않은 날짜입니다.")
        except ValueError:
            print("올바른 숫자를 입력하세요.")

def select_date():
    """날짜 선택 메뉴"""
    today = datetime.date.today()
    
    print("\n날짜 선택 방법:")
    print("1. 달력에서 선택")
    print("2. 직접 입력 (YYYY-MM-DD)")
    print("0. 취소")
    
    choice = input("\n선택: ")
    
    if choice == '0' or choice.lower() == 'back':
        return None
    
    if choice == '1':
        # 달력에서 선택
        return display_calendar(today.year, today.month)
    elif choice == '2':
        # 직접 입력
        while True:
            date_str = input("날짜 입력 (YYYY-MM-DD): ")
            if date_str.lower() == 'back':
                return None
            
            try:
                return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                print("잘못된 날짜 형식입니다. YYYY-MM-DD 형식으로 입력해주세요.")
    else:
        print("올바른 옵션을 선택하세요.")
        return select_date()  # 재귀 호출로 다시 선택

def load_menu_history():
    """이전에 입력한 메뉴 목록 불러오기"""
    history_file = 'menu_history.json'
    history = {'아침': [], '점심': [], '저녁': []}
    
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            pass
    
    return history

def save_menu_history(history, meal_type, meal_name):
    """메뉴 입력 기록 저장"""
    history_file = 'menu_history.json'
    
    # 중복 제거하고 최근 입력을 맨 앞으로
    if meal_name in history[meal_type]:
        history[meal_type].remove(meal_name)
    
    # 맨 앞에 추가
    history[meal_type].insert(0, meal_name)
    
    # 최대 20개만 유지
    history[meal_type] = history[meal_type][:20]
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def input_with_autocomplete(prompt, options):
    """자동완성 기능이 있는 입력"""
    if not options:
        return input(prompt)
    
    print(prompt)
    print("추천 메뉴 (숫자로 선택하거나 직접 입력):")
    for i, option in enumerate(options[:5], 1):  # 상위 5개만 표시
        print(f"{i}. {option}")
    
    user_input = input("선택 또는 입력: ")
    
    # 숫자로 입력한 경우 해당 옵션 반환
    try:
        idx = int(user_input) - 1
        if 0 <= idx < len(options):
            return options[idx]
    except ValueError:
        pass
    
    # 숫자가 아니면 그대로 반환
    return user_input

def select_multiple_dates():
    """다중 날짜 선택 기능"""
    selected_dates = []
    
    print("\n===== 다중 날짜 선택 =====")
    print("날짜 선택 방법:")
    print("1. 날짜 범위 지정")
    print("2. 개별 날짜 여러 개 선택")
    print("0. 취소")
    
    choice = input("\n선택: ")
    
    if choice == '0' or choice.lower() == 'back':
        return []
    
    if choice == '1':
        # 날짜 범위 선택
        print("\n시작 날짜 선택:")
        start_date = select_date()
        if not start_date:
            return []
        
        print("\n종료 날짜 선택:")
        end_date = select_date()
        if not end_date:
            return []
        
        if end_date < start_date:
            print("종료 날짜는 시작 날짜 이후여야 합니다.")
            return []
        
        # 시작일부터 종료일까지의 모든 날짜 생성
        current = start_date
        while current <= end_date:
            selected_dates.append(current)
            current += datetime.timedelta(days=1)
            
    elif choice == '2':
        # 개별 날짜 선택
        while True:
            print(f"\n현재 선택된 날짜: {[date.strftime('%Y-%m-%d') for date in selected_dates]}")
            print("\n추가할 날짜 선택 (완료: d, 취소: c):")
            
            date = select_date()
            if not date:
                continue
                
            if date in selected_dates:
                print("이미 선택된 날짜입니다.")
            else:
                selected_dates.append(date)
                
            action = input("\n계속 날짜를 추가하시겠습니까? (y/n/c): ")
            if action.lower() == 'n' or action.lower() == 'd':
                break
            elif action.lower() == 'c':
                return []
    
    # 선택된 날짜 정렬
    selected_dates.sort()
    
    # 선택된 날짜 출력
    print("\n선택된 날짜:")
    for date in selected_dates:
        print(f"- {date.strftime('%Y-%m-%d')}")
    
    return selected_dates

def add_meal_plan_multiple_dates(service, calendar_id):
    """여러 날짜에 동일한 식단 추가"""
    print("\n===== 여러 날짜에 식단 추가 =====")
    
    # 날짜 선택
    dates = select_multiple_dates()
    if not dates:
        print("선택된 날짜가 없습니다.")
        return
    
    # 식단 입력
    meal_plan = {}
    menu_history = load_menu_history()
    
    # 템플릿 사용 여부 확인
    use_template = input("저장된 템플릿을 사용하시겠습니까? (y/n): ").lower() == 'y'
    
    if use_template:
        template = load_meal_template()
        if template:
            meal_plan = template
    
    # 템플릿을 사용하지 않거나 템플릿이 없는 경우 직접 입력
    if not meal_plan:
        for meal_type in MEAL_TIMES.keys():
            meal_name = input_with_autocomplete(f"{meal_type} 메뉴를 입력하세요 (건너뛰기: Enter): ", menu_history[meal_type])
            if meal_name:
                meal_plan[meal_type] = meal_name
                save_menu_history(menu_history, meal_type, meal_name)
    
    # 입력 확인
    if not meal_plan:
        print("입력된 식단 정보가 없습니다.")
        return
    
    # 확인 메시지
    print("\n다음 날짜에 식단을 추가합니다:")
    for date in dates:
        print(f"- {date.strftime('%Y-%m-%d')}")
    
    print("\n다음 메뉴로 추가합니다:")
    for meal_type, meal_name in meal_plan.items():
        print(f"- {meal_type}: {meal_name}")
    
    confirm = input("\n일정을 추가하시겠습니까? (y/n): ")
    if confirm.lower() == 'y':
        for date in dates:
            for meal_type, meal_name in meal_plan.items():
                create_event(service, calendar_id, meal_type, meal_name, date)
        print(f"\n{len(dates)}일 분량의 식단 일정이 추가되었습니다.")
    else:
        print("\n일정 추가가 취소되었습니다.")

def create_recurring_events(service, calendar_id, meal_type, meal_name, start_date, recurrence_rule, end_date=None):
    """반복 일정 생성"""
    hour, minute = MEAL_TIMES[meal_type]

    # 시간대 객체 생성
    try:
        tz = ZoneInfo(TIMEZONE)
    except ZoneInfoNotFoundError:
        print(f"오류: 알 수 없는 시간대 '{TIMEZONE}'")
        return

    # 시작 시간 설정
    start_dt = datetime.datetime.combine(start_date, datetime.time(hour, minute), tzinfo=tz)
    
    # 종료 시간 설정
    end_dt = start_dt + datetime.timedelta(hours=EVENT_DURATION_HOURS)

    # RRULE 형식으로 반복 규칙 생성
    rrule = [f"RRULE:{recurrence_rule}"]
    if end_date:
        # 종료일이 있는 경우
        rrule = [f"RRULE:{recurrence_rule};UNTIL={end_date.strftime('%Y%m%dT235959Z')}"]

    event = {
        'summary': f'{meal_type}: {meal_name}',
        'description': f'{meal_type} 식단: {meal_name} (반복 일정)',
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': TIMEZONE,
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': TIMEZONE,
        },
        'recurrence': rrule,
    }

    try:
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"반복 {meal_type} 일정 생성됨: {created_event.get('htmlLink')}")
        return created_event
    except HttpError as error:
        print(f"반복 일정 생성 중 오류 발생: {error}")
        return None

def add_recurring_meal_plan(service, calendar_id):
    """반복 식단 일정 추가"""
    print("\n===== 반복 식단 일정 추가 =====")
    
    # 시작 날짜 선택
    print("\n시작 날짜 선택:")
    start_date = select_date()
    if not start_date:
        return
    
    # 반복 패턴 선택
    print("\n반복 패턴 선택:")
    print("1. 매일")
    print("2. 매주 특정 요일")
    print("3. 매월 특정 날짜")
    print("0. 취소")
    
    choice = input("\n선택: ")
    
    if choice == '0' or choice.lower() == 'back':
        return
    
    recurrence_rule = ""
    
    if choice == '1':
        # 매일
        recurrence_rule = "FREQ=DAILY"
    elif choice == '2':
        # 매주 특정 요일
        days_of_week = ["월", "화", "수", "목", "금", "토", "일"]
        days_in_rrule = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        
        print("\n요일 선택 (쉼표로 구분, 예: 1,3,5):")
        for i, day in enumerate(days_of_week, 1):
            print(f"{i}. {day}")
        
        day_choices = input("\n선택: ")
        selected_days = []
        
        try:
            for choice in day_choices.split(','):
                idx = int(choice.strip()) - 1
                if 0 <= idx < 7:
                    selected_days.append(days_in_rrule[idx])
        except ValueError:
            print("올바른 숫자를 입력하세요.")
            return
        
        if not selected_days:
            print("요일을 선택해야 합니다.")
            return
        
        recurrence_rule = f"FREQ=WEEKLY;BYDAY={','.join(selected_days)}"
    elif choice == '3':
        # 매월 특정 날짜
        day_of_month = start_date.day
        recurrence_rule = f"FREQ=MONTHLY;BYMONTHDAY={day_of_month}"
    else:
        print("올바른 옵션을 선택하세요.")
        return
    
    # 종료 날짜 또는 반복 횟수 설정
    print("\n종료 조건 선택:")
    print("1. 종료 날짜 지정")
    print("2. 반복 횟수 지정")
    print("3. 종료 없음 (무기한)")
    
    end_choice = input("\n선택: ")
    
    end_date = None
    
    if end_choice == '1':
        # 종료 날짜 선택
        print("\n종료 날짜 선택:")
        end_date = select_date()
        if not end_date or end_date <= start_date:
            print("종료 날짜는 시작 날짜 이후여야 합니다.")
            return
    elif end_choice == '2':
        # 반복 횟수 지정
        try:
            count = int(input("반복 횟수 입력: "))
            if count <= 0:
                print("반복 횟수는 양수여야 합니다.")
                return
            recurrence_rule += f";COUNT={count}"
        except ValueError:
            print("올바른 숫자를 입력하세요.")
            return
    # end_choice == '3'인 경우 종료 없음 (기본값)
    
    # 식단 입력
    meal_plan = {}
    menu_history = load_menu_history()
    
    # 템플릿 사용 여부 확인
    use_template = input("저장된 템플릿을 사용하시겠습니까? (y/n): ").lower() == 'y'
    
    if use_template:
        template = load_meal_template()
        if template:
            meal_plan = template
    
    # 템플릿을 사용하지 않거나 템플릿이 없는 경우 직접 입력
    if not meal_plan:
        for meal_type in MEAL_TIMES.keys():
            meal_name = input_with_autocomplete(f"{meal_type} 메뉴를 입력하세요 (건너뛰기: Enter): ", menu_history[meal_type])
            if meal_name:
                meal_plan[meal_type] = meal_name
                save_menu_history(menu_history, meal_type, meal_name)
    
    # 입력 확인
    if not meal_plan:
        print("입력된 식단 정보가 없습니다.")
        return
    
    # 확인 메시지
    print(f"\n시작 날짜: {start_date.strftime('%Y-%m-%d')}")
    if end_date:
        print(f"종료 날짜: {end_date.strftime('%Y-%m-%d')}")
    
    print("\n다음 메뉴로 반복 일정을 추가합니다:")
    for meal_type, meal_name in meal_plan.items():
        print(f"- {meal_type}: {meal_name}")
    
    confirm = input("\n일정을 추가하시겠습니까? (y/n): ")
    if confirm.lower() == 'y':
        for meal_type, meal_name in meal_plan.items():
            create_recurring_events(service, calendar_id, meal_type, meal_name, start_date, recurrence_rule, end_date)
        print("\n반복 식단 일정이 추가되었습니다.")
    else:
        print("\n일정 추가가 취소되었습니다.")

# --- 메인 실행 로직 ---
if __name__ == '__main__':
    # 식사 시간 수정 (저녁 7시로)
    MEAL_TIMES['저녁'] = (19, 0)
    
    service = get_calendar_service()
    if not service:
        exit()

    target_calendar_id = find_calendar_id(service, TARGET_CALENDAR_NAME)
    if not target_calendar_id:
        exit()
    
    while True:
        choice = show_main_menu()
        
        if choice == '0':
            print("프로그램을 종료합니다.")
            break
        elif choice == '1':
            add_meal_plan(service, target_calendar_id)
        elif choice == '2':
            add_meal_plan_multiple_dates(service, target_calendar_id)
        elif choice == '3':
            add_recurring_meal_plan(service, target_calendar_id)
        elif choice == '4':
            view_meal_plans(service, target_calendar_id)
        elif choice == '5':
            manage_templates()
        elif choice == '6':
            settings_menu()
        else:
            print("올바른 메뉴를 선택해주세요.")

# 클래스 기반 구조로 리팩터링
class MealPlanner:
    def __init__(self, calendar_name='식단', timezone='Asia/Seoul'):
        self.calendar_name = calendar_name
        self.timezone = timezone
        self.meal_times = {
            '아침': (8, 0),
            '점심': (12, 0),
            '저녁': (19, 0),
        }
        self.service = self._get_calendar_service()
        self.calendar_id = self._find_calendar_id()
    
    def _get_calendar_service(self):
        # 인증 및 서비스 생성 로직
        pass
    
    def _find_calendar_id(self):
        # 캘린더 ID 찾기 로직
        pass
    
    def add_meal(self, date, meal_type, meal_name):
        # 식사 일정 추가 로직
        pass
    
    # 기타 메소들...