import requests
import json
import argparse  # 用于命令行参数解析

# 基础URL（需替换实际环境IP）
BASE_URL = "http://{{ip}}/api/v1"

# 环境变量（实际使用时替换）
ENV = {
    "ip": "192.168.1.100",          # 服务器IP
    "appkey": "your_appkey",        # 应用密钥
    "appname": "your_appname",      # 应用名称
    "account_token": "",            # 由登录接口返回
    "username": "admin",            # 登录账号
    "password": "admin123",         # 登录密码
    "conf_id": "",                  # 由创建会议返回
    "meeting_id": "",               # 由创建会议返回
    "mt_id": "192.168.1.101"        # 终端ID（示例）
}

def get_token():
    """1. 获取系统token"""
    url = f"{BASE_URL}/system/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "oauth_consumer_secret": ENV["appkey"],
        "oauth_consumer_key": ENV["appname"]
    }
    resp = requests.post(url, headers=headers, data=data)
    if resp.status_code == 200 and resp.json().get("success") == 1:
        ENV["account_token"] = resp.json()["account_token"]
        return True
    print(f"获取token失败: {resp.text}")
    return False

def login():
    """2. 用户登录"""
    if not ENV["account_token"]:
        print("未获取到token")
        return False
  
    url = f"{BASE_URL}/system/login"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "account_token": ENV["account_token"],
        "username": ENV["username"],
        "password": ENV["password"]
    }
    resp = requests.post(url, headers=headers, data=data)
    return resp.status_code == 200

def create_conference(conf_name):
    """3. 创建会议（支持会议名传参）"""
    ENV["conf_name"] = conf_name  # 存储会议名到环境变量
  
    url = f"{BASE_URL}/mc/confs"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "API-Level": "6"
    }
    payload = {
        "account_token": ENV["account_token"],
        "params": json.dumps({
            "name": conf_name,  # 使用传入的会议名
            "conf_level": 5,
            "duration": 240,
            "conf_type": 0,
            "invite_members": [],
            "video_formats": [{
                "format": 4,
                "resolution": 13,
                "frame": 30,
                "bitrate": 4096
            }]
        })
    }
    resp = requests.post(url, headers=headers, data=payload)
    if resp.status_code == 200 and resp.json().get("success") == 1:
        ENV["conf_id"] = resp.json()["conf_id"]
        ENV["meeting_id"] = resp.json()["meeting_id"]
        print(f"已创建会议: {conf_name} (ID: {ENV['conf_id']})")
        return True
    print(f"创建会议失败: {resp.text}")
    return False

def invite_terminal():
    """4. 邀请终端"""
    url = f"{BASE_URL}/vc/confs/{ENV['conf_id']}/mts"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    payload = {
        "account_token": ENV["account_token"],
        "params": json.dumps({
            "mts": [{
                "mt_id": ENV["mt_id"],
                "protocol": "SIP"
            }]
        })
    }
    resp = requests.post(url, headers=headers, data=payload)
    return resp.status_code == 200

def start_data_conf():
    """5. 发送双流"""
    url = f"{BASE_URL}/vc/confs/{ENV['conf_id']}/data"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    payload = {
        "account_token": ENV["account_token"],
        "params": json.dumps({"value": 1})
    }
    resp = requests.put(url, headers=headers, data=payload)
    return resp.status_code == 200

def stop_data_conf():
    """6. 停止双流"""
    url = f"{BASE_URL}/vc/confs/{ENV['conf_id']}/data"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    payload = {
        "account_token": ENV["account_token"],
        "params": json.dumps({"value": 0})
    }
    resp = requests.delete(url, headers=headers, data=payload)
    return resp.status_code == 200

def hangup_terminal():
    """7. 挂断终端"""
    url = f"{BASE_URL}/vc/confs/{ENV['conf_id']}/mts/{ENV['mt_id']}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    payload = {"account_token": ENV["account_token"]}
    resp = requests.delete(url, headers=headers, data=payload)
    return resp.status_code == 200

def end_conference():
    """8. 结束会议"""
    url = f"{BASE_URL}/mc/confs/{ENV['conf_id']}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    payload = {"account_token": ENV["account_token"]}
    resp = requests.delete(url, headers=headers, data=payload)
    if resp.status_code == 200:
        print(f"已结束会议: {ENV.get('conf_name', '')} (ID: {ENV['conf_id']})")
        return True
    return False

def main(conf_name):
    """主流程（接受会议名参数）"""
    # 1. 获取token
    if not get_token():
        return
  
    # 2. 用户登录
    if not login():
        print("登录失败")
        return
  
    # 3. 创建会议（使用传入的会议名）
    if not create_conference(conf_name):
        return
  
    # 4. 邀请终端
    if not invite_terminal():
        print("邀请终端失败")
        return
  
    # 5. 发送双流
    if not start_data_conf():
        print("发送双流失败")
        return
  
    # 6. 停止双流
    if not stop_data_conf():
        print("停止双流失败")
        return
  
    # 7. 挂断终端
    if not hangup_terminal():
        print("挂断终端失败")
        return
  
    # 8. 结束会议
    if not end_conference():
        print("结束会议失败")
        return
  
    print(f"会议流程执行成功: {conf_name}")

if __name__ == "__main__":
    # 命令行参数解析
    parser = argparse.ArgumentParser(description='会议控制脚本')
    parser.add_argument('--conf_name', type=str, default='默认会议名称', 
                        help='会议名称（默认: 默认会议名称）')
    args = parser.parse_args()
  
    # 执行主流程
    main(args.conf_name)
