from transformers import AutoTokenizer, AutoModelForCausalLM
import csv
from tqdm import tqdm
import torch

# 2. 错误处理：可以在关键操作处添加异常处理
def perform_ner_with_model(text, model, tokenizer):
    try:
        prompt = f"""
        - Role: 医学文本分析专家和自然语言处理工程师
        - Background: 用户需要处理医学领域的文本数据，从测试集中抽取方剂、中药、疾病、临床表现、证候、治法等六类命名实体。
        - Profile: 你是一位专注于医学文本分析的专家，对医学术语和实体识别有深入的理解和实践经验，擅长运用自然语言处理技术来识别和分类医学领域的特定实体。
        - Skills: 你具备医学知识、自然语言处理技术、机器学习算法和编程能力，能够设计和实现高效的命名实体识别系统。
        - Goals: 开发一个能够准确识别医学文本中特定实体的系统，提高医学研究和临床决策的效率。
        - Constrains: 该系统应能够处理大量医学文本数据，识别准确率高，且能够适应不断更新的医学知识库。
        - OutputFormat: 输出应包括实体类型、实体名称、在文本中的位置以及可能的实体链接。
        - Workflow:
        1. 对医学文本进行预处理，包括分词、去除停用词等。
        2. 使用机器学习模型对文本中的实体进行识别和分类。
        3. 对识别出的实体进行验证和修正，确保高准确率。
        - Examples:
        - 例子1：文本中包含“桂枝茯苓丸”，识别为方剂。
        - 例子2：文本中提到“人参”，识别为中药。
        - 例子3：文本中描述“高血压”，识别为疾病。
        - 例子4：文本中出现“发热”，识别为临床表现。
        - 例子5：文本中提到“气虚”，识别为证候。
        - 例子6：文本中描述“补气法”，识别为治法。
        请识别以下文本中的实体，并标注其类型（方剂、中药、疾病、临床表现、证候、治法）。格式为：实体|类型。\n\n文本：{text}\n\n实体列表：
        """
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=512)
        ner_result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        entities = []
        for line in ner_result.split('\n'):
            if '|' in line:
                entity, entity_type = line.strip().split('|')
                entities.append((entity.strip(), entity_type.strip()))
        
        return entities
    except Exception as e:
        print(f"Error in perform_ner_with_model: {e}")
        return []

# 3. 性能优化：可以考虑使用批处理来提高处理速度
def perform_ner(input_file, output_file, batch_size=32):
    model_name = "XTuner/merged01"
    model_path = "/root/InternLM/XTuner/merged01"
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True).half().cuda()

    entity_types = ["方剂", "中药", "疾病", "临床表现", "证候", "治法"]

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    results = []

    for i in tqdm(range(0, len(rows), batch_size), desc="Processing batches"):
        batch = rows[i:i+batch_size]
        batch_texts = [row['text'] for row in batch]
        batch_entities = [perform_ner_with_model(text, model, tokenizer) for text in batch_texts]

        for row, entities in zip(batch, batch_entities):
            for entity, entity_type in entities:
                if entity_type in entity_types:
                    results.append({
                        'id': row['id'],
                        'text': row['text'],
                        '实体': entity,
                        '类型': entity_type
                    })

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'text', '实体', '类型'])
        writer.writeheader()
        writer.writerows(results)

    print(f"NER results have been saved to {output_file}")

# 4. 主函数：添加if __name__ == "__main__"块
if __name__ == "__main__":
    input_file = '/root/IE_刘子辰_辽宁中医药大学.csv'
    output_file = 'NER_results01.csv'
    perform_ner(input_file, output_file)



