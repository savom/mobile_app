import os
import mysql.connector
from mysql.connector import Error

# Database connection
def connect_to_db():
    try:
        return mysql.connector.connect(
            host="",  # 또는 "localhost"
            port=,         # MariaDB/MySQL 기본 포트
            user="",       # MariaDB 사용자 이름
            password="",   # 사용자 비밀번호
            database="",   # 사용할 데이터베이스 이름
            charset="",
            collation=""       
        )
    except Error as e:
        print(f"DB 연결 실패: {e}")
        return None

# Function to update an image by drug_num
def update_image_by_drug_num(file_path, drug_num):
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"파일을 찾을 수 없습니다: {file_path}")
            return

        # Read the image as binary data
        with open(file_path, 'rb') as file:
            blob_data = file.read()

        # Database connection
        conn = connect_to_db()
        if not conn:
            return
        
        cursor = conn.cursor()

        # Prepare SQL query to update the image
        sql = """
            UPDATE drug_info SET image = %s WHERE drug_num = %s
        """
        cursor.execute(sql, (blob_data, drug_num))

        # Commit changes
        conn.commit()

        if cursor.rowcount > 0:
            print(f"이미지가 성공적으로 업데이트되었습니다: drug_num = {drug_num}")
        else:
            print(f"해당 drug_num을 찾을 수 없습니다: {drug_num}")

    except Error as err:
        print(f"MySQL 오류: {err}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
        print("데이터 처리 완료.")

# Example usage
file_path = ""
drug_num = 0 # Example drug_num
update_image_by_drug_num(file_path, drug_num)
