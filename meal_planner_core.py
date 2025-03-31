import datetime
import os.path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import json
import os
import calendar

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class MealPlanner:
    # API 접근 범위
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, calendar_name='식단', timezone='Asia/Seoul'):
        self.calendar_name = calendar_name
        self.timezone = timezone
        self.credentials_file = os.environ.get('GOOGLE_CREDENTIALS_FILE', 'client_secret.json')
        self.token_file = 'token.json'
        self.meal_times = {
            '아침': (8, 0),
            '점심': (12, 0),
            '저녁': (19, 0),
        }
        self.event_duration_hours = 1
        self.service = self._get_calendar_service()
        if self.service:
            self.calendar_id = self._find_calendar_id()
        else:
            self.calendar_id = None
    
    def _get_calendar_service(self):
        """Google Calendar API 서비스 객체를 인증하고 반환합니다."""
        creds = None
        # token.json 파일이 있으면 사용자 인증 정보를 저장합니다.
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        # 유효한 인증 정보가 없으면 사용자가 로그인하도록 합니다.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"토큰 갱신 중 오류 발생: {e}")
                    # 토큰 갱신 실패 시 기존 토큰 삭제 후 재시도
                    if os.path.exists(self.token_file):
                        os.remove(self.token_file)
                    return self._get_calendar_service() # 재귀 호출로 재시도
            else:
                # credentials.json 파일이 있는지 확인
                if not os.path.exists(self.credentials_file):
                    print(f"오류: '{self.credentials_file}' 파일을 찾을 수 없습니다.")
                    print("Google Cloud Platform에서 OAuth 2.0 클라이언트 ID를 생성하고 JSON 파일을 다운로드하세요.")
                    return None

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0) # port=0: 사용 가능한 포트 자동 선택

            # 다음 실행을 위해 인증 정보를 저장합니다.
            with open(self.token_file, 'w') as token:
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
    
    def _find_calendar_id(self):
        """주어진 이름의 캘린더 ID를 찾습니다."""
        if not self.service:
            return None
        try:
            print(f"'{self.calendar_name}' 캘린더 ID 찾는 중...")
            calendar_list = self.service.calendarList().list().execute()
            for calendar_list_entry in calendar_list.get('items', []):
                if calendar_list_entry.get('summary') == self.calendar_name:
                    calendar_id = calendar_list_entry['id']
                    print(f"'{self.calendar_name}' 캘린더 찾음 (ID: {calendar_id})")
                    return calendar_id
            print(f"오류: '{self.calendar_name}' 캘린더를 찾을 수 없습니다. 캘린더 이름을 확인하거나 캘린더를 생성하세요.")
            return None
        except HttpError as error:
            print(f"캘린더 목록 조회 중 오류 발생: {error}")
            return None
    
    def create_event(self, meal_type, meal_name, target_date):
        """주어진 정보로 캘린더에 이벤트를 생성합니다."""
        if not self.service or not self.calendar_id:
            print("오류: 서비스 또는 캘린더 ID가 유효하지 않아 이벤트를 생성할 수 없습니다.")
            return

        hour, minute = self.meal_times[meal_type]

        # 시간대 객체 생성
        try:
            tz = ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError:
            print(f"오류: 알 수 없는 시간대 '{self.timezone}'. 올바른 시간대 이름을 사용하세요.")
            return

        # 시작 시간 설정 (날짜와 시간 결합)
        start_dt = datetime.datetime.combine(target_date, datetime.time(hour, minute), tzinfo=tz)
        
        # 종료 시간 설정
        end_dt = start_dt + datetime.timedelta(hours=self.event_duration_hours)

        event = {
            'summary': f'{meal_type}: {meal_name}',
            'description': f'오늘의 {meal_type} 식단: {meal_name}',
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': self.timezone,
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': self.timezone,
            },
        }

        try:
            created_event = self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
            print(f"'{created_event['summary']}' 이벤트 생성됨: {created_event.get('htmlLink')}")
            return created_event
        except HttpError as error:
            print(f"'{meal_type}' 이벤트 생성 중 오류 발생: {error}")
            return None
        except Exception as e:
            print(f"'{meal_type}' 이벤트 생성 중 알 수 없는 오류: {e}")
            return None
    
    def save_meal_template(self, name, meals):
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
        return True
    
    def load_meal_template(self, template_name=None):
        """저장된 식단 템플릿 불러오기
        template_name이 지정되면 해당 템플릿을 바로 반환합니다.
        지정되지 않으면 템플릿 목록을 반환합니다.
        """
        templates_file = 'meal_templates.json'
        if not os.path.exists(templates_file):
            print("저장된 템플릿이 없습니다.")
            return None
            
        with open(templates_file, 'r', encoding='utf-8') as f:
            templates = json.load(f)
        
        if not templates:
            print("저장된 템플릿이 없습니다.")
            return None
        
        if template_name:
            if template_name in templates:
                return templates[template_name]
            else:
                print(f"'{template_name}' 템플릿을 찾을 수 없습니다.")
                return None
        
        # 템플릿 이름을 지정하지 않으면 전체 템플릿 데이터 반환
        return templates
    
    def get_templates_list(self):
        """템플릿 목록을 가져옵니다."""
        templates = self.load_meal_template()
        if templates:
            return list(templates.keys())
        return []
    
    def delete_template(self, template_name):
        """템플릿 삭제"""
        templates_file = 'meal_templates.json'
        if not os.path.exists(templates_file):
            print("저장된 템플릿이 없습니다.")
            return False
            
        with open(templates_file, 'r', encoding='utf-8') as f:
            templates = json.load(f)
        
        if template_name not in templates:
            print(f"'{template_name}' 템플릿을 찾을 수 없습니다.")
            return False
        
        del templates[template_name]
        
        with open(templates_file, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        
        print(f"'{template_name}' 템플릿이 삭제되었습니다.")
        return True
    
    def list_meal_events(self, start_date, end_date=None):
        """특정 기간의 식단 일정 조회"""
        if not end_date:
            end_date = start_date
        
        # 시작일과 종료일 설정
        tz = ZoneInfo(self.timezone)
        start_datetime = datetime.datetime.combine(start_date, datetime.time.min, tzinfo=tz)
        end_datetime = datetime.datetime.combine(end_date, datetime.time.max, tzinfo=tz)
        
        # API 호출 형식으로 변환
        timeMin = start_datetime.isoformat()
        timeMax = end_datetime.isoformat()
        
        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=timeMin,
                timeMax=timeMax,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                print(f"{start_date}부터 {end_date}까지 등록된 식단이 없습니다.")
                return []
            
            result = []
            for event in events:
                start = event['start'].get('dateTime')
                event_time = datetime.datetime.fromisoformat(start)
                event_info = {
                    'id': event['id'],
                    'summary': event['summary'],
                    'time': event_time,
                    'formatted_time': event_time.strftime('%Y-%m-%d %H:%M')
                }
                result.append(event_info)
                print(f"{event_time.strftime('%Y-%m-%d %H:%M')} - {event['summary']}")
            
            return result
        except HttpError as error:
            print(f"일정 조회 중 오류 발생: {error}")
            return []
    
    def load_menu_history(self):
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
    
    def save_menu_history(self, meal_type, meal_name):
        """메뉴 입력 기록 저장"""
        history_file = 'menu_history.json'
        history = self.load_menu_history()
        
        # 중복 제거하고 최근 입력을 맨 앞으로
        if meal_name in history[meal_type]:
            history[meal_type].remove(meal_name)
        
        # 맨 앞에 추가
        history[meal_type].insert(0, meal_name)
        
        # 최대 20개만 유지
        history[meal_type] = history[meal_type][:20]
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        return True
    
    def add_meal_plan(self, target_date, meal_plan):
        """식단 추가"""
        if not meal_plan:
            print("입력된 식단 정보가 없습니다.")
            return False
        
        print(f"\n{target_date} 날짜에 다음 식단 일정을 추가합니다:")
        for meal_type, meal_name in meal_plan.items():
            print(f"- {meal_type}: {meal_name}")
            # 메뉴 히스토리에 저장
            self.save_menu_history(meal_type, meal_name)
            # 일정 추가
            self.create_event(meal_type, meal_name, target_date)
        
        return True
    
    def add_meal_plan_multiple_dates(self, dates, meal_plan):
        """여러 날짜에 동일한 식단 추가"""
        if not dates:
            print("선택된 날짜가 없습니다.")
            return False
        
        if not meal_plan:
            print("입력된 식단 정보가 없습니다.")
            return False
        
        # 확인 메시지
        print("\n다음 날짜에 식단을 추가합니다:")
        for date in dates:
            print(f"- {date.strftime('%Y-%m-%d')}")
        
        print("\n다음 메뉴로 추가합니다:")
        for meal_type, meal_name in meal_plan.items():
            print(f"- {meal_type}: {meal_name}")
            # 메뉴 히스토리에 저장
            self.save_menu_history(meal_type, meal_name)
        
        for date in dates:
            for meal_type, meal_name in meal_plan.items():
                self.create_event(meal_type, meal_name, date)
        
        print(f"\n{len(dates)}일 분량의 식단 일정이 추가되었습니다.")
        return True
    
    def create_recurring_events(self, meal_type, meal_name, start_date, recurrence_rule, end_date=None):
        """반복 일정 생성"""
        hour, minute = self.meal_times[meal_type]

        # 시간대 객체 생성
        try:
            tz = ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError:
            print(f"오류: 알 수 없는 시간대 '{self.timezone}'")
            return None

        # 시작 시간 설정
        start_dt = datetime.datetime.combine(start_date, datetime.time(hour, minute), tzinfo=tz)
        
        # 종료 시간 설정
        end_dt = start_dt + datetime.timedelta(hours=self.event_duration_hours)

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
                'timeZone': self.timezone,
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': self.timezone,
            },
            'recurrence': rrule,
        }

        try:
            created_event = self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
            print(f"반복 {meal_type} 일정 생성됨: {created_event.get('htmlLink')}")
            return created_event
        except HttpError as error:
            print(f"반복 일정 생성 중 오류 발생: {error}")
            return None
    
    def add_recurring_meal_plan(self, start_date, recurrence_rule, meal_plan, end_date=None):
        """반복 식단 일정 추가"""
        if not meal_plan:
            print("입력된 식단 정보가 없습니다.")
            return False
        
        # 확인 메시지
        print(f"\n시작 날짜: {start_date.strftime('%Y-%m-%d')}")
        if end_date:
            print(f"종료 날짜: {end_date.strftime('%Y-%m-%d')}")
        
        print("\n다음 메뉴로 반복 일정을 추가합니다:")
        for meal_type, meal_name in meal_plan.items():
            print(f"- {meal_type}: {meal_name}")
            # 메뉴 히스토리에 저장
            self.save_menu_history(meal_type, meal_name)
            # 반복 일정 추가
            self.create_recurring_events(meal_type, meal_name, start_date, recurrence_rule, end_date)
        
        return True
    
    def update_meal_time(self, meal_type, hour, minute):
        """식사 시간 설정 업데이트"""
        if meal_type not in self.meal_times:
            print(f"'{meal_type}'은(는) 유효한 식사 유형이 아닙니다.")
            return False
        
        if 0 <= hour < 24 and 0 <= minute < 60:
            self.meal_times[meal_type] = (hour, minute)
            print(f"{meal_type} 시간이 {hour:02d}:{minute:02d}로 변경되었습니다.")
            return True
        else:
            print("올바른 시간 형식이 아닙니다.")
            return False
    
    def update_event_duration(self, duration):
        """식사 기간 설정 업데이트"""
        if duration > 0:
            self.event_duration_hours = duration
            print(f"식사 기간이 {self.event_duration_hours}시간으로 변경되었습니다.")
            return True
        else:
            print("식사 기간은 0보다 커야 합니다.")
            return False
    
    def initialize(self):
        """서비스 초기화 및 필요한 설정 확인"""
        if not self.service:
            self.service = self._get_calendar_service()
            if not self.service:
                return False
        
        if not self.calendar_id:
            self.calendar_id = self._find_calendar_id()
            if not self.calendar_id:
                return False
        
        return True 