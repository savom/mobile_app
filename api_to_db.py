import requests
import mysql.connector
from mysql.connector import Error

# API 키 및 URL
API_KEY = ""
IDENTIFICATION_API_URL = ""
DETAIL_API_URL = ""

# 데이터베이스 연결 함수
def connect_to_db():
    try:
        # 데이터베이스 연결
        connection = mysql.connector.connect(
            host="",  # 또는 "localhost"
            port=,         # MariaDB/MySQL 기본 포트
            user="",       # MariaDB 사용자 이름
            password="",   # 사용자 비밀번호
            database="",   # 사용할 데이터베이스 이름
            charset="",
            collation=""            
        )
        if connection.is_connected():
            print("데이터베이스 연결 성공!")
            return connection
    except Error as e:
        print(f"데이터베이스 연결 실패: {e}")
        return None

# 추가적인 약물 정보 조회 함수 (e약은요 API)
def get_additional_drug_info(item_seq):
    """
    e약은요 API에서 추가 약물 정보를 가져옵니다.
    :param item_seq: 약물 고유 식별 번호
    :return: 약물의 상세 정보 (효능, 사용법 등) 또는 기본값
    """
    params = {
        "ServiceKey": API_KEY,  # 인증 키
        "type": "json",         # 요청 데이터 형식
        "itemSeq": item_seq     # 약물 고유 번호
    }

    try:
        # API 호출
        response = requests.get(DETAIL_API_URL, params=params, timeout=10)
        
        # 상태 코드 확인
        if response.status_code != 200:
            print(f"e약은요 API 호출 실패: 상태 코드 {response.status_code}, itemSeq: {item_seq}")
            return ("정보 없음",) * 7

        # JSON 데이터 파싱
        response_json = response.json()
        items = response_json.get("body", {}).get("items", [])
        if not items:
            print(f"e약은요 API 응답에 데이터가 없습니다. itemSeq: {item_seq}")
            return ("정보 없음",) * 7

        # 첫 번째 항목의 데이터 반환
        item = items[0]
        return (
            item.get("efcyQesitm", "정보 없음"),       # 효능/효과
            item.get("useMethodQesitm", "정보 없음"),  # 사용법
            item.get("atpnWarnQesitm", "정보 없음"),   # 경고
            item.get("atpnQesitm", "정보 없음"),       # 주의사항
            item.get("intrcQesitm", "정보 없음"),      # 상호작용
            item.get("seQesitm", "정보 없음"),         # 부작용
            item.get("depositMethodQesitm", "정보 없음")  # 보관 방법
        )

    except requests.RequestException as e:
        # 네트워크 오류 처리
        print(f"e약은요 API 요청 중 네트워크 오류 발생: {e}, itemSeq: {item_seq}")
        return ("정보 없음",) * 7

    except ValueError as e:
        # JSON 파싱 오류 처리
        print(f"e약은요 API JSON 파싱 오류: {e}, itemSeq: {item_seq}")
        return ("정보 없음",) * 7

    response = requests.get(DETAIL_API_URL, params=params)
    print("API 응답 상태 코드:", response.status_code)
    print("API 응답 본문:", response.text)  # 응답 본문을 출력하여 실제 데이터 확인
    
    if response.status_code == 200:
        try:
            items = response.json().get("body", {}).get("items", [])
        except ValueError as e:
            print(f"JSON 파싱 오류: {e}")
            return None
        if not items:
            return None
        item = items[0]
        return (
            item.get("efcyQesitm", "정보 없음"),
            item.get("useMethodQesitm", "정보 없음"),
            item.get("atpnWarnQesitm", "정보 없음"),
            item.get("atpnQesitm", "정보 없음"),
            item.get("intrcQesitm", "정보 없음"),
            item.get("seQesitm", "정보 없음"),
            item.get("depositMethodQesitm", "정보 없음")  # 저장 방법
        )
    return None

