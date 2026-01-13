import requests
import json
from urllib.parse import urljoin
from datetime import datetime, timedelta

# ======================
# 全局变量 - 账号密码配置
# ======================
IP = "10.67.20.13"
USER_NAME = "yx1"
PASSWORD = "888888"
OAUTH_CONSUMER_KEY = "1"
OAUTH_CONSUMER_SECRET = "1"

# 全局凭证（登录后赋值）
ACCOUNT_TOKEN = None
COOKIE_JAR = None

BASE_API = f"http://{IP}/api/v1/"


# ======================
# 通用响应检查函数
# ======================
def check_response(resp, action_desc):
    """统一检查接口返回结果"""
    try:
        resp.raise_for_status()
        result = resp.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ {action_desc} 请求失败: {e}")
    except json.JSONDecodeError:
        raise Exception(f"❌ {action_desc} 返回非JSON格式: {resp.text}")

    if isinstance(result, dict) and ("error" in result or "success" in result and result["success"] != 1):
        raise Exception(f"❌ {action_desc} 失败: {json.dumps(result, ensure_ascii=False)}")

    print(f"✅ {action_desc} 成功: {json.dumps(result, ensure_ascii=False)}")
    return result


# ======================
# 登录接口
# ======================
def login():
    global ACCOUNT_TOKEN, COOKIE_JAR

    token_url = urljoin(BASE_API, "system/token")
    data_key = {
        "oauth_consumer_key": OAUTH_CONSUMER_KEY,
        "oauth_consumer_secret": OAUTH_CONSUMER_SECRET,
    }

    token_resp = requests.post(token_url, data=data_key, headers={
        'Accept': 'application/json',
        "Content-Type": "application/x-www-form-urlencoded",
        "API-Level": '3'
    })
    token_result = check_response(token_resp, "获取token")

    account_token = token_result.get("account_token")
    if not account_token:
        raise Exception(f"❌ token响应格式错误: {token_result}")

    login_url = urljoin(BASE_API, "system/login")
    login_data = {
        "username": USER_NAME,
        "password": PASSWORD,
        "account_token": account_token
    }

    login_resp = requests.post(login_url, data=login_data, headers={
        'Accept': 'application/json',
        "Content-Type": "application/x-www-form-urlencoded",
        "API-Level": '3'
    })
    login_result = check_response(login_resp, "登录")

    ACCOUNT_TOKEN = account_token
    COOKIE_JAR = login_resp.cookies
    return login_result


# ======================
# 创建会议
# ======================
def create_conference(name="测试会议", start_time=None, location="会议室A", duration=240, **extra_params):
    # 该demo创建目前是即时会议，参数name和duration有效
    global ACCOUNT_TOKEN, COOKIE_JAR
    if not ACCOUNT_TOKEN or not COOKIE_JAR:
        login()

    create_url = urljoin(BASE_API, "mc/confs")

    if start_time is None:
        start_time = datetime.now() + timedelta(minutes=5)
    if isinstance(start_time, datetime):
        start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")

    conf_data = {
        "name": name,
        "start_time": start_time,
        "location": location,
        "duration": duration,
        "conf_type": 0,
    }
    conf_data.update(extra_params)

    data = {
        "params": json.dumps(conf_data),
        "account_token": ACCOUNT_TOKEN
    }

    resp = requests.post(create_url, data=data, headers={
        'Accept': 'application/json',
        "Content-Type": "application/x-www-form-urlencoded",
        "API-Level": '3'
    }, cookies=COOKIE_JAR)

    return check_response(resp, "创建会议")

# ======================
# 获取与会终端列表
# ======================
def get_mts_in_meetings(conf_id):
    """
    获取指定会议的终端列表
    :param conf_id: 会议ID
    :return: 会议中的终端列表信息
    """
    global ACCOUNT_TOKEN, COOKIE_JAR
    if not ACCOUNT_TOKEN or not COOKIE_JAR:
        login()
  
    # 构建URL和参数
    endpoints_url = urljoin(BASE_API, f"vc/confs/{conf_id}/mts")
    params = {"account_token": ACCOUNT_TOKEN}
  
    # 发送请求
    resp = requests.get(endpoints_url, params=params, headers={
        'Accept': 'application/json',
        "Content-Type": "application/x-www-form-urlencoded",
        "API-Level": '3'
    }, cookies=COOKIE_JAR)
  
    return check_response(resp, f"获取会议{conf_id}的终端列表")

