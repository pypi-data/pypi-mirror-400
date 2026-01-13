import json
import requests

API_BASE_URL = 'http://127.0.0.1:5050/oddagent/chat'                # API地址

def recognize_intent(message):
    """调用api_oddagent_chat API"""
    try:
        response = requests.post(
            API_BASE_URL,
            json={
                'question': message, 
                'api_mode': 1 # 模拟API结果，0-不模拟，1-模拟，2-自定义API
                }, 
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return { 'err_code': 200, 'message': 'success', 'data': data}
    except Exception as e:
        print(f"API调用失败: {str(e)}")
        return { 'err_code': 500, 'message': f'API调用失败: {str(e)}', 'data': None }

if __name__ == '__main__':
    json_response = recognize_intent("开个周例会")
    print(json.dumps(json_response, ensure_ascii=False, indent=2))