# 약물 정보 삽입 함수
def insert_drug_info():
    try:
        # 데이터베이스 연결
        conn = connect_to_db()
        if not conn:
            return
        cursor = conn.cursor(buffered=True)

        # 1단계: 낱알 식별 API 호출
        params = {
            "ServiceKey": API_KEY,
            "type": "json",
            "numOfRows": 30
        }
        response = requests.get(IDENTIFICATION_API_URL, params=params)
        if response.status_code == 200:
            items = response.json().get("body", {}).get("items", [])
            if not items:
                print("API에서 데이터를 가져오지 못했습니다.")
                return

            insert_values = []
            for item in items:
                # 낱알 식별 데이터 추출
                drug_num = item.get("ITEM_SEQ")
                drug_name = item.get("ITEM_NAME")
                if not isinstance(drug_num, str) or not isinstance(drug_name, str):
                    print("잘못된 데이터 형식이 발견되어 건너뜁니다.")
                    continue
                if not drug_num or not drug_name:
                    print("필수 데이터가 누락되어 약물 정보를 건너뜁니다.")
                    continue

                formulation = item.get("FORM_CODE_NAME", "")
                formulation = formulation.strip() if formulation is not None else "기타"
                shape = item.get("DRUG_SHAPE", "기타")
                color = item.get("COLOR_CLASS1", "기타")
                line_front = item.get("LINE_FRONT", "")
                line_back = item.get("LINE_BACK", "")
                entp_name = item.get("ENTP_NAME", "기타")
                image_url = item.get("ITEM_IMAGE", "")

                # 이미지 데이터 가져오기
                image_blob = None
                if image_url:
                    try:
                        image_blob = requests.get(image_url, timeout=10).content
                    except requests.RequestException as e:
                        print(f"이미지 다운로드 실패: {e}")
                        continue

                # 2단계: e약은요 API 호출
                additional_info = get_additional_drug_info(drug_num)
                if additional_info is None:
                    efficacy, usage_method, warning, precautions, interactions, side_effects, storage_method = ("정보 없음",) * 7
                else:
                    efficacy, usage_method, warning, precautions, interactions, side_effects, storage_method = additional_info

                # 매핑된 값 생성
                formulation_num = {
                    "정제": 0, "나정": 0, "필름코팅정": 0, "저작정": 0, "발포정": 0, "설하정": 0,
                    "장용정": 0, "트로키제": 0, "당의정": 0, "산제": 1, "액제": 2, "캡슐제": 3,
                    "경질캡슐제": 3, "연질캡슐제": 3, "반고형제": 4, "연고제": 4, "크림제": 4,
                    "겔제": 4, "주사제": 5, "에어로솔제": 6, "기타": 7
                }.get(formulation, 7)

                shape_num = {
                    "원형": 0, "타원형": 1, "장방형": 2, "반원형": 3
                }.get(shape, 4)

                color_num = {
                    "하양": 1, "검정": 2, "빨강": 3, "주황": 4, "노랑": 5, "분홍": 6, "갈색": 7,
                    "초록": 8, "연두": 9, "청록": 10, "파랑": 11, "남색": 12, "보라": 13,
                    "회색": 14, "투명": 15, "기타": 16
                }.get(color, 16)

                # 분할선 유무 확인 및 매핑
                separating_line_num = 1 if line_front or line_back else 0
                separating_line = "있음" if separating_line_num == 1 else "없음"

                # 최종 데이터 준비
                values = (
                    drug_num, drug_name, formulation_num, formulation, shape_num, shape,
                    color_num, color, separating_line_num, separating_line,
                    image_blob if image_blob is not None else None, efficacy, usage_method, warning, precautions, interactions, side_effects, storage_method
                )

                # 데이터 추가
                insert_values.append(values)

            # SQL 배치 처리
            sql = """
                INSERT INTO drug_info (
                    drug_num, drug_name, formulation_num, formulation, shape_num, shape, 
                    color_num, color, Separating_Line_num, Separating_Line, image, 
                    efficacy, usage_method, warning, precautions, interactions, side_effects, storage_method
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(sql, insert_values)
            conn.commit()
            print(f"{len(insert_values)}개의 약물 정보가 성공적으로 삽입되었습니다.")

        else:
            print(f"낱알 식별 API 호출 실패: 상태 코드 {response.status_code}")

    except Error as err:
        print(f"MySQL 오류: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
        print("데이터 처리 완료.")

# 실행
insert_drug_info()
