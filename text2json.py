import json
import re
from openai import OpenAI
def markdown_to_json(markdown_text):
        # 正则表达式匹配markdown格式的文本
        # 使用正则表达式匹配markdown格式的文本
        for char in markdown_text:
            if char == '\n':
                markdown_text = markdown_text.replace(char,'')
        pattern = r'\d.+'
        matches = re.finditer(pattern, markdown_text)
        # 将匹配结果转换为json格式
        json_data = []
        for match in matches:
            dicts = {}
            #print(type(match))
            try:
                entity = str(match).split('>')[0].split('-')[0].split('**')[1]
                category = str(match).split('>')[0].split('-')[1].split('：')[1][:-1]
                 
            except:
                try:
                    entity = str(match).split('-')[1].strip()
                    category = str(match).split('-',2)[2]
                except:
                    pass
                else:
                    dicts['实体'] = entity
                    dicts['实体类别'] = category
                    json_data.append(dicts)
            
            else:
                dicts['实体'] = entity
                dicts['实体类别'] = category
                json_data.append(dicts)
        return json_data

def text2json(query):
    guide = {
        'type': 'object',
        'properties': {
			'name': {
				'type': 'string'
			},
			'skills': {
				'type': 'array',
				'items': {
					'type': 'string',
					'maxLength': 10
				},
				'minItems': 3
			},
			'work history': {
				'type': 'array',
				'items': {
					'type': 'object',
					'properties': {
						'company': {
							'type': 'string'
						},
						'duration': {
							'type': 'string'
						}
					},
					'required': ['company']
				}
			}
		},
		'required': ['name', 'skills', 'work history']
	}
    response_format=dict(type='json_schema',  json_schema=dict(name='test',schema=guide))
    messages = [{"role": "system", "content": "请你扮演一个角色，名叫Tom，是一位优秀的自然语言理解工程师，精通命名实体识别和关系抽取。同时你也对中医药学有深入研究，尤其是皮肤病相关疾病的诊断与治疗方面，不弱于世界上任何一位医药学家"},
    ]
    messages.append({'role': 'user', 'content': '请找到下面这句话中的实体，实体类别。这句话是:'+query})
    client = OpenAI(api_key='internlm', base_url='http://127.0.0.1:23333/v1')
    model_name = client.models.list().data[0].id
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.1,
        response_format=response_format,
        top_p=0.8)
    res = response.json()
    print(type(res))
    resdict = json.loads(res)
    result = resdict['choices'][0]['message']['content']#{"id":"5","choices":[{"finish_reason":"stop","index":0,"logprobs":null,"message":{"content":
    #result_json = markdown_to_json(result)
    #print(result)
    return result


