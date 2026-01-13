from .core import ComciganAPI

def get_timetable(school_name, grade, class_num):
    """
    NFCL: 학교 이름, 학년, 반을 입력하면 시간표 데이터를 반환합니다.
    """
    bot = ComciganAPI(headless=True) # 백그라운드 실행
    result = bot.get_timetable(school_name, grade, class_num)
    return result