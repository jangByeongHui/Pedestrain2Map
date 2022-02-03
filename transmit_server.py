import requests
import json


# 관제 서버에 주차 상태를 전송
def put(url1, data, headers):
    try:
        r = requests.put(url1, data=json.dumps(data), headers=headers)
        if r.status_code != 200:  # 전송 성공시 상태 코드 출력
            print(r.status_code)
    # 오류 발생시 예외처리
    except requests.exceptions.Timeout as errd:
        print("Timeout Error : ", errd)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting : ", errc)
    except requests.exceptions.HTTPError as errb:
        print("Http Error : ", errb)
        # Any Error except upper exception
    except requests.exceptions.RequestException as erra:
        print("AnyException : ", erra)
