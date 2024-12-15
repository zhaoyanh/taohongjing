import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm
import csv
import json

def build_triples(input_file, output_file):
    # Load the local model and tokenizer
    model_name = "models/internlm-xcomposer2-7b"
    model_path = "/root/models/internlm-xcomposer2-7b"
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True).half().cuda()

    triples = []

    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in tqdm(data, desc="Processing items"):
        text = item['text']
        prompt = f"""
请从以下文本中提取三元组（head，head_type，tail,tail_type,relation,properties）：
head是头节点 head_type是头节点类型 tail是尾节点 tail_type是尾节点类型 relation是头节点与尾节点的关系 properties是这个关系的特性
使用键值对的方式描述
{text}
要求：
1. head和tail应为实体，relation应为它们之间的关系
2. 尽可能多地提取有意义的三元组
3. 输出格式为：（head，head_type，tail,tail_type,relation,properties）
4. 每个三元组单独一行
"""

        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=512)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract triples from the response
        item_triples = []
        for line in response.split('\n'):
            if line.startswith('(') and line.endswith(')'):
                triple = eval(line)
                if len(triple) == 3:
                    item_triples.append({
                        'head': triple[0],
                        'head_type': triple[1],
                        'tail': triple[2],
                        'tail_type':  triple[3],
                        'relation':  triple[4],
                        'properties':  triple[5],
                    })
        
        if item_triples:
            triples.append({
                'text': text,
                'triples': item_triples
            })

    # Write results to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(triples, f, ensure_ascii=False, indent=2)

    print(f"Triples have been saved to {output_file}")

# Update the main function if needed
if __name__ == "__main__":
    input_file = '/root/pretraindata.json'
    output_file = 'triples_output.json'
    build_triples(input_file, output_file)

# def build_triples(input_file, output_file):
#     # Load the local model and tokenizer
#     model_name = "XTuner/merged01"
#     model_path = "/root/models/internlm-xcomposer2-7b"
#     tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
#     model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True).half().cuda()

#     triples = []

#     # Read input file
#     with open(input_file, 'r', encoding='utf-8') as f:
#         reader = csv.DictReader(f)
#         rows = list(reader)

#     for row in tqdm(rows, desc="Processing rows"):
#         text = row['text']
#         prompt = f"""
# 请从以下文本中提取三元组（主体，关系，客体）：
# {text}
# 要求：
# 1. 主体和客体应为实体，关系应为它们之间的联系
# 2. 尽可能多地提取有意义的三元组
# 3. 输出格式为：(主体, 关系, 客体)
# 4. 每个三元组单独一行
# """

#         inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
#         with torch.no_grad():
#             outputs = model.generate(**inputs, max_new_tokens=512)
#         response = tokenizer.decode(outputs[0], skip_special_tokens=True)

#         # Extract triples from the response
#         for line in response.split('\n'):
#             if line.startswith('(') and line.endswith(')'):
#                 triple = eval(line)
#                 if len(triple) == 3:
#                     triples.append({
#                         'id': row['id'],
#                         'text': text,
#                         '主体': triple[0],
#                         '关系': triple[1],
#                         '客体': triple[2]
#                     })

#     # Write results to output file
#     with open(output_file, 'w', newline='', encoding='utf-8') as f:
#         writer = csv.DictWriter(f, fieldnames=['id', 'text', '主体', '关系', '客体'])
#         writer.writeheader()
#         writer.writerows(triples)

#     print(f"Triples have been saved to {output_file}")

# if __name__ == "__main__":
#     input_file = '/root/pretraindata.json'
#     output_file = 'triples_results.csv'
#     build_triples(input_file, output_file)