# ======================
# 获取所有账号信息
# ======================
def get_all_accounts(start=0, count=10, account_filter=None):
    global ACCOUNT_TOKEN, COOKIE_JAR
    if not ACCOUNT_TOKEN or not COOKIE_JAR:
        login()
  
    # 构建URL和参数
    accounts_url = urljoin(BASE_API, "amc/accounts")
    params = {"account_token": ACCOUNT_TOKEN}
    if account_filter:
        params["account"] = account_filter
    if count > 0:
        params["start"] = start
        params["count"] = count

    # 发送请求
    resp = requests.get(accounts_url, params=params, headers={
        'Accept': 'application/json',
        "Content-Type": "application/x-www-form-urlencoded",
        "API-Level": '3'
    }, cookies=COOKIE_JAR)
  
    return check_response(resp, "获取会议成员")

# ======================
# 根据别名获取账号信息
# ======================
def search_accounts_by_alias(alias):
    global ACCOUNT_TOKEN, COOKIE_JAR
    if not ACCOUNT_TOKEN or not COOKIE_JAR:
        login()
  
    # 获取所有账号信息
    all_accounts = get_all_accounts(0, 216)  # 获取所有账号
    results = []
  
    # 搜索字段列表，真实姓名
    # search_fields = ['account', 'name']
    search_fields = ['name']
  
    # 遍历每个账号信息
    for account in all_accounts.get("accounts", []):
        for field in search_fields:
            if account[field] == "yx1":
                print(alias.lower(), account[field].lower())
            if field in account and account[field] and alias.lower() in account[field].lower():
                results.append(account)
                break
    print({"total": len(results), "accounts": results}) 
    return {"total": len(results), "accounts": results}

# ======================
# 添加终端
# ======================
def invite_mt(conf_id, mt_list):
    global ACCOUNT_TOKEN, COOKIE_JAR
    if not ACCOUNT_TOKEN or not COOKIE_JAR:
        login()

    invite_url = urljoin(BASE_API, f"vc/confs/{conf_id}/mts")

    params = {
        "from_audiences": 0,
        "mts": mt_list
    }

    data = {
        "params": json.dumps(params),
        "account_token": ACCOUNT_TOKEN
    }

    resp = requests.post(invite_url, data=data, headers={
        'Accept': 'application/json',
        "Content-Type": "application/x-www-form-urlencoded",
        "API-Level": '3'
    }, cookies=COOKIE_JAR)

    return check_response(resp, "添加终端")

# ======================
# 移除终端
# ======================
def hangup_mt(conf_id, mt_list):
    global ACCOUNT_TOKEN, COOKIE_JAR
    if not ACCOUNT_TOKEN or not COOKIE_JAR:
        login()

    hangup_url = urljoin(BASE_API, f"vc/confs/{conf_id}/mts")

    params = {
        "mts": mt_list
    }

    data = {
        "params": json.dumps(params),
        "account_token": ACCOUNT_TOKEN
    }

    resp = requests.delete(hangup_url, data=data, headers={
        'Accept': 'application/json',
        "Content-Type": "application/x-www-form-urlencoded",
        "API-Level": '3'
    }, cookies=COOKIE_JAR)

    return check_response(resp, f"移除终端 {mt_list}")

# ======================
# 指定会议双流源
# ======================
def send_dual_stream(conf_id, mt_id):
    """
    指定会议双流源（异步操作）
    :param conf_id: 会议ID
    :param mt_id: 发双流的终端ID；为空则取消会议双流源
    """
    global ACCOUNT_TOKEN, COOKIE_JAR
    if not ACCOUNT_TOKEN or not COOKIE_JAR:
        login()

    # 接口URL
    stream_url = urljoin(BASE_API, f"vc/confs/{conf_id}/dualstream")

    params = {"mt_id": mt_id}
    data = {
        "params": json.dumps(params),
        "account_token": ACCOUNT_TOKEN
    }

    resp = requests.put(stream_url, data=data, headers={
        'Accept': 'application/json',
        "Content-Type": "application/x-www-form-urlencoded",
        "API-Level": '3'
    }, cookies=COOKIE_JAR)

    return check_response(resp, "指定会议双流源")



