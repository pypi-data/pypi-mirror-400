# nfcl/core.py
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

class ComciganAPI:
    def __init__(self, headless=True):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless") # 창 숨기기
            options.add_argument("--disable-gpu")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # 드라이버 자동 관리자 사용
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 20)
        self.base_url = "http://www.xn--s39aj90b0nb2xw6xh.kr/"

    def find_frame_with_search_bar(self):
        # ... (이전 코드의 로직 그대로 사용) ...
        driver = self.driver
        try:
            driver.find_element(By.ID, "sc")
            return True
        except: pass

        frames = driver.find_elements(By.TAG_NAME, "frame")
        for frame in frames:
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame(frame)
                driver.find_element(By.ID, "sc")
                return True
            except: continue

        driver.switch_to.default_content()
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame(iframe)
                driver.find_element(By.ID, "sc")
                return True
            except: continue
        return False

    def get_timetable(self, school_name, grade, class_num):
        driver = self.driver
        try:
            driver.get(self.base_url)
            time.sleep(1)

            if not self.find_frame_with_search_bar():
                return {"error": "프레임 탐색 실패"}

            # 학교 검색
            search_box = self.wait.until(EC.element_to_be_clickable((By.ID, "sc")))
            search_box.clear()
            search_box.send_keys(school_name)
            driver.find_element(By.CSS_SELECTOR, 'input[value="검색"]').click()
            
            time.sleep(1)
            try:
                self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.검색")))
            except:
                 return {"error": "검색 결과 없음"}

            search_results = driver.find_elements(By.CSS_SELECTOR, "tr.검색")
            clicked = False
            found_school_name = ""
            
            for row in search_results:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 2:
                    try:
                        link = cols[1].find_element(By.TAG_NAME, "a")
                        if school_name in link.text:
                            found_school_name = link.text
                            link.click()
                            clicked = True
                            break
                    except: continue
            
            if not clicked: return {"error": f"'{school_name}' 학교를 찾을 수 없습니다."}

            time.sleep(1.5)
            select_element = self.wait.until(EC.presence_of_element_located((By.ID, "ba")))
            select_obj = Select(select_element)
            target_value = f"{grade}-{class_num}"
            
            try:
                select_obj.select_by_value(target_value)
            except:
                return {"error": "해당 반 정보가 없습니다."}

            time.sleep(1)
            
            week_days = ["월", "화", "수", "목", "금"]
            final_schedule = {day: [] for day in week_days}

            rows = driver.find_elements(By.TAG_NAME, "tr")
            header_count = 0 

            for row in rows:
                periods = row.find_elements(By.CLASS_NAME, "교시")
                if not periods: continue
                
                period_text = periods[0].text.strip()
                if period_text == "교시":
                    header_count += 1
                    if header_count > 1: break
                    continue 

                simple_period = period_text.split("(")[0] 
                subjects_td = row.find_elements(By.CSS_SELECTOR, "td.내용, td.변경")
                
                if len(subjects_td) != 5: continue

                for col_idx, td in enumerate(subjects_td):
                    raw_text = td.text.replace("\n", " ").strip()
                    if not raw_text:
                        subject = "-"
                        teacher = ""
                    else:
                        parts = raw_text.split(" ")
                        if len(parts) >= 2:
                            subject = parts[0]
                            teacher = " ".join(parts[1:]) 
                        else:
                            subject = raw_text
                            teacher = ""

                    final_schedule[week_days[col_idx]].append({
                        "period": simple_period,
                        "subject": subject,
                        "teacher": teacher
                    })

            return {
                "school": found_school_name,
                "class": f"{grade}-{class_num}",
                "timetable": final_schedule
            }

        except Exception as e:
            return {"error": str(e)}
        finally:
            driver.quit()