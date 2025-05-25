# -*- coding: utf-8 -*-
"""
이 스크립트는 주어진 제목, 내용, 태그로 티스토리에 자동으로 글을 발행하는 함수를 포함합니다.
헤드리스 모드로 실행되며, "저장된 글" 알림 발생 시 "취소" 후 새 글 작성을 시도합니다.
"""

# Selenium 관련
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager # ChromeDriver 자동 관리를 위해 사용
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoAlertPresentException

# 표준 라이브러리
import time

def post_to_tistory(title_text, content_text, tags_text):
    """
    주어진 제목, 내용, 태그로 티스토리에 자동으로 글을 발행하는 함수 (헤드리스 모드).
    "저장된 글" 알림 발생 시 "취소" 후 새 글 작성을 시도합니다.

    Args:
        title_text (str): 포스팅할 글의 제목.
        content_text (str): 포스팅할 글의 내용.
        tags_text (str): 포스팅할 글의 태그 (쉼표로 구분된 문자열).

    Returns:
        bool: 포스팅 성공 시 True, 실패 시 False.
    """
    print(f"티스토리 자동 포스팅 시작: '{title_text}'")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # 중요: 아래 email, password, blog_name은 실제 값으로 채워야 합니다.
    # 이 정보는 함수 외부에서 관리하거나, 더 안전한 방식으로 전달하는 것이 좋습니다.
    email = "email"  # 실제 카카오 계정 이메일로 변경
    password = "password"     # 실제 카카오 계정 비밀번호로 변경
    blog_name = "blog_name"        # 실제 티스토리 블로그 이름으로 변경

    driver = None
    posting_successful = False

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        print("WebDriver 시작됨 (헤드리스 모드)")

        driver.get('https://accounts.kakao.com/login/?continue=https%3A%2F%2Fkauth.kakao.com%2Foauth%2Fauthorize%3Fclient_id%3D3e6ddd834b023f24221217e370daed18%26prompt%3Dselect_account%26redirect_uri%3Dhttps%253A%252F%252Fwww.tistory.com%252Fauth%252Fkakao%252Fredirect%26response_type%3Dcode%26auth_tran_id%3D0jyki8ku4znd3e6ddd834b023f24221217e370daed18maxym4gt%26ka%3Dsdk%252F1.43.6%2520os%252Fjavascript%2520sdk_type%252Fjavascript%2520lang%252Fko%2520device%252FWin32%2520origin%252Fhttps%25253A%25252F%25252Fwww.tistory.com%26is_popup%3Dfalse%26through_account%3Dtrue#login')
        print(f"카카오 로그인 페이지 접속: {driver.current_url}")

        # 로그인 시도
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'loginId')))
            email_input = driver.find_element(By.NAME, 'loginId')
            email_input.send_keys(email)
            password_input = driver.find_element(By.NAME, 'password')
            password_input.send_keys(password)
            print("이메일 및 비밀번호 입력 완료.")
            login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()
            print("로그인 버튼 클릭.")
            print("로그인 버튼 클릭 후 10초 대기 시작...")
            time.sleep(10) # 로그인 및 페이지 전환 대기 시간 (필요에 따라 조절)
            current_url_after_click_and_wait = driver.current_url
            print(f"로그인 버튼 클릭 10초 후 URL: {current_url_after_click_and_wait}")
            screenshot_name = "debug_screenshot_after_login_attempt.png"
            driver.save_screenshot(screenshot_name)
            print(f"로그인 시도 후 스크린샷 저장됨: {screenshot_name}.")

            if "tistory.com" in current_url_after_click_and_wait and \
               not ("accounts.kakao.com" in current_url_after_click_and_wait and "login" in current_url_after_click_and_wait):
                print("로그인 성공! 🎉")
            else:
                print("로그인 실패: 최종 URL이 티스토리 로그인 성공 상태가 아닙니다.")
                raise Exception("로그인 최종 실패 (URL 조건 불일치 또는 카카오 페이지에 머무름)")
        except Exception as e:
            print(f"로그인 과정 중 오류 발생: {e}")
            print("저장된 스크린샷(예: debug_screenshot_after_login_attempt.png)을 확인하여 원인을 파악하세요.")
            raise

        # 글쓰기 페이지 이동
        write_page_url = f'https://{blog_name}.tistory.com/manage/newpost'
        driver.get(write_page_url)
        print(f"글쓰기 페이지로 이동 시도: {write_page_url}")

        # === "저장된 글" 알림 처리 로직 추가 ===
        try:
            print("알림 창 확인 시도 (최대 5초 대기)...")
            WebDriverWait(driver, 5).until(EC.alert_is_present())

            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"알림 발견! 내용: '{alert_text}'")

            if "저장된 글이 있습니다" in alert_text:
                print("저장된 글 관련 알림 확인. '취소'를 클릭하여 새 글 작성을 시작합니다.")
                alert.dismiss() # "취소" 클릭
                time.sleep(1) # 알림 닫은 후 잠시 대기
                print("알림을 닫았습니다 (취소 선택).")
            else:
                print(f"예상치 못한 다른 알림입니다: '{alert_text}'. 일단 '확인'을 클릭합니다.")
                alert.accept() # 다른 종류의 알림이면 일단 '확인'
                time.sleep(1)
                print("알림을 닫았습니다 (확인 선택).")
        except TimeoutException:
            print("알림 창이 5초 내에 나타나지 않았습니다. 정상 진행합니다.")
        except NoAlertPresentException: # WebDriverWait이 성공해도 alert이 없을 수 있으므로 이 예외는 보통 발생 안 함
            print("NoAlertPresentException: 알림이 없습니다. 정상 진행합니다.")
        except Exception as e_alert:
            print(f"알림 처리 중 예외 발생: {e_alert}")
            driver.save_screenshot("debug_screenshot_alert_handling_error.png")
            raise
        # =======================================

        # 글쓰기 페이지 로드 및 제목 필드 확인
        try:
            title_input_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "post-title-inp"))
            )
            print("글쓰기 페이지 로드 및 제목 필드 확인 완료 (알림 처리 후).")
        except Exception as e:
            print(f"글쓰기 페이지 로드 실패 또는 제목 필드를 찾을 수 없음 (알림 처리 후): {e}")
            print("현재 URL:", driver.current_url)
            driver.save_screenshot("debug_screenshot_editor_page_load_error_after_alert.png")
            raise

        # 제목 입력
        try:
            title_input_element.send_keys(title_text)
            print("제목 입력 완료: ", title_text)
        except AttributeError as e_attr:
            print(f"제목 입력 중 AttributeError: {e_attr}. title_input_element가 None일 수 있습니다.")
            driver.save_screenshot("debug_screenshot_title_input_none_error.png")
            raise
        except Exception as e:
            print(f"제목 입력 중 오류: {e}")
            driver.save_screenshot("debug_screenshot_title_input_error.png")
            raise

        # 본문 입력
        try:
            WebDriverWait(driver, 20).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, "editor-tistory_ifr"))
            )
            print("본문 편집 iframe (id='editor-tistory_ifr')으로 전환 성공. 👍")
            body_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "tinymce"))
            )
            body_element.clear()
            body_element.send_keys(content_text) # 여기서 content_text는 일반 텍스트여야 합니다.
            print("본문 입력 완료. ✍️")
            driver.switch_to.default_content()
            print("기본 콘텐츠로 돌아오기 완료.")
        except Exception as e:
            print(f"본문 입력 중 오류 발생: {e} 😥")
            driver.save_screenshot("debug_screenshot_body_input_error.png")
            raise

        # 태그 입력
        try:
            tag_input_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "tagText"))
            )
            tag_input_element.send_keys(tags_text)
            print("태그 입력 완료: ", tags_text, "🏷️")
            time.sleep(1) # 태그 입력 후 안정화 시간
        except Exception as e:
            print(f"태그 입력 중 오류 발생: {e} 😥")
            driver.save_screenshot("debug_screenshot_tag_input_error.png")
            raise

        # 발행 버튼 클릭
        try:
            complete_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "publish-layer-btn"))
            )
            complete_button.click()
            print("'완료' 버튼 클릭 완료. 🎉")

            # '공개' 옵션 선택 (일반적으로 기본값일 수 있으나 명시적으로 처리)
            public_option_span_xpath = "//span[@class='checkbox-text' and normalize-space()='공개']"
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, public_option_span_xpath))
            )
            print("'공개' 옵션이 포함된 발행 설정 창 확인됨.")
            
            # '공개' 옵션이 이미 선택되어 있을 수 있으므로, 클릭 전에 상태 확인하거나 무조건 클릭
            # 여기서는 일단 클릭하는 것으로 가정
            public_option_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, public_option_span_xpath))
            )
            # 상황에 따라 '공개' 라디오 버튼이나 체크박스 ID/Name을 직접 사용하는 것이 더 안정적일 수 있습니다.
            # 예: driver.find_element(By.ID, "openState1").click() 등
            public_option_element.click() 
            print("'공개' 옵션 클릭 시도 완료. ☑️")
            time.sleep(0.5) # 옵션 선택 후 잠시 대기

            final_publish_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "publish-btn"))
            )
            final_publish_button.click()
            print("최종 '공개 발행' 버튼 클릭 완료! 🚀")
            print("게시글 발행 시도 후 잠시 대기...")
            time.sleep(5) # 발행 후 페이지 이동 또는 확인 대기
            print("발행 후 현재 URL:", driver.current_url)
            posting_successful = True
        except Exception as e:
            print(f"발행 과정 중 오류 발생: {e} 😥")
            driver.save_screenshot("debug_screenshot_publish_process_error.png")
            raise

        print("🎉 자동 포스팅 모든 단계 성공적으로 실행 시도 완료 🎉")

    except Exception as e_global:
        print(f"💥 스크립트 실행 중 예외 발생: {e_global}")
        if driver:
            try:
                final_error_screenshot_name = "debug_screenshot_function_fatal_error.png"
                driver.save_screenshot(final_error_screenshot_name)
                print(f"함수 실행 중 치명적 오류 발생 시 스크린샷 저장됨: {final_error_screenshot_name}")
            except Exception as screenshot_err:
                print(f"치명적 오류 스크린샷 저장 실패: {screenshot_err}")
    finally:
        if driver:
            driver.quit()
            print("WebDriver 종료됨.")

    return posting_successful

