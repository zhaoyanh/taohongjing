import os
import pickle
import json
import requests
import re
def 读取pkl文件(文件路径):
    with open(文件路径, 'rb') as f:
        return pickle.load(f)

def 获取所有Title值(数据,typeC):
    Title值列表 = []
    if typeC == 'All':
        for 项目 in 数据:
            if isinstance(项目, dict):
                Title值列表.append(str(项目.items()))
    else:
        
        for 项目 in 数据:
            if isinstance(项目, dict) and typeC in 项目.keys():
                Title值列表.append(项目[typeC])
    return Title值列表

def 调用大模型(文本):
    提示词 = "你是一位资深语言学工程师，对命名实体识别和关系抽取有深入研究，又精通医学、药学、中医药学，尤其擅长皮肤科疾病的诊治，请识别这句话中的实体词，实体词所属类别以及他们之间的关系，以json格式返回结果"
    # 这里需要替换为实际的大模型API调用代码
    # 以下为示例代码，实际使用时需要根据具体的API进行修改
    
    url = "https://api.siliconflow.cn/v1/chat/completions"

    payload = {
        
        "model": "deepseek-ai/DeepSeek-V2-Chat",
        "messages": [
            {
                "role": "user",
                "content": f"{提示词}\n\n文本：{文本}"
            }
        ],
        "stream": False,
        "max_tokens": 512,
        "stop": ["<string>"],
        "temperature": 0.1,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "json_object"}
    }
    headers = {
        "Authorization": "Bearer sk-kanktzjwuzjczhryjjuljbqsqnfjqlxflggvxkvlzmiacziu",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    #print(response.text)
    '''
    url = "http://10.100.4.15:8080/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "prompt": f"{提示词}\n\n文本：{文本}",
        "max_tokens": 150
    }
    response = requests.post(url, headers=headers, json=data)
    '''
    if response.status_code == 200 and response.text != None and response.text != "":
        return json.loads(response.text)['choices'][0]['message']['content']
    else:
        return None

def 处理pkl文件(filename,typeC):
    pkl目录 = 'pkl'
    实体关系列表 = []
    for 文件名 in os.listdir(pkl目录):
        
        if 文件名.endswith('.pkl') and 文件名 == filename:
            文件路径 = os.path.join(pkl目录, 文件名)
            数据 = 读取pkl文件(文件路径)
            Title值列表 = 获取所有Title值(数据,typeC)
            
            for Title值 in Title值列表:
                结果 = 调用大模型(Title值)
                print(f"文件：{文件名}, typeC：{Title值}")
                print(结果,type(结果))
                if 结果:
                    try:
                        # 尝试直接解析JSON字符串
                        结果字典 = json.loads(结果)
                    except json.JSONDecodeError:
                        
                        结果字典 = None                    
                    if 结果字典:
                        结果字典[typeC] = Title值
                        print(f"转换后的字典：{结果字典}")
                        
                        实体关系列表.append(结果字典)
                        print(f"字典类型：{type(结果字典)}",结果字典.keys())
                else:
                    print("未获得有效结果")
                #print(f"识别结果：{json.dumps(结果, ensure_ascii=False, indent=2)}")
                print("---")
    # 将实体关系列表保存为pkl文件
    输出文件名 = filename[:-4]+'_实体关系_by'+typeC+'.pkl'
    with open(输出文件名, 'wb') as f:
        pickle.dump(实体关系列表, f)
    print(f"实体关系列表已保存到 {输出文件名}")



def 读取pkl文件111(file_path):
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
        total_records = len(data)
        print(f"总记录数：{total_records}")
        print("前10条记录：")
        for i, record in enumerate(data[:10], 1):
            print(f"记录{i}: {record}")

# INSERT_YOUR_CODE




if __name__ == "__main__":
    处理pkl文件('皮肤科知识库名医论文.pkl','All')
    #读取pkl文件111('pkl/皮肤科知识库名医.pkl')
    #读取pkl文件111('皮肤科知识库名医论文_实体关系_byAbstract.pkl')