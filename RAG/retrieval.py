import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .embedding import get_sentence_embedding, load_embedding_models
import json


# 这段代码定义了一个异步函数 query_embedding，该函数的目的是根据给定的查询文本（query），
# 通过与一个 DataFrame 中的文本数据计算相似度，返回按相似度排序的结果
async def query_embedding(query, df):
    model_state = await load_embedding_models()
    query_emb = await get_sentence_embedding(query, model_state)

    # Convert to numpy array and reshape to (1, -1)
    query_emb = np.array(query_emb.tolist()).reshape(1, -1)

    embeddings = []

    # Iterate over DataFrame rows and compute similarities
    for index, row in df.iterrows():
        emb_vector = np.array(row['text']).reshape(1, -1)
        # row['similarity'] = ...：为每一行添加一个新的列 'similarity'，用于存储该行与查询文本的相似度。
        row['similarity'] = cosine_similarity(query_emb, emb_vector)[0][0]
        embeddings.append(row)

    # Sort embeddings by similarity
    # 对 embeddings 列表按每行的 'similarity' 值进行降序排序（reverse=True）。这会将最相似的文本排在前面。
    sorted_embeddings = sorted(embeddings, key=lambda x: x['similarity'], reverse=True)
    return sorted_embeddings
