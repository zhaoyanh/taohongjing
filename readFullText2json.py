import os
import json

def 读取全文并转换为json():
    数据目录 = 'data/第二批数据/全文'
    所有文件数据 = []

    for 文件名 in os.listdir(数据目录):
        if 文件名.endswith('.txt'):
            文件路径 = os.path.join(数据目录, 文件名)
            
            with open(文件路径, 'r', encoding='utf-8') as 文件:
                内容 = 文件.read()
            
            句子列表 = 内容.split('。')
            
            文件数据 = [{"text": 句子.strip()} for 句子 in 句子列表 if 句子.strip()]

            
            所有文件数据.extend(文件数据)

    with open(数据目录+'/'+'pretrain.json', 'w', encoding='utf-8') as json文件:
        json.dump(所有文件数据, json文件, ensure_ascii=False, indent=4)

    print("所有文件已处理完毕，数据已保存到 pretrain.json")

读取全文并转换为json()
