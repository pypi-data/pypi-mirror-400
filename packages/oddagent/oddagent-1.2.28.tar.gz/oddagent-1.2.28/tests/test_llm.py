# -*- coding: utf-8 -*-

import requests

'''
with open("../llm/apikey_iflow.txt", "r", encoding='utf-8') as f: #api_key
    api_key = f.read()
    print("api_key:", api_key)
base_url = 'https://apis.iflow.cn/v1/chat/completions'
model_id = "qwen3-max"
'''
api_key = 'sk-d8f0024e2d874a7dac8324538ecf2e6c'
base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
model_id = "qwen3-max"

base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
base_url = "http://172.16.225.149:19025/v1/chat/completions"
model_id = "qwen3-4b-instruct"


# curl http://172.16.226.101:19025/generate \
# -header "content-Type: application/json" \
# -H "Authorization: Bearer $api_key" \
# -d '{"model": "qwen3-4b-instruct", "messages": [{"role": "user", "content": "请介绍一下自己"}], "max tokens": 20}'

def test_openai_chat_completion():
    from openai import OpenAI
    client = OpenAI(base_url=base_url, api_key=api_key)

    completion = client.chat.completions.create(
        model=model_id,
        messages=[{"role": "user", "content": "Hello!"}]
    )

def test_chat_completion():
    from openai import OpenAI

    client = OpenAI(
        base_url="http://172.16.225.149:19025/v1",
        api_key="na"
    )

    SYSTEM_PROMPT = ""

    text = "你是谁"
    response = client.chat.completions.create(
        model="qwen",  
        messages=[{"role": "user", "content": text}],
        temperature=0.0,
        max_tokens=1000
    )

    print(response.choices[0].message.content) 


def test_http_chat_completion():
    # header信息 Authorization的值为实际的Token
    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key
    }

    # 根据具体模型要求的数据格式构造服务请求。
    data = {
        "model": model_id,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "你好！/no_think"
            }
        ]
    }

    base_url = "http://172.16.225.149:19025/generate"

    # 发送请求
    resp = requests.post(base_url, json=data, headers=headers)
    print(resp)
    print("内容：")
    print(resp.content.decode('utf-8'))

# test_openai_chat_completion()
# test_http_chat_completion()
test_chat_completion()