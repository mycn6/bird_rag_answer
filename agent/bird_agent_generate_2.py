# -*- coding: utf-8 -*-
import requests
import time


def extract_page_content(data):
    """
    从返回数据中提取 `page_content` 字段值。
    :param data: API响应数据，JSON格式
    :return: 包含所有 `page_content` 的列表
    """
    page_contents = []
    if "data" in data and "final" in data["data"]:
        final_list = data["data"]["final"]
        for item in final_list:
            if isinstance(item, list) and len(item) > 0 and "page_content" in item[0]:
                page_contents.append(item[0]["page_content"])
    return page_contents


def send_request(url, headers, query, path_list, is_team=True, is_china=False, top_k=4):
    """
    发送POST请求至API。
    :param url: API的URL地址
    :param headers: 请求头部信息，包含 `Content-Type` 和 `Authorization`
    :param query: 查询的关键词
    :param path_list: 文件夹路径列表
    :param is_team: 是否为团队（默认为True）
    :param is_china: 是否为中国环境（默认为False）
    :param top_k: 返回结果的数量（默认为8）
    :return: 响应数据，JSON格式
    """
    data = {
        "query": query,
        "pathList": path_list,
        "isTeam": is_team,
        "isChina": is_china,
        "topK": top_k
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        time.sleep(40)  # 请求成功后添加延迟
        if response.status_code == 200:
            return response.json()
        else:
            print(f"请求失败: 状态码 {response.status_code}")
            print("响应内容:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print("请求过程中出现错误:", str(e))
        return None


def process_api_response(url, headers, query, path_list, is_team=True, is_china=False, top_k=8):
    """
    处理API响应并提取 `page_content` 字段值。
    :param url: API的URL地址
    :param headers: 请求头部信息，包含 `Content-Type` 和 `Authorization`
    :param query: 查询的关键词
    :param path_list: 文件夹路径列表
    :param is_team: 是否为团队（默认为True）
    :param is_china: 是否为中国环境（默认为False）
    :param top_k: 返回结果的数量（默认为8）
    :return: 返回值:page_content，直接打印 `page_content`
    """
    response_data = send_request(url, headers, query, path_list, is_team, is_china, top_k)

    if response_data:
        page_contents = extract_page_content(response_data)
        # for i, content in enumerate(page_contents, 1):
        #     print(f"Page Content {i}:{content}\n")
        #     print("====================================")
        return page_contents


def generate_request(prompt, url=None, history=None):
    # 检查输入是否符合要求
    if not url:
        raise ValueError("必须提供  API 的 url 参数。")

    # 准备 API 请求数据
    data = {
        "input": prompt,
        "history": history or [],
        "serviceParams": {
            "maxContentRound": 0,
            "maxOutputLength": 8192,
            "maxWindowSize": 500,
            "stream": False,
            "system": "假如你是一个地理方面的专家，你可以根据我提供的数据，将数据中出现的鸟识别出来。",
            "promptTemplateName": "geogpt",
            "generateStyle": "chat",
        },
        "modelParams": {
            "best_of": 1,
            "temperature": 0.2,
            "use_beam_search": False,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0,
            "top_p": 1.0,
            "top_k": -1,
            "length_penalty": 1.0,
        },
    }

    # 设置请求头
    headers = {"Content-Type": "application/json"}

    try:
        # 发送 POST 请求
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()

        # 解析响应数据
        response_data = response.json()
        output_text = response_data.get('data', {}).get('output', "")
        # 保存结果到 Markdown 文件
        # with open("候鸟信息.md", "w", encoding="utf-8") as file:
        #     file.write(output_text)
        return output_text

    except requests.exceptions.RequestException as e:
        return f"请求失败: {e}"
    except KeyError:
        return "响应格式不正确，无法提取 output 数据。"


def agent_generate_2(query):
    # 用户输入要查询的问题
    question = query

    # 调用新API生成候鸟column_name的字典
    url = ["https://geogpt-portal.zero2x.org.cn:8443/be-api/service/api/rag/top_k",
           "https://geogpt.zero2x.org/be-api/service/api/rag/top_k"]
    headers = {
        "Content-Type": "application/json",
        # 国内
        # "Authorization": "Bearer 11cf50f86a6b416498baf20a9252bb16"
        # 国际
        "Authorization": "Bearer 6001818e1ec04cff85b3b0030f2c41467"
    }
    # 国内
    # path_list = ["/test/"]
    # is_china = True
    # 国际
    path_list = ["/birds in china/", "/birds in world/"]
    is_china = False
    # 使用国际账号下的文献，检索
    data_list = process_api_response(url[1], headers, question, path_list, is_team=True, is_china=is_china,
                                     top_k=1)
    # 调用问答API对问题进行回答
    # 传入问答的API endpoint，需要替换为实际的 URL
    url2 = "http://10.200.99.220:30638/llm/generate"
    # 历史记录
    history_data = []

    # 构造提示词
    prompt = f"""
    请根据以下提供的候鸟信息数据列表，对回答回答问题并提供明确的答案。  

    ### 数据列表  
    {data_list}

    ### 问题  
    {question}


    ### 任务要求  
    1.详细回答问题
     
    2.仔细阅读数据列表，并根据问题中的需求查找相关信息,并进行回答

    """
    # 调用API接口
    answer = generate_request(prompt, url2, history_data)
    print(answer)

    # 定义保存的md文件路径
    file_path = f"{query}[文献RAG].md"

    # 将内容写入md文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(answer)

    print(f"内容已保存到 {file_path}")

    return answer