if __name__ == '__main__':
    # 아래는 함수 테스트를 위한 예시입니다.
    # 실제 사용 시에는 이 부분을 적절히 수정하거나 삭제하세요.

    # 주의: 테스트 시 BMP(Basic Multilingual Plane) 외부 문자가 content_for_tistory에 포함되지 않도록 해야 합니다.
    # 원본 스크립트의 filter_bmp_characters 함수를 참고하여 필요시 정제 로직을 추가하세요.
    # 여기서는 간단한 텍스트를 사용합니다.

    test_title = "티스토리 자동 포스팅 테스트 제목"
    test_content_plain = """
안녕하세요. 티스토리 자동 포스팅 테스트 본문입니다.
이 내용은 Selenium을 사용하여 자동으로 작성되었습니다.

줄바꿈도 잘 되는지 확인합니다.
1. 첫 번째 항목
2. 두 번째 항목

감사합니다.
    """
    test_tags = "자동화,테스트,파이썬" # 쉼표로 구분

    print(f"테스트를 위해 post_to_tistory 함수를 호출합니다.")
    print(f"제목: {test_title}")
    print(f"태그: {test_tags}")
    # print(f"내용 (앞 100자): {test_content_plain[:100]}...") # 내용이 길 경우 일부만 출력

    # 카카오 계정 정보(email, password)와 블로그 이름(blog_name)이
    # post_to_tistory 함수 내에 정확히 설정되어 있어야 합니다.
    success = post_to_tistory(test_title, test_content_plain, test_tags)

    if success:
        print("\n✅ 테스트 실행 결과: 포스팅 성공!")
    else:
        print("\n❌ 테스트 실행 결과: 포스팅 실패 또는 오류 발생.")
