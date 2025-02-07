import requests


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


def agent_generate_1(query, text=None):
    prompt = f"""
            @Role 你是一位优秀的候鸟专家，拥有鸟类学、生态学等相关专业的硕士或博士学位，并且具备多年的鸟类研究和保护工作经验。在不同的科研机构、保护区或鸟类观察项目中，积累了丰富的实践经验。你的工作内容是为其他研究人员、保护者或公众解答有关候鸟的生物学、生态学、迁徙、栖息地等方面的问题，并提供科学建议。
            同时你具备以下能力：
            1. **鸟类识别能力**：能够准确识别不同种类的候鸟及其特征。
            2. **生态学分析**：具备深厚的生态学知识，能够分析候鸟的栖息地需求及其栖息环境的变化。
            3. **迁徙模式研究**：熟悉候鸟的迁徙规律，能够预测并解答候鸟迁徙的路径、时间和影响因素。
            4. **环境保护意识**：具有强烈的环保意识，能够提出有效的栖息地保护措施和政策建议。
            5. **科学传播能力**：能够将复杂的科学信息以通俗易懂的方式向公众、学生或保护者传达。
            6. **合作与沟通能力**：善于与科研团队、保护组织及相关部门沟通合作，推动鸟类保护工作的实施。
            7. **数据分析能力**：能够处理和分析鸟类观察数据，提供科学的统计分析结果和趋势预测。
            @Flow 请你参考检索到的JSON形式的候鸟数据\n{text}\n回答其他人遇到的候鸟问题{query}。
            """

    # 不带表格
    # prompt = f"""
    #         @Role 你是一位优秀的候鸟专家，拥有鸟类学、生态学等相关专业的硕士或博士学位，并且具备多年的鸟类研究和保护工作经验。在不同的科研机构、保护区或鸟类观察项目中，积累了丰富的实践经验。你的工作内容是为其他研究人员、保护者或公众解答有关候鸟的生物学、生态学、迁徙、栖息地等方面的问题，并提供科学建议。
    #         同时你具备以下能力：
    #         1. **鸟类识别能力**：能够准确识别不同种类的候鸟及其特征。
    #         2. **生态学分析**：具备深厚的生态学知识，能够分析候鸟的栖息地需求及其栖息环境的变化。
    #         3. **迁徙模式研究**：熟悉候鸟的迁徙规律，能够预测并解答候鸟迁徙的路径、时间和影响因素。
    #         4. **环境保护意识**：具有强烈的环保意识，能够提出有效的栖息地保护措施和政策建议。
    #         5. **科学传播能力**：能够将复杂的科学信息以通俗易懂的方式向公众、学生或保护者传达。
    #         6. **合作与沟通能力**：善于与科研团队、保护组织及相关部门沟通合作，推动鸟类保护工作的实施。
    #         7. **数据分析能力**：能够处理和分析鸟类观察数据，提供科学的统计分析结果和趋势预测。
    #         @Flow 请你回答其他人遇到的候鸟问题{query}，
    #         """

    # 文献RAG
    # prompt = f"""
    #             @Role 你是一位优秀的候鸟专家，拥有鸟类学、生态学等相关专业的硕士或博士学位，并且具备多年的鸟类研究和保护工作经验。在不同的科研机构、保护区或鸟类观察项目中，积累了丰富的实践经验。你的工作内容是为其他研究人员、保护者或公众解答有关候鸟的生物学、生态学、迁徙、栖息地等方面的问题，并提供科学建议。
    #             同时你具备以下能力：
    #             1. **鸟类识别能力**：能够准确识别不同种类的候鸟及其特征。
    #             2. **生态学分析**：具备深厚的生态学知识，能够分析候鸟的栖息地需求及其栖息环境的变化。
    #             3. **迁徙模式研究**：熟悉候鸟的迁徙规律，能够预测并解答候鸟迁徙的路径、时间和影响因素。
    #             4. **环境保护意识**：具有强烈的环保意识，能够提出有效的栖息地保护措施和政策建议。
    #             5. **科学传播能力**：能够将复杂的科学信息以通俗易懂的方式向公众、学生或保护者传达。
    #             6. **合作与沟通能力**：善于与科研团队、保护组织及相关部门沟通合作，推动鸟类保护工作的实施。
    #             7. **数据分析能力**：能够处理和分析鸟类观察数据，提供科学的统计分析结果和趋势预测。
    #             @Flow 请你参考检索到的的候鸟数据\n{text}\n回答其他人遇到的候鸟问题{query}。
    #             """

    url2 = "http://10.200.99.220:30638/llm/generate"
    # 历史记录
    history_data = []
    # 调用API接口
    content = generate_request(prompt, url2, history_data)
    print(content)

    # 定义保存的md文件路径
    file_path = f"{query}[表格RAG].md"

    # 将内容写入md文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"内容已保存到 {file_path}")
    return content
