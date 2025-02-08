import numpy as np
import torch
from transformers import BertModel, BertTokenizer, BertConfig
import os
import asyncio


# 异步加载 BERT 模型和分词器。
# 通过分词器将输入文本分割成 BERT 能理解的 Token。
# 使用 BERT 推理获取文本的隐藏状态。
# 提取 [CLS] Token 的向量作为文本的嵌入表示。


# 使用异步方式加载文件。
# torch.load 通常用于加载 PyTorch 模型文件。
# 文件加载是在异步任务中通过 run_in_executor 完成，避免阻塞主线程。
async def load_file_async(path):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, torch.load, path, torch.device('cpu'))


# 获取当前脚本所在的路径。
# 定位到 model 子目录，该目录存放模型相关文件（权重、配置和词汇表）。
async def load_embedding_models():
    base_path = os.path.dirname(__file__)  # 获取当前文件的目录
    path = os.path.join(base_path, 'model')

    # 定义文件路径
    # pytorch_model.bin: 模型权重文件，包含 BERT 的参数。
    # config.json: 配置文件，定义了模型的结构（例如层数、隐藏维度、注意力头数）。
    # vocab.txt: 词汇表，用于将文本分词。
    model_path = os.path.join(path, 'pytorch_model.bin')
    config_path = os.path.join(path, 'config.json')
    vocab_path = os.path.join(path, 'vocab.txt')

    # 加载配置文件
    config = BertConfig.from_pretrained(config_path)

    # 初始化模型
    model = BertModel(config)

    # 异步加载模型权重
    state_dict = await load_file_async(model_path)
    model.load_state_dict(state_dict)

    # 加载分词器
    tokenizer = BertTokenizer(vocab_file=vocab_path)
    return {"model": model, "tokenizer": tokenizer}


# 该函数的目的是从输入的文本中获取其嵌入表示，通常是用于下游任务（如文本分类、情感分析等）。
# 通过调用预训练的语言模型（例如 BERT、RoBERTa 等），它获取了文本的 CLS token 向量，通常用来表示该文本的整体语义。
# async def get_sentence_embedding(text, emb_model):
#     inputs = emb_model["tokenizer"](text, return_tensors='pt')
#     with torch.no_grad():
#         outputs = emb_model["model"](**inputs)
#     # 获取 [CLS] token 的向量
#     cls_embedding = outputs.last_hidden_state[:, 0, :].numpy()
#     # 轉數組
#     # embedding = np.array(cls_embedding).tolist()[0][:128]
#     # 最后返回[CLS]嵌入向量
#     return cls_embedding


# 示例用法
# async def main():
#     emb_model = await load_embedding_models()
#     embedding = await get_sentence_embedding("This is a test sentence.", emb_model)
#     print(embedding)
#
# asyncio.run(main())


# 获取句子的嵌入表示
async def get_sentence_embedding(text, emb_model):
    inputs = emb_model["tokenizer"](text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = emb_model["model"](**inputs)
    cls_embedding = outputs.last_hidden_state[:, 0, :].numpy()  # 获取 [CLS] token 的向量
    return cls_embedding


# 分块长文本
def chunk_text(text, chunk_size=512):
    # 按照 chunk_size 分块，避免文本太长超过模型的最大输入限制（如 BERT 是 512）
    words = text.split()
    chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]
    return [' '.join(chunk) for chunk in chunks]


# 主函数：分块处理长文本
async def process_long_text(text, emb_model):
    # 将长文本分块
    chunks = chunk_text(text)

    # 获取每个块的嵌入
    embeddings = await asyncio.gather(*(get_sentence_embedding(chunk, emb_model) for chunk in chunks))

    # 返回所有块的嵌入
    return np.array(embeddings).reshape(-1, 768)  # 假设 [CLS] 的向量维度为 768


