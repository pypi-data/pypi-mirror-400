import json
import requests
import time
import threading
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class BaseChat:
    def __init__(self, model_name, base_url, temperature=0.1, top_p=0.9, retry_times=3, system_prompt="", concurrency_limit=5, api_key=""):
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = 20
        self.retry_times = retry_times
        self.system_prompt = system_prompt
        self.concurrency_limit = concurrency_limit
        self.semaphore = threading.Semaphore(concurrency_limit)
        self.headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            "Authorization": "Bearer " + api_key
        }

    def prepare_messages(self, system_prompt, user_prompt):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        return messages

    def prepare_payload(self, messages):
        payload = {
            "model": self.model_name,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "messages": messages
        }
        return payload

    def parse_response(self, response_json):
        return response_json['choices'][0]['message']['content']

    def chat(self, system_prompt, user_prompt):
        if system_prompt is None:
            system_prompt = self.system_prompt

        # 构造消息
        messages = self.prepare_messages(system_prompt, user_prompt)
        payload = self.prepare_payload(messages)
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')

        for attempt in range(self.retry_times):
            with self.semaphore:
                try:
                    response = requests.post(
                        self.base_url,
                        headers=self.headers,
                        data=data,
                        timeout=3000,
                        verify=False
                    )


                    response.raise_for_status()

                    # 尝试解析JSON
                    try:
                        response_json = response.json()
                    except Exception as je:
                        print("[ERROR] JSON解析失败:", je)
                        raise

                    try:
                        content = self.parse_response(response_json)
                    except KeyError as ke:
                        print("[ERROR] parse_response 阶段 KeyError:", ke)
                        raise
                    except Exception as pe:
                        print("[ERROR] parse_response 阶段其他异常:", pe)
                        raise

                    return content

                except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError, ValueError) as e:
                    print("[ERROR] 捕获的已知异常类型:", repr(e))
                    if attempt == self.retry_times - 1:
                        return f"Error: {str(e)}"
                    time.sleep(2 ** attempt)

                except Exception as e:
                    print("[ERROR] 捕获的未知异常类型:", repr(e))
                    if attempt == self.retry_times - 1:
                        return f"Error: {str(e)}"
                    time.sleep(2 ** attempt)

        return "Error: Max retries exceeded"