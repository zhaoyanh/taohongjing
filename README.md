# 陶弘景中医药大模型
陶弘景中医药大模型，包括命名实体识别，关系抽取，知识图谱构建，大模型增量微调，RAG


👋 联系我们: 644735344@qq.com

🎉 项目进展

🔥更好的模型永远在路上!🔥

    Oct. 16,2024： 上传Taohongjing-7B至github,以供下载

🌈 模型介绍

陶弘景（456年—536年），字通明，自号华阳隐居，谥贞白先生，丹阳秣陵（今江苏省南京市）人。南朝齐、梁时道教学者、炼丹家、医药学家。著有《神农本草经集注》。

陶弘景中医药大模型(简称: Taohongjing)希望能够遵循陶弘景的生平轨迹, 重视民间医疗经验, 完善中药基源、分类、应用知识体系。不断累积中文医疗数据, 并将数据附加给模型, 致力于提供安全、可靠、普惠的中文医药大模型.

🚩 Taohongjing-7B模型由Internlm2_5-chat-7B模型与高质量医药数据增量微调而得，在CMB-Exam中达到30B量级模型SOTA！ 同时在中国国家执业医师、药师、护士资格考试中均取得优异成绩。

📅 模型列表
模型名称 	lora权重 	合并后的权重

🆕Taohongjing-7B 	🤖modelscope / 🤗huggingface 	🤖modelscope /✡️WiseModel/ 🤗huggingface
Taohongjing-1.8B 	🤖modelscope / 🤗huggingface 	🤖modelscope / 🤗huggingface
Taohongjing-20B-Chat 	🤖modelscope / 🤗huggingface 	🤖modelscope / 🤗huggingface

📚 数据详情

Taohongjing的各个版本训练数据均取自我们精心构建的文摘数据池，该数据池融合各类医药卫生文献及教材、多科室诊断数据、海量医疗问诊对话、医学知识问答、病历分析等，基于开源数据和GPT4自动构建，经人工清洗标注、自动化数据分析处理所得。

该数据池仍在持续更新中！ 部分数据样例参考：data/example_single.json data/example_multi.json
🎓 模型评估（暂未进行）
CMB-Exam

Taohongjing-7B在CMB-Exam中具体表现如下：

注：图中模型分数均取自CMB榜单数据，具体分数统计于data/cmb_compare.xlsx，详见：CMB-Leaderboard
考试表现
模型名称 	考试名称 	题目数量 	准确率
Sunsimiao-7B 	中国国家执业医师资格考试 	3000 	79.23%
Sunsimiao-7B 	中国国家执业药师资格考试 	2400 	71.33%
Sunsimiao-7B 	中国国家执业护士资格考试 	1200 	83.83%


🔓 使用方法

from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

pipe = pipeline(task=Tasks.text_generation, model='AI-ModelScope/Taohongjing', model_revision='v1.0.0')

query = '小孩发烧了怎么办？'

prompt="Below is an instruction that describes a task. Write a response that appropriately completes the request."
prompt+="### Instruction:\n{}\n\n### Response:\n".format(query)

result = pipe(prompt)
print(result)

{'text': 'Below is an instruction that describes a task. Write a response that appropriately completes the request.### Instruction:\n小孩发烧了怎么办？\n\n### Response:\n\n如果您的孩子发烧了，您可以参考以下建议：\n\n1. 帮助孩子退热：\n\n将冷水倒入一个杯子，放在孩子的腋下(或额头)，每5分钟转一次。\n\n将冰毛巾擦在孩子的胸部、颈部和后背。\n\n将退烧药放在孩子额头或颈部。\n\n2. 检查孩子的症状：\n\n是否咳嗽、鼻塞或流鼻涕？\n\n3. 根据症状：\n\n如果孩子咳嗽，可以给孩子喝些水或温水，并给孩子喝一些蜂蜜;\n\n如果孩子鼻塞，可以给孩子吸入一些蒸汽;\n\n如果孩子发烧，可以给孩子喂些温水，并让孩子休息;\n\n如果孩子呼吸急促或呼吸困难，应立即就医。\n\n4. 如果孩子有其他不适：\n\n如果孩子没有食欲或呕吐，可以给孩子吃些软餐;\n\n如果孩子感到疲倦，可以让孩子休息;\n\n如果孩子的眼睛出现红色或分泌物，应立即就医。\n\n5. 注意孩子的个人卫生：\n\n让孩子勤喝水，勤洗手，保持室内通风;\n\n避免孩子与别的孩子进行密切接触，以免传染。\n\n祝您的孩子早日康复！'}

更多使用方法见scripts
致谢

本项目由辽宁中医药大学副馆长赵彦辉发起,药学院22级栽培与鉴定专业刘子辰具体实施 并受到以下项目及平台的大力支持, 在此表示感谢!

    LLaMA-Efficient-Tuning: 提供微调代码
    OpenAI启智社区: 提供模型训练算力
    魔搭ModelScope、OpenXLab、Huggingface：模型存储和体验空间;
    文心一格: 生成模型logo

特别感谢上海人工智能实验室推出的书生·浦语大模型实战营、InternStudio为我们的项目提供宝贵的技术指导和强大的算力支持!

@Misc{llama-efficient-tuning, 
  title = {LLaMA Efficient Tuning}, 
  author = {hiyouga}, 
  howpublished = {\url{https://github.com/hiyouga/LLaMA-Efficient-Tuning}}, 
  year = {2023}
}

@article{qwen,
  title={Qwen Technical Report},
  author={Jinze Bai and Shuai Bai and Yunfei Chu and Zeyu Cui and Kai Dang and Xiaodong Deng and Yang Fan and Wenbin Ge and Yu Han and Fei Huang and Binyuan Hui and Luo Ji and Mei Li and Junyang Lin and Runji Lin and Dayiheng Liu and Gao Liu and Chengqiang Lu and Keming Lu and Jianxin Ma and Rui Men and Xingzhang Ren and Xuancheng Ren and Chuanqi Tan and Sinan Tan and Jianhong Tu and Peng Wang and Shijie Wang and Wei Wang and Shengguang Wu and Benfeng Xu and Jin Xu and An Yang and Hao Yang and Jian Yang and Shusheng Yang and Yang Yao and Bowen Yu and Hongyi Yuan and Zheng Yuan and Jianwei Zhang and Xingxuan Zhang and Yichang Zhang and Zhenru Zhang and Chang Zhou and Jingren Zhou and Xiaohuan Zhou and Tianhang Zhu},
  journal={arXiv preprint arXiv:2309.16609},
  year={2023}
}

@misc{2023internlm,
    title={InternLM: A Multilingual Language Model with Progressively Enhanced Capabilities},
    author={InternLM Team},
    howpublished = {\url{https://github.com/InternLM/InternLM-techreport}},
    year={2023}
}