# 示例使用
async def main():
    emb_model = await load_embedding_models()  # 加载模型和分词器
    long_text = """候鸟名称":"三宝鸟","栖息地_位置":"山地或平原林中，林区边缘空旷处或林区里的开垦地、山地或平原林中，林区边缘空旷处或林区里的开垦地上、山地或平原林中，
    林区边缘空旷处或林区里的开垦地上","栖息地_时间":"早、晚活动频繁，天气较热时、早、晚活动频繁，天气较热时栖息在密林中的乔木上或较开阔处的大树梢处、
    早、晚活动频繁，天气较热时","栖息地_类型":"密林中的乔木，较开阔处的大树梢、林区，林区边缘空旷处，开垦地、林区、密林中的乔木，较开阔处的大树梢","栖息地_面积":"50平方公里"
    ,"栖息地_分布":"分布广泛，但并不常见、分布广泛、分布广泛，但并不常见","栖息地_食物丰富度":"丰富，主要为昆虫、小型无脊椎动物和果实","栖息地_质量":
    "最适宜生境","种群分布_分布格局":"东南亚、南亚、澳大利亚北部","种群分布_时空动态":"三宝鸟主要分布于东南亚和南亚地区，包括印度、斯里兰卡、泰国、马来西亚、印度尼西亚等地。
    它们通常在热带雨林、次生林和林缘地带活动。三宝鸟的种群分布随季节变化不大，但在某些地区可能会有局部迁徙行为，例如在雨季和旱季之间进行短距离移动。","种群分布_扩散现状
    ":"三宝鸟主要分布于东南亚、南亚和澳大利亚等地，包括印度、斯里兰卡、泰国、马来西亚、印度尼西亚、菲律宾、新几内亚和澳大利亚北部。它们通常栖息在热带雨林、次生林、果园和农田附近。
    三宝鸟的种群分布较为广泛，但具体扩散现状可能因地区和环境变化而有所不同。在一些地区，由于森林砍伐和栖息地破坏，三宝鸟的种群数量可能有所下降。然而，在其他地区，
    由于保护措施的实施，种群数量可能保持稳定或有所增加。总体而言，三宝鸟的种群分布扩散现状较为复杂，需要进一步的监测和研究。","数量_水鸟总数量":"未提及",
    "数量_种群数量":"未提及","数量_重要物种的性比":"未知","数量_重要物种的成幼比":"未提及","行为_迁徙":"迁徙鸟","行为_迁移":"东南亚至澳大利亚",
    "行为_觅食":"在空中来回旋转，通过不停地飞翔捕食，速度较快，猎获昆虫之后复返原来枝桠","行为_节律":"早、晚活动频繁、早、晚活动频繁，天气较热时、早、晚活动频繁"
    ,"行为_繁殖":"三宝鸟主要在热带和亚热带地区繁殖，通常在树洞或人工巢箱中筑巢。它们的繁殖季节通常在春季，每窝产卵2-4枚，由雌鸟负责孵化，孵化期约为14-16天。
    雏鸟出生后由双亲共同喂养，大约3周后雏鸟可以离巢。","行为_人鸟冲突":"三宝鸟在迁徙过程中可能会进入人类居住区寻找食物和栖息地，导致与人类的冲突。
    例如，它们可能会在农田、果园或城市公园中觅食，影响农作物和园艺植物的生长，也可能在建筑物上筑巢，引发卫生和安全问题。",
    "特征_体型":"中等体型，约25-30厘米，体态优美，羽毛鲜艳","特征_大小":"中等体型","特征_体色":"嘴鲜红，脚亦红色，身体蓝绿色",
    "特征_生态型":"热带雨林","特征_鸣声":"三宝鸟的鸣声清脆悦耳，通常在清晨和黄昏时分最为活跃，鸣叫声类似‘啾啾’或‘啾-啾-啾’，有时还会发出类似哨声的高音调鸣叫。"  # 示例长文本"""

    # 处理长文本并获取每个块的嵌入
    embeddings = await process_long_text(long_text, emb_model)
    print(embeddings)


# 启动异步任务
# asyncio.run(main())