def text2json_pkl():    
    import pandas as pd

    df = pd.read_csv('./第三批数据/测评数据集/IE/IE_data.csv')
    textlist = df['text'].tolist()
    idlist = df['id'].tolist()
    result_data = []
    i = 0
    for text in textlist:
        
        if text[0] != '\"':
            text = '\"'+text+'\"'
            textjson =  text2json(text)
            result_data.append(textjson)
            '''
            if len(textjson) > 0:
                textjson.append({'id':idlist[i]})
                i += 1
                textjson.append({'text':text})
                result_data.append(textjson)
            else:
                i += 1
            '''  
    print(result_data,len(result_data))
    import pickle

    with open('result_data.pkl', 'wb') as f:
        pickle.dump(result_data, f)
    #result_data.to_csv('result_data.csv', index=False)
    #text2json(df)
    
    #print(text2json('患者李*男52岁,因双足起疹伴流水、痒十余天,用药后面部、躯干、上肢泛发皮疹4天入院。患者足癣病史10余年,曾在10年前因“足癣继发感染”于我科住院治疗。半月前无明显诱因病情复发,双足新生丘疹、红斑,伴瘤痒,流水。自行使用“高锰酸钾”及过期中药泡洗,病情稍有控制,一周后病情再次加重,伴流水,并于入院前4天在外院就诊,诊断为“足癣”,给予口服“米诺环素、甲硝哇”,静脉注射“克林霉素”治疗,外用药不详,用药治疗后病情变化,双足皮损未见明显缓解,且皮损自头面部泛发全身,出现面部肿,双耳流水,双臂起红斑,痉痒明显,遂于我院门诊就诊,诊断为“1.足癣继发感染,2,药疹”,为求进一步系统诊治收入院。入院时症见:头面部肿胀,双耳流水、双臂红斑,双手足及指趾间糜烂、渗出、结痴,饮食可、二便调。患者既往有血压升高史及胆囊切除史。入院查体:系统检查无异常,舌苔黄腻,脉弦滑。皮科情况:双手足大片肿胀红斑,双手指间及指侧多数水疤,疤壁厚,疤液略浑浊;双足趾间浸渍、糜烂、渗出,上覆大片污秽痴皮。头面、躯干、双上肢大片潮红斑片,少许脱屑;面部红肿、干燥斑片;双耳廓渗出、结痴;双上肢少许抓痕。入院实验室检查:血尿常规及生化检查均示正常。入院中医诊断:臭田螺,湿热感毒症;西医诊断:1.足癣继发感染2.药疹。1.2.治疗方法根据患者证候舌脉综合分析,此例足廖感染,中医可辨为湿热感毒,而药疹所见皮损亦属于察赋不耐,受禁忌之毒邪所致。故中医治疗立法为清热利湿,解毒止痒,方用赵炳南传统中药方剂清热除湿汤加减(龙胆草10、黄芩10、板蓝根15、白茅根15、生地黄30、泽泻10、猪苓10、马齿苋15g、大腹皮10、六一散30、黄连10、白鲜皮15g、苦参10、蒲公英15g),每日一剂水煎服。手足部皮损予以“清热消肿洗剂”(北京中医医院院内制剂,成分:马齿苋、黄柏)稀释后湿敷,以“甘草油”(北京中医医院院内制剂,成分:甘草,香油)清洁痴皮,配合半导体激光照射治疗,促进皮损干燥。连续治疗5天后,患者双足肿胀减轻,浸渍干燥,红斑退,脱屑较多;头面肿胀基本消退;双耳廓渗出减少,可见干燥脱屑及痴皮。躯干,双上肢仍可见大片潮红斑片及抓痕(药疹表现)。双手新生疤融合成大疙,舌质红苔薄黄,脉滑数。停用中药化腐清疮治疗,中药立法仍以清热利湿解毒为法,佐以利水消肿之品。前方去六一散、苦参,加桑枝l0,生薏米15,冬瓜皮15七剂煎服。入院后第10天,患者双足肿基本消退,躯干,双上肢潮红斑消失,有少量皮屑。双手无新生水疤,原有水疤已干燥结痴,舌质淡红苔薄黄,脉滑。停用半导体激光照射及清热消肿洗剂外敷,前方中药继服,皮屑痴皮处,外用甘草油、硅霜(北京中医医院院内制剂)安抚涂搽。治疗18天后,患者痊愈出院'))

