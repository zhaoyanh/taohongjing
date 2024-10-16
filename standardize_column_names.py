import os
import pickle
from collections import defaultdict

def 读取pkl文件(文件路径):
    with open(文件路径, 'rb') as f:
        return pickle.load(f)

def 转换为中文(键):
    # 这里可以添加更多的英文到中文的映射
    映射 = {
        'Title': '标题',
        'Author': '作者',
        'Date': '日期',
        # 添加更多映射...
    }
    return 映射.get(键, 键)

pkl目录 = 'pkl'
所有文件内容 = []
所有键值对 = defaultdict(set)

for 文件名 in os.listdir(pkl目录):
    if 文件名.endswith('.pkl'):
        文件路径 = os.path.join(pkl目录, 文件名)
        文件内容 = 读取pkl文件(文件路径)
        所有文件内容.append(文件内容)
        
        if 文件内容 and isinstance(文件内容[0], dict):
            第一个字典 = 文件内容[0]
            for 键, 值 in 第一个字典.items():
                中文键 = 转换为中文(键)
                所有键值对[中文键].add(str(值))

print("各文件第一行的键和值：")
for i, 文件内容 in enumerate(所有文件内容):
    if 文件内容 and isinstance(文件内容[0], dict):
        print(f"文件 {i+1}:")
        for 键, 值 in 文件内容[0].items():
            中文键 = 转换为中文(键)
            print(f"  {中文键}: {值}")
        print()

print("所有文件中的键和值的比较：")
for 键, 值集合 in 所有键值对.items():
    print(f"{键}:",len(键))
    '''
    if len(值集合) == 1:
        print(f"  所有文件相同: {list(值集合)[0]}")
    else:
        print(f"  不同值: {', '.join(值集合)}")
    print()

    '''


def 读取并修改pkl文件(文件路径):
    with open(文件路径, 'rb') as f:
        数据 = pickle.load(f)
    
    修改后数据 = []
    for 记录 in 数据:
        新记录 = {}
        for 键, 值 in 记录.items():
            if 键.startswith('Unnamed'):
                新记录['Unnamed'] = 值
            else:
                新记录[键] = 值
        修改后数据.append(新记录)
    
    return 修改后数据

def 保存pkl文件(数据, 文件路径):
    with open(文件路径, 'wb') as f:
        pickle.dump(数据, f)

文件名 = "皮肤科知识库师承.pkl"
pkl目录 = 'pkl'
输入文件路径 = os.path.join(pkl目录, 文件名)
输出文件路径 = os.path.join(pkl目录, "皮肤科知识库师承new.pkl")

if os.path.exists(输入文件路径):
    修改后数据 = 读取并修改pkl文件(输入文件路径)
    保存pkl文件(修改后数据, 输出文件路径)
    print(f"已将 '{文件名}' 中的 'Unnamed' 开头的键修改为 'Unnamed' 并保存为 '皮肤科知识库师承new.pkl'")
else:
    print(f"文件 '{文件名}' 不存在")


''' 
def 读取并修改pkl文件(文件路径):
    with open(文件路径, 'rb') as f:
        数据 = pickle.load(f)
    
    修改后数据 = []
    for 记录 in 数据:
        if 'Reference Type' in 记录.keys():
            记录['ReferenceType'] = 记录.pop('Reference Type')
        修改后数据.append(记录)
    
    return 修改后数据

def 保存pkl文件(数据, 文件路径):
    with open(文件路径, 'wb') as f:
        pickle.dump(数据, f)

文件名 = "皮肤科知识库名医论文.pkl"
pkl目录 = 'pkl'
文件路径 = os.path.join(pkl目录, 文件名)

if os.path.exists(文件路径):
    修改后数据 = 读取并修改pkl文件(文件路径)
    保存pkl文件(修改后数据, 文件路径+'.new')
    print(f"已将 '{文件名}' 中的 'Reference Type' 键修改为 'ReferenceType' 并保存")
else:
    print(f"文件 '{文件名}' 不存在")

 
import os
import re
  
def 合并特定pkl文件():
    合并数据 = []
    pkl目录 = 'pkl'
    文件名模式 = re.compile(r'^[\u4e00-\u9fa5]{2,3}\.pkl$')
    
    for 文件名 in os.listdir(pkl目录):
        if 文件名模式.match(文件名):
            文件路径 = os.path.join(pkl目录, 文件名)
            文件内容 = 读取pkl文件(文件路径)
            合并数据.extend(文件内容)
    
    输出文件路径 = os.path.join(pkl目录, "皮肤科知识库名医论文.pkl")
    print(合并数据)
    with open(输出文件路径, 'wb') as f:
        pickle.dump(合并数据, f)
    
    print(f"已将符合条件的文件内容合并并保存到 {输出文件路径}")

合并特定pkl文件()
'''