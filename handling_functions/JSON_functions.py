import json


# 读取JSON文件
def read_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


# 通过字符串数字ID，读取当前鸟类的JSON数据
def read_current_process(file_path, current_id):
    data = read_json_data(file_path)
    # current_process_data = data["到期号码续费"][current_id]
    current_process_data = data[current_id]
    return current_process_data




