from ..models.base import BaseChat


class Qwen2_72B_Chat(BaseChat):
    def __init__(self, model_name="qwen2.5-72b-20250730", base_url="https://10.114.165.100:443/api/publishaddress/inference/c5f6eb95/v1/chat/completions",
                 temperature=0.1, top_p=0.9, retry_times=3, system_prompt="", concurrency_limit=5, api_key="ujeVSpFKas3BQ5gL2mJ0RzEfqhWvl1HrNUbYMwcID6987Cx4"):
        super().__init__(
            model_name=model_name,
            base_url=base_url,
            temperature=temperature,
            top_p=top_p,
            retry_times=retry_times,
            system_prompt=system_prompt,
            concurrency_limit=concurrency_limit,
            api_key=api_key
        )


if __name__ == '__main__':
    system_prompt = "你是人工智能助手"
    user_prompt = "常见的十字花科植物有哪些？"
    resp = Qwen2_72B_Chat().chat(system_prompt, user_prompt)
    print(resp)