import json
import asyncio
import pandas as pd
import numpy as np
from RAG.retrieval import query_embedding


def json_to_numpy(json_str):
    return np.array(json.loads(json_str))


async def find_most_similar(query, df):
    sorted_embeddings = await query_embedding(query, df)
    if sorted_embeddings:
        most_similar = sorted_embeddings[0]
        return most_similar['鸟名'], most_similar['similarity']
    return None, None


# 检索
async def query_handling(query, vectorized_csv_file):
    df = pd.read_csv(vectorized_csv_file)

    # 将每个嵌入列转换为 NumPy 数组
    for column in df.columns:
        if column == "text":
            df[column] = df[column].apply(json_to_numpy)

    most_similar_id, most_similar_similarity = await find_most_similar(query, df)
    return most_similar_id, most_similar_similarity