# ======================
# 取消会议双流源
# ======================
def stop_dual_stream(conf_id, mt_id):
    """
    取消会议双流源（异步操作）
    :param conf_id: 会议ID
    :param mt_id: 要取消双流的终端ID
    """
    global ACCOUNT_TOKEN, COOKIE_JAR
    if not ACCOUNT_TOKEN or not COOKIE_JAR:
        login()

    stream_url = urljoin(BASE_API, f"vc/confs/{conf_id}/dualstream")

    # DELETE 请求允许带参数（部分接口要求附带双流源终端）
    params = {
        "mt_id": mt_id
    }
    data = {
        "params": json.dumps(params),
        "account_token": ACCOUNT_TOKEN
    }

    resp = requests.delete(stream_url, data=data, headers={
        'Accept': 'application/json',
        "Content-Type": "application/x-www-form-urlencoded",
        "API-Level": '3'
    }, cookies=COOKIE_JAR)

    return check_response(resp, "取消会议双流源")



# ======================
# 结束会议
# ======================
def end_conference(conf_id):
    global ACCOUNT_TOKEN, COOKIE_JAR
    if not ACCOUNT_TOKEN or not COOKIE_JAR:
        login()

    end_url = urljoin(BASE_API, f"mc/confs/{conf_id}")
    params = {"account_token": ACCOUNT_TOKEN}

    resp = requests.delete(end_url, params=params, headers={
        'Accept': 'application/json',
        "API-Level": '3'
    }, cookies=COOKIE_JAR)

    return check_response(resp, "结束会议")


# ======================
# 测试用例
# ======================
if __name__ == '__main__':
    try:
        print("=== 登录系统 ===")
        login_result = login()

        print("\n=== 创建会议 ===")
        create_result = create_conference(
            name="应急调度会议",
            start_time=datetime.now() + timedelta(minutes=10),
            location="指挥中心A",
            duration=180
        )
        conf_id = create_result.get("conf_id")
        if not conf_id:
            raise Exception("创建会议返回中未找到 conf_id")

        print(f"\n✅ 会议创建成功，ID: {conf_id}")

        print("\n=== 获取所有账号信息 ===")
        get_all_accounts(0, 5)

        print("\n=== 根据账号名获取账号信息 ===")
        get_all_accounts(0, 5, account_filter="yx1")

        print("\n=== 包含某个别名的账号信息 ===")
        search_accounts_by_alias("wgh")

        print("\n=== 添加终端 ===")
        # mt_list = [
        #     {
        #         "account": "5406260000002",
        #         "account_type": 5,
        #         "bitrate": 2048,
        #         "protocol": 1,
        #         "forced_call": 0,
        #         "call_mode": 0
        #     },
        #     {
        #         "account": "5406260000209",
        #         "account_type": 5,
        #         "bitrate": 2048,
        #         "protocol": 1,
        #         "forced_call": 0,
        #         "call_mode": 0
        #         }
        #     ]
        mt_list = [
            {
                "account": "5406260000009",
                "account_type": 5,
                "bitrate": 2048,
                "protocol": 1,
                "forced_call": 0,
                "call_mode": 0
            }
        ]

        mt_list = [{"account": "5406260000209", "account_type": 5, "bitrate": 2048, "protocol": 1, "forced_call": 0, "call_mode": 0}]

        invite_mt(conf_id, mt_list)

        print("\n=== 指定会议双流源 ===")
        send_dual_stream(conf_id, "1")

        print("\n=== 取消会议双流源 ===")
        stop_dual_stream(conf_id, "1")

        print("\n=== 获取与会终端列表 ===")
        get_mts_in_meetings(conf_id)

        print("\n=== 移除终端 ===")
        mt_list = [
            {"mt_id": "1"}
        ]
        hangup_mt(conf_id, mt_list)

        print("\n=== 结束会议 ===")
        end_conference(conf_id)

        print("\n🎯 全部测试执行完成！")

    except Exception as e:
        print(f"\n❌ 测试执行出错: {e}")
        end_conference(conf_id)
