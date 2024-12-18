from flask import Flask, request, jsonify
import torch
import pymysql
from PIL import Image
import io
import base64
from flask_cors import CORS
import sys
import pathlib
from pathlib import Path

# pathlib 경로 문제 해결 코드
pathlib.PosixPath = pathlib.WindowsPath

app = Flask(__name__)
CORS(app)

# DB 연결 설정
db_settings = {
    'host': '',
    'port': ,
    'user': 'root',
    'password': '',
    'database': '',
    'charset': '',
    'collation':''
}

# YOLOv5 경로 설정
yolov5_path = Path(r'')

def get_db_connection():
    """DB 연결을 관리하는 함수"""
    return pymysql.connect(**db_settings)

def load_yolov5_model():
    """YOLOv5 모델을 로드하는 함수"""
    if yolov5_path.exists():
        sys.path.append(str(yolov5_path))
    else:
        raise FileNotFoundError(f"YOLOv5 directory not found at {yolov5_path}. Please check the path.")
    
    try:
        model = torch.hub.load(str(yolov5_path), 'custom', path=str(yolov5_path / ''), source='', device='')
        print("YOLOv5 모델 로드 성공")
        return model
    except Exception as e:
        print(f"모델 로드 중 오류 발생: {str(e)}")
        raise Exception(f"Failed to load YOLOv5 model: {str(e)}")

def process_image(image_file):
    """이미지 변환 및 예외 처리"""
    try:
        image = Image.open(io.BytesIO(image_file.read())).convert('RGB')
        print("이미지 변환 성공")
        return image
    except Exception as e:
        print(f"이미지 변환 실패: {str(e)}")
        raise Exception(f"Invalid image format: {str(e)}")

def encode_image(image_data):
    """이미지 데이터를 Base64로 인코딩"""
    if image_data:
        try:
            return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            print(f"이미지 인코딩 실패: {str(e)}")
            raise Exception(f"Failed to encode image: {str(e)}")
    return None

def fetch_drug_info_from_db(drug_num):
    """DB에서 약물 정보를 조회하는 함수"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT drug_num, drug_name, formulation, color, Separating_Line, image, efficacy, 
                       usage_method, warning, precautions, interactions, side_effects, storage_method
                FROM drug_info WHERE drug_num = %s
            """
            cursor.execute(query, (drug_num,))
            result = cursor.fetchone()

            if result is None:
                raise Exception("No data found for detected class")
            
            encoded_image = encode_image(result[5])
            response = {
                'drug_num': result[0],
                'drug_name': result[1],
                'formulation': result[2],
                'color': result[3],
                'Separating_Line': result[4],
                'image': encoded_image,
                'efficacy': result[6],
                'usage_method': result[7],
                'warning': result[8],
                'precautions': result[9],
                'interactions': result[10],
                'side_effects': result[11],
                'storage_method': result[12]
            }
            return response
    finally:
        connection.close()

def handle_login_request(user_id, login_type, access_token, refresh_token, token_expiry):
    """로그인 요청을 처리하는 함수"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            check_query = "SELECT * FROM pill_check_loginfo WHERE user_id = %s AND login_type = %s"
            cursor.execute(check_query, (user_id, login_type))
            result = cursor.fetchone()

            if result:
                update_query = """
                    UPDATE pill_check_loginfo 
                    SET access_token = %s, refresh_token = %s, token_expiry = %s
                    WHERE user_id = %s AND login_type = %s
                """
                cursor.execute(update_query, (access_token, refresh_token, token_expiry, user_id, login_type))
            else:
                insert_query = """
                    INSERT INTO pill_check_loginfo (user_id, login_type, access_token, refresh_token, token_expiry)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (user_id, login_type, access_token, refresh_token, token_expiry))
            connection.commit()
    except Exception as e:
        print(f"DB 처리 중 오류 발생: {str(e)}")
        raise Exception(f"DB error: {str(e)}")
    finally:
        connection.close()

