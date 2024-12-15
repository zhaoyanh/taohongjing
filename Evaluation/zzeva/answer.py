import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import csv
import os

def generate_answers_csv():
    input_file = '/root/Question_KG_Competiton3.csv'
    output_file = 'QA_刘子辰_辽宁中医药大学.csv'
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = ['id', 'type', 'question', 'answer']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            question_id = row['id']
            question_type = '选择' if row['type'] == '选择' else '问答'
            question = row['question']
            
            answer = answer_questionnaire(question, 'multiple_choice' if question_type == '选择' else 'open_ended')
            
            writer.writerow({
                'id': question_id,
                'type': question_type,
                'question': question,
                'answer': answer
            })

    print(f"Answers have been generated and saved to {output_file}")

def answer_questionnaire(question, question_type):
    # Load the XTuner/merged01 model and tokenizer
    model_name = "XTuner/merged01"
    model_path = "/root/InternLM/XTuner/merged01"
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True).half().cuda()
   
    # Prepare the prompt based on the question type
    if question_type == "multiple_choice":
        prompt = f"""
要求最后给出的答案：
1、直接输出答案，如：A或B等，不需要给出其他任何解释、不需要选项后面的中文。
2、根据经验进行作答，选择最确定的答案；
3、直接输出选项的字母，不要有任何多余输出。

问题：{question}
"""
    elif question_type == "open_ended":
        prompt = f"""
你是中医赵炳南流派皮肤科的专家，以下是一道中医皮肤科的问答题。请根据题面，给出答案与分析。
要求最后给出的答案：
1、能够逐步推理、必要时可分点论述，以更全面展现中医诊疗知识的推理过程；
2、结合中医专业知识，根据经验进行作答；
3、直接输出答案，不要输出任何prompt(提示词)，如：“你是中医赵炳南流派皮肤科的专家，以下是一道中医皮肤科的问答题。请根据题面，给出答案与分析”等prompt(提示词)。
4、倘若答案中包含"你是中医赵炳南流派皮肤科的专家，以下是一道中医皮肤科的问答题。请根据题面，给出答案与分析。.....问题："请去除，只输出答案部分。

问题：{question}
"""
    else:
        raise ValueError("Invalid question type. Must be 'multiple_choice' or 'open_ended'.")

    # Generate the answer
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=2048)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # For multiple-choice questions, extract only the letter answer
    if question_type == "multiple_choice":
        answer = answer.strip()[-1]  # Assuming the last character is the answer

    return answer

# Example usage
# multiple_choice_question = "赵炳南名医擅长的方剂是哪种？A清营汤；B增液汤合益胃汤；C皮炎汤；D以上均不是"
# open_ended_question = "赵炳南针对皮肤淀粉样变提出的综合治法及其理论基础是什么？"
# 
# print(answer_questionnaire(multiple_choice_question, "multiple_choice"))
# print(answer_questionnaire(open_ended_question, "open_ended"))

generate_answers_csv()