if __name__=='__main__':
    def write_rowresult():
        import pickle

        with open('result_data.pkl', 'rb') as f:
            result_data = pickle.load(f)
            rown = 0
            rowresult = []
            for row in result_data:
                #print(row)
                rown += 1
                rowresult.append(rown)
                rowresult.append(row.split('\n')[2:-2])
                #if rown == 10:
                    #break
            print(rowresult)
            with open('rowresult.pkl', 'wb') as f:
                pickle.dump(rowresult, f)
    def getIdandTextFromcsv(filepath,id):
        import csv
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            #print(type(reader))
            data_list = []
            for row in reader:
                data_list.append(row)
            return data_list[id]
    def splitrowlist():
        import pickle

        with open('rowresult.pkl', 'rb') as f:
            rowresult = pickle.load(f)
        #print(rowresult)
        
        rowresult_split_header = ['id','text','实体','实体类别']
        rowresult_split_data = []
        rown = 0
        rowlist = []
        for row in rowresult:
            if rown % 2 == 0:
                #print(row)
                pass
            else:
                rowlist.append(row)      
            rown += 1
        rownn = 0
        rownnlist = []
        restrowlist = []      
        for row in rowlist:#72行列表数据
            for rowdata in row:
                idAndTest  = getIdandTextFromcsv('./第三批数据/测评数据集/IE/IE_data.csv',rownn+1)
                try:
                    entity = rowdata.split('-')[0].strip().split('**')[1]
                    #print('entity:',entity)
                    category = rowdata.split('-')[1].strip().split('：')[1]
                    #print('category:',category)
                    idAndTest.append(entity)
                    idAndTest.append(category)
                    rowresult_split_data.append(idAndTest)
                    rownnlist.append(rownn)
                except:
                        pass
                #print(rowdata)           
            rownn += 1
            #if rownn == 10:
            #    break
        
        
        
        #print(rowlist,len(rowlist))
        #print(rownnlist,len(rownnlist))
        aldict = {}
        for rownnkey in rownnlist:
            aldict[rownnkey] = rownnlist.count(rownnkey)
        #print(aldict.keys())
        rownnn = 0
        for row in rowlist:
            try:
                if aldict[rownnn] != -1:
                    pass
            except:
                row.append(rownnn)
                restrowlist.append(row)
            rownnn += 1
        #print(restrowlist,len(restrowlist))
        keyrowdict = {}
        rownnnn = 0
        rowresult_restlist_data = []
        for i in range(len(restrowlist)):
            if i + 1 < len(restrowlist):
                row = restrowlist[i+1]
                yuanNumber = row[-1]#拿到剩余数据行在原列表中的序号
                for rowdata in row[:-1]:
                    try:
                        entity = rowdata.split('-')[0].strip().split('**')[1]
                        category = rowdata.split('-')[1].strip()
                        #print(entity,category)
                        rowresult_restlist_data.append([i+1,yuanNumber,entity,category])
                    except:
                        try:
                            entity = rowdata.split('-')[1].strip()
                            category = rowdata.split('-')[2].strip()
                            #print(entity,category)
                            rowresult_restlist_data.append([i+1,yuanNumber,entity,category])
                        except:
                            pass
                        keyrowdict[rownnnn] = row
                        pass
            rownnnn += 1
        print("尚未抽取的记录：",keyrowdict.keys(),len(keyrowdict.keys()))
        restdatalist = []
        
        for p in range(len(rowresult_restlist_data)):
            restrow = getIdandTextFromcsv('./第三批数据/测评数据集/IE/IE_data.csv',rowresult_restlist_data[p][1]+1)
            restrow.append(rowresult_restlist_data[p][2])   
            restrow.append(rowresult_restlist_data[p][3])
            restdatalist.append(restrow)
            #print(rowresult_restlist_data[p])
        
        #print(restdatalist)
        rowresult_split_data.extend(restdatalist)
        #提取尚未抽取的记录
        finalrowlist = []
        finalrowlist.append(restrowlist[0])
        for rownnnnn in range(len(restrowlist)):
            try:
                rownumber = keyrowdict[rownnnnn]              
                finalrowlist.append(restrowlist[rownnnnn])
            except:
                pass
        #print(finalrowlist,len(finalrowlist))
        global finalkeyrowdict
        finalkeyrowdict = {}
        def getrowlistbyfinalrowlist(finalrowlist):
            rowresult_final_data = []
            rownumber1 = 0
            for row in finalrowlist:
                for text in row[:-1]:
                    if len(text.split('-')) == 2:
                        #print("------------:",text,'\n\n')
                        if len(text.split('-')) == 2 and len(text.split('-')[0].strip()) == 0:
                            pass
                            #print("单实体:",text,'\n\n')
                            
                        else:
                            
                            entity = text.split('-')[0].strip().split('**')[1]
                            category = text.split('-')[1].strip()
                            #print("实体:",entity)
                            #print("实体类别:",category)
                            restrow = getIdandTextFromcsv('./第三批数据/测评数据集/IE/IE_data.csv',row[-1]+1)
                            restrow.append(entity)
                            restrow.append(category)
                            rowresult_final_data.append(restrow)    
                            finalkeyrowdict[rownumber1] = row[-1]+1
                    if len(text.split(':')) == 2 and len(text.split('-')) != 2:
                        pass
                        #print("::::::::::::::::::",text,'\n\n')
                    if len(text.split(':')) != 2 and len(text.split('-')) != 2:
                        pass
                        #print("--非2，：非2:",text,'\n\n')
                rownumber1 += 1
            return rowresult_final_data
        finalrowlist = getrowlistbyfinalrowlist(finalrowlist)
        #print(finalrowlist,len(finalrowlist))
        print("补充抽取的记录",finalkeyrowdict.keys(),len(finalkeyrowdict.keys()),'values:',finalkeyrowdict.values())
        rowresult_split_data.extend(finalrowlist)
        
        import csv
        with open('output.csv', 'w', newline='',encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(rowresult_split_header)
            writer.writerows(rowresult_split_data)
    
    #入口程序，执行数据清洗 
    splitrowlist()
    #print(getIdandTextFromcsv('./第三批数据/测评数据集/IE/IE_data.csv',3))  
    #读取结果文件，按id排序后重写
    def rewritecsvbyid(filepath):
        import csv
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            data_list = []
            header = []
            rownumber = 0
            for row in reader:
                if rownumber == 0:
                    header = row
                else:
                    data_list.append(row)
                rownumber += 1
        data_list.sort(key=lambda x: int(x[0]))
        with open('output_sortByid.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(data_list)
    rewritecsvbyid('output.csv')
    
    