@app.route('/login', methods=['POST'])
def login():
    user_id = request.json.get('user_id')
    login_type = request.json.get('login_type')

    if not user_id or not login_type:
        return jsonify({'error_code': 'MISSING_FIELDS', 'message': 'user_id와 login_type은 필수입니다.'}), 400

    try:
        handle_login_request(
            user_id,
            login_type,
            request.json.get('access_token'),
            request.json.get('refresh_token'),
            request.json.get('token_expiry')
        )
        return jsonify({'message': '로그인 정보가 저장되었습니다.'}), 200
    except Exception as e:
        return jsonify({'error_code': 'DB_ERROR', 'message': str(e)}), 500

@app.route('/store-login-info', methods=['POST'])
def store_login_info():
    """로그인 정보를 저장하는 엔드포인트"""
    try:
        data = request.get_json()  # JSON 데이터를 받아옵니다.
        user_id = data.get('user_id')
        login_type = data.get('login_type')
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        token_expiry = data.get('token_expiry')

        if not user_id or not login_type:
            return jsonify({'error': 'user_id와 login_type은 필수입니다.'}), 400
        
        handle_login_request(user_id, login_type, access_token, refresh_token, token_expiry)
        return jsonify({'message': '로그인 정보가 저장되었습니다.'}), 200

    except Exception as e:
        print(f"로그인 정보 저장 중 오류 발생: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/get_permission/<user_id>', methods=['GET'])
def get_permission(user_id):
    # user_id에 대한 권한 확인 로직
    return jsonify({'image_permission': 1})  # 예시로 권한을 허용했다고 가정


@app.route('/predict', methods=['POST'])
def predict():
    print("POST /predict 요청 도착")
    image_file = request.files.get('image')
    if not image_file:
        return jsonify({'error': 'No image provided'}), 400

    try:
        # 이미지 처리
        image = process_image(image_file)

        # YOLOv5 모델 로드 및 예측 수행
        model = load_yolov5_model()
        results = model(image)

        if len(results.xyxy[0]) == 0:
            return jsonify({'error': 'No object detected'}), 400

        # 감지된 첫 번째 객체의 클래스 번호 및 신뢰도 추출
        detected_class = int(results.xyxy[0][0][-1].item())  # 클래스 번호
        confidence = float(results.xyxy[0][0][-2].item())  # 신뢰도

        print(f"감지된 클래스 번호: {detected_class}, 신뢰도: {confidence*100:.2f}%")

        # DB에서 해당 클래스 정보 조회
        drug_info = fetch_drug_info_from_db(detected_class)
        
        # 응답에 신뢰도 추가 (퍼센트로 변환)
        drug_info['confidence'] = confidence * 100  # 신뢰도 추가 (퍼센트로 변환)

        return jsonify(drug_info)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    data = request.json
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    # DB 연결 및 커서 생성
    connection = None
    cursor = None
    try:
        # DB 연결
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # user_id로 login_type 조회
        query = "SELECT login_type, access_token FROM pill_check_loginfo WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({'error': 'User not found'}), 404

        login_type = result['login_type']
        access_token = result['access_token']

        # DB에서 access_token 삭제
        delete_token(user_id)

        # Flutter 앱에서 처리해야 할 로그아웃 응답
        if login_type == 'google':
            return jsonify({'message': 'Google logout request'}), 200
        elif login_type == 'kakao':
            return jsonify({'message': 'Kakao logout request'}), 200
        else:
            return jsonify({'error': 'Unsupported login type'}), 400

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    finally:
        # 커서와 연결 종료
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def delete_token(user_id):
    """DB에서 토큰 삭제"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 해당 user_id의 access_token 삭제
        query = "UPDATE pill_check_loginfo SET access_token = NULL WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        connection.commit()

    except Exception as e:
        print(f"Error while deleting token: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(host='', port=5000, debug=True)
