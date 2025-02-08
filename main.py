from fastapi import FastAPI
from handling_functions.JSON_functions import read_current_process
from handling_functions.query_handling import query_handling

from agent.bird_agent_generate_1 import agent_generate_1
from agent.bird_agent_generate_2 import agent_generate_2
import asyncio
import uvicorn

# 创建 FastAPI 实例
app = FastAPI()

json_file_path = "handling_functions/transformed_data.json"
vectorized_database_path = "handling_functions/bird_vector_database.csv"


def clean_bird_dict_data_skip_key(bird_data):
    """
    清理字典中的无效数据，遇到无效数据时跳过该键。
    """
    # 定义异常值集合
    invalid_values = ['未提及', '未知', '无', '', None]

    # 创建新的字典，跳过无效字段
    cleaned_data = {key: value for key, value in bird_data.items() if value not in invalid_values}

    return cleaned_data


# 表格RAG回答
@app.post("/table_rag_answer")
async def table_answer(query: str):
    text_id, text_similarity = await query_handling(query, vectorized_database_path)
    current_process_data = read_current_process(json_file_path, str(text_id))
    # content = agent_generate_1(query, current_process_data)
    clean_data = clean_bird_dict_data_skip_key(current_process_data)
    content = agent_generate_1(query, clean_data)
    return content


# 文献RAG回答
@app.post("/literature_rag_answer")
async def literature_rag_answer(query: str):
    # 调用API查询候鸟信息
    content = agent_generate_2(query)
    return content


# main 函数，用于启动 FastAPI 应用
def main():
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
