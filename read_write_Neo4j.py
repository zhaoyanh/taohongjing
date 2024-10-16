from neo4j import GraphDatabase
import networkx as nx
import pickle
import os
def read_neo4j_to_networkx():
    # Neo4j数据库连接信息
    uri = "neo4j://10.100.4.14:7687"
    user = "neo4j"
    password = "Liuzichen"

    # 创建NetworkX图
    G = nx.Graph()

    # 连接Neo4j数据库
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        with driver.session() as session:
            # 读取所有节点
            # 读取所有节点
            result = session.run("MATCH (n) RETURN n limit 25")
            for record in result:
                if record != None and record['n'] != None:
                    #print(record)
                    node = record['n']
                    #print("node:",node)
                    node_properties = dict(node)
                    # 检查并过滤掉超过200字节的属性
                    #filtered_properties = {k: v for k, v in node_properties.items() if len(str(v).encode('utf-8')) <= 200}
                    filtered_properties = {k: v for k, v in node_properties.items()}
                    #print("filtered_properties:",filtered_properties,type(filtered_properties),filtered_properties.keys(),filtered_properties.get('name'))
                    nodename = filtered_properties.get('name') if 'name' in filtered_properties else None
                    if nodename != None:
                        G.add_node(nodename, **filtered_properties)

            # 读取所有边
            result = session.run("MATCH (a)-[r]->(b) RETURN a,b,r,type(r),properties(r) limit 25")# a.id, b.id, type(r), properties(r)")
            for record in result:
                if record != None:
                    #print('边：',record)
                    source = record['a']
                    source_properties = dict(source)
                    target = record['b']
                    target_properties = dict(target)
                    source_name = source_properties.get('name')
                    target_name = target_properties.get('name')
                    
                    rel_type = record['type(r)']
                    rel_props = record['properties(r)']
                    #print("a-b:",source_name,target_name,rel_type,rel_props)  
                    # 检查并过滤掉超过200字节的属性
                    #filtered_rel_props = {k: v for k, v in rel_props.items() if len(str(v).encode('utf-8')) <= 200}
                    filtered_rel_props = {k: v for k, v in rel_props.items()}
                    G.add_edge(source_name, target_name , type=rel_type, **filtered_rel_props)
            

    return G


def write_pkl_to_neo4j(filepath):
    # Neo4j数据库连接信息
    uri = "neo4j://10.100.4.14:7687"
    user = "neo4j"
    password = "Liuzichen"

    # 连接Neo4j数据库
    driver = GraphDatabase.driver(uri, auth=(user, password))

    def create_node_and_relationships(tx, data):
        ppp = 0
        for item in data:
            ppp+= 1
            if item['relation'] != None:
                item['relation'] = item['relation'].replace(' ','').replace('%','百分之').replace(',','').replace('.','点').replace('±','加减').replace('(','').replace(')','')
            print(ppp)
            # 为每个字典创建一个唯一标识符
            unique_id = str(hash(frozenset(item.items())))
            if ppp == 1200:
                item['relation'] = '晚期死亡率为百分之3'
            if ppp == 1201:
                item['relation'] = '术后4年生存率为百分之96点9加减百分之3点1'
            if item['docs'].find('观察紫杉醇联合顺铂对晚期食管癌患者肿瘤标记物及MMP') != -1:
                item['docs'] = '\"'+item['docs']+'\"'
                #print(item['docs'])
            if item['docs'][0:1] != "\"":               
                item['docs'] = '\"'+item['docs']+'\"'
                #print(item['docs'])
            # 创建带有属性的关系
            tx.run(
                """
                MERGE (h:Entity {name: $head_name, type: $head_type})
                MERGE (t:Entity {name: $tail_name, type: $tail_type})
                MERGE (h)-[r: %s]->(t)
                SET r +=  {journal_id: %s,docs: %s}
                """ % (item['relation'],item['journal_id'],item['docs']) ,
                head_name=item['head'],
                head_type=item['head_type'],
                tail_name=item['tail'],
                tail_type=item['tail_type'],
                relation_type=item['relation'],
                properties={
                    'journal_id': item['journal_id'],
                    'docs': item['docs']
                }
            )
            # 创建一个唯一项节点来连接所有属性
            tx.run(
                "MERGE (u:UniqueItem {id: $id})",
                id=unique_id
            )
        
    
    def 检查并清理数据(data):
        n = 0
        清理后的数据 = []
        for item in data:
            
            for char in item['tail']:
                if char == ',':
                    item['tail'] = item['tail'].replace(char, '')
                if char == '\'' or char == '\"':
                    item['tail'] = item['tail'].replace(char, '')
                if char == '、' or char == ',':
                    item['tail'] = item['tail'].replace(char, '')
            n += 1
            print("item:",n)
            if n >= 1140:
                for char in item['docs']:
                    if char == '\'':
                        item['docs'] = item['docs'].replace(char, '')
            if item['head'] == '凉血五花汤' and item['tail'] == '红斑性皮肤病':
                item['docs'] = '\'凉血五花汤治疗红斑性皮肤病验案3则 凉血五花汤出自(赵炳南临床经验集),是赵炳南老先生的众多经验方中一首比较著名的方剂,在中医皮肤科临床得到较为广泛的应用.凉血五花汤由红花,鸡冠花,凌霄花,玫瑰花及野菊花组成,具有凉血活血,疏风解毒的功效,适用于血热发斑,热毒阻络所致的皮肤病.方中凌霄花凉血活血泻热为主,玫瑰花及红花理气活血化瘀,鸡冠花疏风活血,野菊花清热解毒.因药味取花,花性轻扬,所以本方比较适宜治疗病变在上半身或全身散发的皮肤病.笔者在临床工作中,根据患者的病情,常选用凉血五花汤治疗红斑类皮肤病,获得了较好的疗效,现列举验案3则如下.\''
            if item['head'] == '中医辨证论治' and item['tail'] == '赵炳南的\'首辨阴阳\'':
                item['docs'] = '\'浅谈赵炳南首辨阴阳学术思想对皮肤病湿证治疗的指导作用 赵炳南先生治疗皮肤病以首辨阴阳为原则,尤其是对于与湿相关的皮肤病,重点是辨别疾病属于湿热性亦或是湿气性;是热重于湿抑或是湿重于热   这点尤其体现在对湿疹和带状疱疹的辨证治疗上   学习和继承赵炳南学术思想,就应该坚持首辨阴阳的原则\''
                item['tail'] = '赵炳南的首辨阴阳'                
                #print(item)
            if item['relation'].find('黑色拔膏棍的理论内涵及临床应用 膏药是我国传统中药剂型') != -1:
                item['docs'] = item['relation']
                item['relation'] = '具有'
                item['tail'] = item['head']
                item['journal_id'] = item['tail_type']
                item['tail_type'] = '治疗效果'
                item['head_type'] = '膏药'
                item['head'] = '黑色拔膏棍'
                #print(item)
            if item['head'] == '药物性皮肤炎' and item['tail'] == '湿毒肿疮':
                value = item['relation']
                item['relation'] = '由_导致'
            if item['head'] == '龙胆泻肝汤' and item['tail'] == '五味子':
                value = item['relation']
                item['relation'] = '由_组成'
                #print(item)
            if item['head'] == '治风三方' and item['tail'] == '全虫':
                value = item['relation']
                item['relation'] = '由_组成'
                #print(item)
            if item['head'] == '治风三方' and item['tail'] == '全虫方':
                value = item['relation']
                item['relation'] = '由_组成'
                #print(item)
            if item['head'] == '治风三方' and item['tail'] == '麻黄':
                value = item['relation']
                item['relation'] = '由_组成'
                #print(item)
            if item['head'] == '皮肤瘙痒症' and item['tail'].find('搔后皮肤发红') != -1:
                item['tail'] = '搔后皮肤发红不起风团'
            if item['head'] == '治学思想' and item['tail'].find('学习贵在专') != -1:
                item['tail'] = '学习贵在专师古更创新宁可会不用不可用不会'
            if item['head'] == '治学思想' and item['tail'].find('态度与方向') != -1:
                item['tail'] = '态度与方向继承与发展博学与精专'  
            if item['head'] == '过敏性紫斑' and item['tail'].find('血热壅盛') != -1:
                item['tail'] = '血热壅盛迫血妄行血不循经溢于脉络凝滞成斑复感风邪'
            if item['head'] == '湿疹' and item['tail'].find('本在湿') != -1:
                item['tail'] = '本在湿标在热'
            if item['head'] == '治风三方' and item['tail'] == '麻黄方':
                value = item['relation']
                item['relation'] = '由_组成'
                #print(item)
            if item['head'] == '治风三方' and item['tail'] == '荆防':
                value = item['relation']
                item['relation'] = '由_组成'
                #print(item)
            if item['head'] == '治风三方' and item['tail'] == '荆防方':
                value = item['relation']
                item['relation'] = '由_组成'
                #print(item)
            if item['head'] == '风湿疡' and item['tail'] == '六淫':
                value = item['relation']
                item['relation'] = '与_有关'
                #print(item)
            if item['head'] == '淘砌疗法' and item['tail'] == '赵炳南教授':
                value = item['relation']
                item['relation'] = '由_提出'
                #print(item)
            if item['head'] == '湿邪' and item['tail'] == '茵陈':
                value = item['relation']
                item['relation'] = '由_治疗'
                #print(item)
            if item['head'] == '湿象' and item['tail'].find('白鲜皮') != -1:
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '三七粉' and item['tail'].find('泻肺清热') != -1:
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '泛发性脓疱型银屑病' and item['tail'].find('当归') != -1:
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '泛发性脓疱型银屑病' and item['tail'].find('加虫类药物') != -1:
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '泛发性脓疱型银屑病' and item['tail'].find('白鲜皮') != -1:
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '湿热毒' and item['tail'] == '槐花':
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '泛发性脓疱型银屑病' and item['tail'].find('槐花') != -1:
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '泛发性脓疱型银屑病' and item['tail'].find('湿') != -1:
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '阴血亏耗' and item['tail'].find('当归') != -1:
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '湿象' and item['tail'] == '虫类药物':
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '秦艽丸' and item['tail'] == '凉血活血除湿解毒养血益气':
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '秦艽丸' and item['tail'] == '养血益气':
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '赵炳南' and item['tail'] == '秦艽丸':
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '秦艽丸' and item['tail'] == '除湿解毒':
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '秦艽丸' and item['tail'] == '凉血活血':
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '泛发性脓疱型银屑病' and item['tail'] == '糜烂黏腻':
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '秦艽丸' and item['tail'] == '泛发性脓疱型银屑病':
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '湿热毒' and item['tail'] == '泛发性脓疱型银屑病':
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '多皮饮' and item['tail'] == '慢性荨麻疹':
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '多皮饮' and item['tail'].find('泻肺清热') != -1:
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '慢性荨麻疹' and item['tail'].find('肺热郁闭') != -1:
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '慢性荨麻疹' and item['tail'] == '多皮饮':
                value = item['docs'].replace('。',' ')
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '自汗病' and item['tail'] == '脾气虚弱':
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '自汗病' and item['tail'] == '肺气不足':
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '自汗病' and item['tail'] == '气虚':
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
                #break
            if item['head'] == '自汗病' and item['tail'] == '甘温之品':
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['head'] == '心律失常' and item['tail'] == '三七粉':
                value = item['docs']
                item['docs'] = '\"'+value+'\"'
                #print(item)
            if item['docs']  == None:
                #print(item)
                item['docs'] = '\"\"'
            if item['docs'] != None and item['docs'].find('秦艽丸治疗泛发性脓疱型银屑病临证阐析') != -1:
                    item['docs'] = '\"'+'秦艽丸治疗泛发性脓疱型银屑病临证阐析 泛发性脓疱型银屑病是皮肤科的疑难重症,严重时可能危及患者生命   中医皮外科创始人及奠基者赵炳南教授认为本病是由湿,热,毒互结郁于血分,发于肌肤所致,疾病后期易化瘀,并导致气血失和   秦艽丸有凉血活血,除湿解毒,养血益气之效   赵炳南教授运用秦艽丸临证加减治疗泛发性脓疱型银屑病,热象重者加用槐花,丹参,湿象重者加白鲜皮,地肤子,苦参,土茯苓,苍术,白术,顽湿不退者加虫类药物,阴血亏耗者加当归,生地黄   秦艽丸能够缓解皮损糜烂黏腻,脓疱,红肿疼痛之象,促进皮损消退'+'\"'
                    #print(item)
            if item['docs'] != None and item['docs'].find('孙丽蕴教授基于燕京赵氏皮科阴阳辨证论治过敏性紫癜经验') != -1:
                    item['docs'] = '\"'+'孙丽蕴教授基于燕京赵氏皮科阴阳辨证论治过敏性紫癜经验 过敏性紫癜属中医葡萄疫范畴,是临床常见的难治性疾病   孙丽蕴教授在传承燕京赵氏皮科首辨阴阳思想基础上,进一步将本病划分为病起之阳斑,病进之阳斑及阴斑,补充本病阴阳辨证论治体系   阳斑治用凉血五根汤化裁,病起之阳斑重清热凉血祛风,病进之阳斑重活血养阴;阴斑治用养血健脾经验方化裁,健脾益气,养血消斑,止血   孙教授辨伴发肢体水肿之阴阳,阳证用白茅根,丝瓜络祛风清热行水,阴证加赤茯苓皮,川牛膝健脾化瘀利水;内外同理,外治上对三阶段分别予以芙蓉膏清热凉血,紫色消肿膏化瘀,紫草茸油健脾活血   本文特举典型病案予以总结'+'\"'
                    #print(item)
            if item['docs'] != None and item['docs'].find('王莒生用多皮饮治疗荨麻疹经验') != -1:
                    item['docs'] = '\"'+'王莒生用多皮饮治疗荨麻疹经验 多皮饮源自三因方中五皮饮,是名老中医赵炳南教授的经验方,王莒生教授作为赵氏皮科流派的主要传承人之一,对于多皮饮的应用有自己独到的心得,在充分分析多皮饮功能主治的基础上,提出多皮饮具有健脾清热除湿作用,所治主症热多寒少,临床上用于治疗慢性荨麻疹可虚可实,可寒可热'+'\"'
                    #print(item)
            if item['docs'] != None and item['docs'].find('燕京学术流派赵炳南治疗药物性皮炎经验') != -1:
                    item['docs'] = '\"'+'燕京学术流派赵炳南治疗药物性皮炎经验 总结赵炳南治疗药物性皮炎的经验   赵炳南认为药物性皮炎属湿毒疡范畴,主因内蕴湿邪,外受毒侵,湿毒合邪郁而化热所致   其认为皮炎病性属实,以脾湿不运为本,毒热壅盛为标   主张从湿,毒,热论治,利湿为基本治则,清热,解毒为重要治法,同时配合凉血养阴,健脾益气,并根据临床辨证分型加减化裁,疗效显著'+'\"'
            if item['docs'] != None and item['docs'].find('燕京赵氏学派从阴阳调和论治狼疮性脂膜炎经验') != -1:
                    item['docs'] = '\"'+'燕京赵氏学派从阴阳调和论治狼疮性脂膜炎经验 狼疮性脂膜炎,中医称之为红蝴蝶疮,阴阳毒,其发病与阴阳失调关系密切,主要证型包括毒热炽盛证,阴血虚亏证,毒邪攻心证,肾阴亏损证,邪热伤肝证   燕京赵氏学派创始人赵炳南教授以着调和阴阳为原则,通过自身临床经验将秦艽丸化裁为秦艽五味方,有调和阴阳,攻补兼施之效,根据相应证型进行加减配伍,在临床上获得较好的疗效   总结燕京赵氏皮科学派从阴阳调和论治狼疮性脂膜炎的经验'+'\"'
            if item['docs'] != None and item['docs'].find('应用赵炳南教授') != -1:
                    item['docs'] = '\"'+'应用赵炳南教授多皮饮治疗慢性荨麻疹临床验证 多皮饮系赵炳南教授在五皮散的基础上化裁而出,治疗多种皮肤疾病的有效方剂 五皮散出自华氏中藏经,主要方药为生姜皮,桑白皮,陈皮,大腹皮,茯苓皮;具有清脾利水消肿,理气健脾的功能;适应于脾虚湿盛,气滞水泛之皮水证 赵炳南教授取其以皮达皮之意,在此基础上创立了多皮饮 处方组成为地骨皮,五加皮,桑白皮,干姜皮,大腹皮,白鲜皮,牡丹皮,茯苓皮,冬瓜皮,扁豆皮,川槿皮 方以健脾除湿,疏风和血 适用于湿疹,荨麻疹,银屑病等湿邪在皮,以祛肌肤之水;较之五皮饮更有凉血疏风止痒之功'+'\"'
            if item['docs'] != None and item['docs'].find('硬皮病辨治经验概述') != -1:
                    item['docs'] = '\"'+'硬皮病辨治经验概述  硬皮病属风湿免疫性疾病范畴,习惯沿用结缔组织疾病,临床分为系统性硬化病和限局性硬皮病两类   该病的属性确定了该病的治疗难度与预后   中医学认为硬皮病属皮痹，皮痹疽范畴,病因总为'+'\"'
            if item['docs'] != None and item['docs'].find('再谈燕京赵氏皮科流派赵炳南教授') != -1:
                    item['docs'] = '\"'+'再谈燕京赵氏皮科流派赵炳南教授从血论治红皮病型银屑病 红皮病型银屑病为皮肤科疑难重症,皮损泛发全身,累及表皮较大面积,燕京赵氏皮科流派创始人赵炳南教授认为本病病位在血,血分热邪,血分毒邪,血分阴虚为3大关键因素   本病主因血分蕴热化火,进而内生或外受毒邪引动血分火邪,火毒炽盛,郁于营血,外发肌肤而来,后期迁延则以血分阴伤为主,正虚邪恋;治疗上赵炳南教授从血分出发,总以清热,解毒,养阴为纲,随病情发展,分期治以清热凉血,泻火解毒,清营护心,养阴益气,清解余邪'+'\"'
            if item['docs'] != None and item['docs'].find('赵炳南白疕1号治疗寻常型银屑病血热型临床观察') != -1:
                    item['docs'] = '\"'+'赵炳南白疕1号治疗寻常型银屑病血热型临床观察 目的 观察赵炳南白疕1号治疗寻常型银屑病血热型的临床疗效   方法 52例用随机数字表法分为治疗组和对照组各26例,治疗组予赵炳南白疕1号口服,对照组口服雷公藤多苷片   结果 治疗组总有效率高于对照组(P<0.05)   治疗后两组红斑,浸润,鳞屑及皮损面积等PASI积分均改善,且治疗组改善优于对照组(P<0.05)   结论 赵炳南白疕1号治疗寻常型银屑病血热型疗效较好'+'\"'
            if item['docs'] != None and item['docs'].find('赵炳南荆防方治疗风热血热型瘙痒性皮肤病探析') != -1:
                    item['docs'] = '\"'+'赵炳南荆防方治疗风热血热型瘙痒性皮肤病探析 荆防方是由赵炳南先生所创,常用于治疗风热型荨麻疹   瘙痒性皮肤病的病因主要有风,湿,热,虫,瘀等,风盛则痒,血热化燥,燥则生风,形成风热血热交互的证候,引起皮肤瘙痒   多种瘙痒性皮肤病存在风热血热的共同病机,荆防方具有祛风清热,凉血止痒之功,加减荆防方也可用于治疗其他风热血热型瘙痒性皮肤病'+'\"'
            if item['docs'] != None and item['docs'].find('赵炳南外治湿疹常用水剂之探源求实及发挥') != -1:
                    item['docs'] = '\"'+'赵炳南外治湿疹常用水剂之探源求实及发挥 名老中医赵炳南为中医皮外科先驱,建立了以气血津液辨证为基础的皮损辨证体系,重视外治法,形成了众多药物外治经验方   赵炳南认为湿疹的病机为本在湿,标在热,湿为发病核心,运用药物外治法时以清热燥湿为基本原则,其中外用水剂为一特色治法   赵炳南外治湿疹常用的水剂包括苍肤水剂,马齿苋水剂,龙胆草水剂,用法包括湿敷,浸泡等,具有使用简便,疗效显著等优点,为其特色外治法的代表'+'\"'
            
            if item['docs'] != None and item['docs'].find('赵炳南益气养阴法治疗败血症探究') != -1:
                        item['docs'] = '\"'+'赵炳南益气养阴法治疗败血症探究 赵炳南益气养阴法治疗败血症探究郎继孝李松林指导唐由君山东中医药大学(济南250014)已故外科名中医赵炳南在败血症的中药治疗上有独到见解,他提出的益气养阴法至今对我们治疗该病仍有指导意义,今阐其要义如下  气阴双亏为本毒气流窜为标乃古今共识败血'+'\"'
            if item['docs'] != None and item['docs'].find('赵炳南引血疗法治疗阴证疮疡思路探讨') != -1:
                        item['docs'] = '\"'+'赵炳南引血疗法治疗阴证疮疡思路探讨 引血疗法是赵炳南先生独树一帜的外治疗法,赵老将引血疗法引入外科阴证性疾患的治疗,开创该类疾病引血治疗之先河   阴证疮疡的病机在于虚,瘀并存,由瘀致虚,或由虚致瘀,虚瘀致寒,寒重瘀重虚重   赵老早年将引血疗法用于外科时毒壅盛的实证,但后期独辟蹊径,大胆使用引血疗法治疗阴证疮疡,充分体现其呼脓去腐煨脓长肉回阳化腐生肌祛瘀生新学术思想,后世在引血治疗阴证思想指导下将此疗法用于各类外科疾病的临床实践   引血疗法治疗阴证疮疡的中医机制在于变瘀为通,变静为动,祛瘀通络,温阳生新,从而瘀去新生,阳气得复,达到治愈疾病的目的   而西医机制在于改善微循环及局部缺血缺氧状态,促进组织细胞恢复,增强细胞免疫功能'+'\"'
            
            if item['docs'] != None and item['docs'].find('赵炳南治疗红斑狼疮的用药经验') != -1:
                        item['docs'] = '\"'+'赵炳南治疗红斑狼疮的用药经验 红斑狼疮可分为局限性盘状和系统性两型,前者以皮肤损害为主,通常毁坏面容;后者除皮肤病变外,尚可同时出现肾,心等脏腑损伤,甚则危及生命   赵老从上实下虚,上热下寒,水火不济,阴阳失调的复杂病象中,善于剖析阴阳消长,邪正增减,寒热变迁等种种关系,选用证治准绳之秦艽丸为基本方化裁,治疗红斑狼疮,常获良效,兹简介如下  秦艽丸组成 黄芪30克秦艽15克黄连6克乌梢蛇6克漏芦10克   赵老认为 方中用药虽然只有5种,然其功用'+'\"'
            if item['docs'] != None and item['docs'].find('赵炳南中医皮肤科学术渊源及学术特点研究') != -1:
                        item['docs'] = '\"'+'赵炳南中医皮肤科学术渊源及学术特点研究 名老中医的学术思想与经验是中医学的宝贵财富,继承,挖掘与传播名老中医的学术思想是加快中医事业发展与创新的重要途径   赵炳南教授(1899-1984)是我国著名中医皮外科专家,是现代中医皮肤科的奠基人和开拓者,为发展中医皮肤科事业做出了卓越贡献   但我们对其搏大精深的学术思想体系还缺乏深入系统的研究   这种状况在很大程度上限制了赵炳南皮肤科学术精髓的传承与推广   深入进行赵炳南中医皮肤科学术渊源,学术思想和经验特色的研究,对中医皮肤科的可持续发展具有重要意义   中医皮肤科赵炳南学术流派及其传承研究是2006年度北京市中医药科技发展基金项目51510重大项目   中医皮肤科赵炳南学派学术渊源及学术思想研究是此重大项目中的第一个子课题,由北京中医药大学中医临床基础系温病教研室负责完成   笔者所选课题为此子课题中的一部分,重点是对赵炳南中医皮肤科学术思想之渊源及特点进行深入研究总结   本研究论文旨在探寻赵炳南中医皮肤科学术思想渊源,研究总结赵炳南中医皮肤科学术思想特色   通过总结中医皮外科古籍文献和温病学名家著作的有关论述,明确中医皮肤科学理论发展的脉络及对赵氏思想的影响,明确赵炳南对中医皮肤病学发展和创新的贡献   通过分析研究(赵炳南临床经验集),(简明中医皮肤病学)等著作及有关文献报道资料,深入总结赵老皮肤病辨治的基本理论和方法,并尽可能地条理化,系统化,便于指导临证或实际应用   本论文主要内容分为三大部分   第一部分是对赵炳南中医皮肤科的学术渊源进行研究   明以前是中医皮肤科理论与实践不断积累的时期,明清两代是中医皮外科学发展的鼎盛和争鸣时期,外科三大主要学术流派即产生于明清   明清时期中医皮外科学所取得的成就是赵炳南皮肤科学术思想的最重要的源泉   赵炳南不但继承了历代皮外科治疗上的精华,且有颇多创新,形成了自己皮外科治疗的独特风格   论文中对(赵炳南临床经验集)中所记载的31个主要皮肤病病种进行文献溯源,分析总结赵炳南论治不同皮肤病的特点与历代主要中医皮外科古籍文献和名家的关系,以期更好地明确赵炳南皮肤科学术思想之渊源,明确赵炳南对中医皮肤病学发展和创新的贡献   论文第二部分是对赵炳南中医皮肤科的学术思想进行研究总结,主要从五个方面论述了赵炳南的学术思想特点   一是坚持中医辨证论治特色,对皮肤病证候进行了规范   (赵炳南临床经验集)记载了11类共31种皮肤病的诊治方法,每一病种都有中医辨证   (简明中医皮肤病学)中介绍了中医基础理论及中医对皮肤病的辨证论治,在皮肤病各论中详细记载了对各种皮肤病的中医辨证分型及论治方法   二是始终以中医整体观指导对皮肤病的辨证治疗   赵炳南将中医整体观作为一种指导思想贯穿于皮肤病诊疗的全过程   他认为应从整体观出发研究皮肤病的发病规律,从整体角度分析皮肤科病证及其变化   三是强调阴阳辨证,擅长运用调和阴阳法治疗皮肤病   阴阳是八纲中的总纲,是辨证的基本大法,赵炳南在医学实践中重视运用阴阳辨证治疗临床疑难杂症   赵老指出调和阴阳法在皮肤科疾病中占有重要位置,并喜用鸡血藤,首乌藤,钩藤,天仙藤等藤类药物为调和阴阳基本方药加减运用于皮肤病临床   四是重视运用卫气营血辨证诊治皮肤病   赵炳南对温病学说有颇深研究,率先将温病学的成就用于皮肤科中   他深入研究卫气营血辨证理论,将之与皮肤病临床紧密结合   尤其是善于运用卫气营血辨证治疗丘斑疹类皮肤病及急性感染性皮肤病   他以卫气营血学说为指导,创制出有关皮肤病治疗的一系列经验方,临床应用,疗效显著   五是治疗皮肤病,常以治湿为根本,治热为关键   赵炳南在诸多皮肤病的致病因素中,对湿邪与热邪尤为重视   赵炳南把温病学说关于湿热病的思想灵活用于皮肤病治疗中   在长期反复临证实践的基础上,赵老形成了对于湿热性皮肤病辨证施治的看法   论文第三部分是对赵炳南中医皮肤科治法和方药特点进行研究   主要从以下五个方面进行了论述   一是赵老在中医皮外科临床领域潜心研究,博览群书又学古不泥,在长期和大量的医疗实践中,对中医皮,外科的理论提出了一些创新的见解,在理法方药等各个方面,均颇有创新   二是在长期临床实践中,赵老通过大量病例,总结出了许多疗效显著的经验方,有些已形成系列   其立法周全详察,组方科学严谨,对后学者极具指导意义   三是对赵炳南部分常用效验方之特点进行分析,主要包括全虫方,秦艽丸,多皮饮,五皮五藤饮,祛湿健发汤等   四是对赵老临床药物运用特点进行分析   通过分析其应用清热解毒药,祛风药,对药,组药,引药的特点,以总结其用药经验,为中医皮肤科的临床用药提供资料   五是分析总结赵老治疗皮肤病时运用外治法,外用药的特点   赵老对中医外用药的配制和使用尤有独到之处,他汲取百家之长,不断研究创新,形成了系统的外治法,外用药方案,还逐渐形成了自己的特色外治疗法'+'\"'
            
            if item['docs'] != None and item['docs'].find('凉血五花汤') != -1:
                        item['docs'] = '\"'+'凉血五花汤治疗红斑性皮肤病验案3则 凉血五花汤出自(赵炳南临床经验集),是赵炳南老先生的众多经验方中一首比较著名的方剂,在中医皮肤科临床得到较为广泛的应用.凉血五花汤由红花,鸡冠花,凌霄花,玫瑰花及野菊花组成,具有凉血活血,疏风解毒的功效,适用于血热发斑,热毒阻络所致的皮肤病.方中凌霄花凉血活血泻热为主,玫瑰花及红花理气活血化瘀,鸡冠花疏风活血,野菊花清热解毒.因药味取花,花性轻扬,所以本方比较适宜治疗病变在上半身或全身散发的皮肤病.笔者在临床工作中,根据患者的病情,常选用凉血五花汤治疗红斑类皮肤病,获得了较好的疗效,现列举验案3则如下.'+'\"'
            if item['docs'] != None and item['docs'].find('刺络放血补虚') != -1:
                        item['docs'] = '\"'+'刺络放血补虚渊源及机理考 刺络放血是中医特色治疗技法之一,既往其适应症主要为热证,实证,瘀证等.至金元后,刺络放血用于虚证的报道逐渐增多,但其观点及操作方法又呈现不同的派别.本文考证刺络放血疗法用于治疗虚证在各朝代的主要适应症,并对不同流派之间观点差异进行分析,对其治疗手法的差异及治疗原理的不同进行整理.笔者发现刺络疗法用于虚证,阴证从(内经)已有报道.这其中观点又分两派,一种以李杲为代表的刺络健脾补虚派;第二种是通过祛瘀,使瘀去新生而达到扶正的目的.两类观点在建国后临床应用均疗效确切.其操作手法存在差异,前者更强调穴位的选取,刺中络脉即可,并不强求出血;而后者除选穴外对局部放血的操作更加注重,除了刺络外还强调局部放血的重要性.前者机理在于增强免疫功能扶正补虚,而后者一定程度上改变微循环,局部血流动力学补虚.当代名家在临床和理论上进一步突破,如将刺络疗法用于阴证,虚证疮疡,提出络以通为用,刺络放血可以通为补,更好指导了刺络放血疗法在虚证类疾病的应用.'+'\"'
            if item['docs'] != None and item['docs'].find('花藤子方') != -1:
                        item['docs'] = '\"'+'花藤子方加减治疗皮肤病验案4则 花藤子方最早见于南通医学院附属医院,当时称三花一子藤方,用于治疗寒冷性多形红斑,荨麻疹,1981年我院管汾教授将其编入 (实用中医皮肤病学). 三花一子藤方当时的组成是槐花12g,白菊花9g,款冬花9g,地肤子30g,首乌藤9g,重点用于治疗寒冷性多形红斑湿热蕴结证[1].1983年赵炳南,张志礼将其作为治疗多形红斑的验方收入(简明中医皮肤病学)[2],此后花藤子方在全国各地得到了普遍运用. 北京龙振华教授临床随证加减为三花一子藤饮,药物组成是红花10g,槐花10g,白菊花10g,地肤子15g,首乌藤10g,用于治疗冻疮,寒冷性多形红斑,寒冷性荨麻疹,均取得了很好的疗效[3-4]. 2002年西京医院制成院内制剂花藤子颗粒用于治疗急性荨麻疹风热证[5]. 第四军医大学药学院王四旺教授等将首乌藤作为君药,同时加入金银花,开发了用于治疗荨麻疹等过敏性疾病的中药新药花藤子颗 粒 ,2004 年 4 月 获 得 国 家 新 药 临 床 批 文(CZL00173)[6]. 外邪阻滞气血,经络可导致风热,血热,湿热证,临床表现为皮疹灼热红肿,自觉疼痛,瘙痒,口干,大便干结,小便黄,舌质红,苔黄,脉数等,具体可诊断为寒冷性多形红斑,结节性红斑,荨麻疹,湿疹等多种皮肤病.'+'\"'
                      
            if item['docs'] != None and item['docs'].find('从血论治') != -1:
                        item['docs'] = '\"'+'从血论治话白疕谈赵炳南,朱仁康,金起凤三位医家从血论治寻常型银屑病 赵炳南,朱仁康,金起凤三位老中医均为中医皮外科的泰斗   他们对银屑病的辨证论治疗效卓著,因为他们既继承了前人的经验,又各有创新和发挥   本文对三位医家的寻常性银屑病的论治分型进行了介绍'+'\"'
            if item['docs'] != None and item['docs'].find('法皮科应用诌议') != -1:
                        item['docs'] = '\"'+'以皮治皮法皮科应用诌议 皮类药物用于皮肤疾患,历代多有例证,(神农本草经)列皮类药16种,其中论五加皮主疽疮阴蚀,论肉桂能和颜色,蛇蜕主虫毒,开皮类药物治皮肤疾患之先河   再如陈实功用治顽癣之顽癣必效方,即以川槿皮,海桐皮为主药,王肯堂用治风瘾疹的的桦皮散(取自(太平惠民和剂局方))及地骨皮汤,李时珍用于洁肤悦面的白杨皮散,(太平圣惠方)中除渣美鼻之木兰皮膏,都体现了以皮治皮的思想   又如钱乙用治小儿肺中郁热之泻白散(桑自皮,地骨皮,甘草),后被用于肺热引起的皮肤蒸热,瘙痒,现常用于痤疮 近代皮肤科专家赵炳南在(麻科活人全书)五皮饮的基础上创多皮饮(冬瓜皮,大腹皮,五加皮,桑白皮,地骨皮,茯苓皮,干姜皮,白藓皮,丹皮,川槿皮)用治湿疹,急慢性荨麻疹,更是以皮治皮思想指导下对皮类药物的应用'+'\"'
              
            #凉血五花汤法皮科应用诌议
            
            else:
                
                if item['docs'] != None and item['docs'].find('强化卫生健康事业发展支撑保障') != -1:
                    #print(item)
                    item['docs'] = '\"强化卫生健康事业发展支撑保障 今年的全国卫生健康工作会议提出,强化卫生健康事业发展的支撑保障,在法治建设,投入保障,科技创新,发展壮大医疗卫生队伍,加 强平安医院建设,加强医疗行业综合监督,守牢意识形态阵地等领域圈出重点   这体现出,发展卫生健康事业坚持统筹观念,进一步补短板,强弱项\"'   
                if item['docs'] != None and item['docs'].find('枇杷老叶无毒') != -1:
                    #print(item)
                    item['docs'] = '\"盘点延禧攻略中的中医误区 伴随着清宫剧延禧攻略的热播,剧情细节和演员表演引人入胜,但是剧中一些中医元素的细节,可能又让中医背锅了    疑点一 枇杷新叶有毒? 剧中女主魏璎珞遇到的第一危及性命的闯关游戏就是因帮助愉贵人找出害她流产的凶手\"'
                    #break
                if item['docs'] != None and item['docs'].find('黑色拔膏棍的理论内涵及临床应用') != -1:
                    #print(item)
                    item['docs'] = '\"黑色拔膏棍的理论内涵及临床应用 拔膏棍是中医传统外治法之一,其历史悠久,源远流长,拔膏棍疗法具有操作简单,疗效显著,适应症广泛等特点,在临床应用中具有重要价值\"'
                    #break
                
            清理后的项 = {}
            for key, value in item.items():
                # 检查缺失值
                if value is None or (isinstance(value, str) and value.strip() == ''):
                    value = 'blank'
                
                # 检查非法字符
                if isinstance(value, str):
                    # 移除控制字符
                    value = ''.join(char for char in value if ord(char) >= 32 or char == '\n')
                    # 替换 Neo4j 中的特殊字符
                    value = value.replace('\'','').replace('"', "").replace('\\', '/').replace('：', ' ').replace(':', ' ')
                    value = value.replace('。', '   ').replace('．', '').replace('４', '4').replace('２', '2').replace('３', '3').replace('５', '5').replace('６', '6').replace('７', '7').replace('８', '8').replace('９', '9').replace('０', '0')
                    value = value.replace('１', '1').replace('－', '-').replace('＋', '+').replace('＊', '*').replace('／', '/').replace('％', '%').replace('＝', '=').replace('＜', '<').replace('＞', '>').replace('［', '[').replace('］', ']').replace('｛', '{').replace('｝', '}').replace('（', '(').replace('）', ')').replace('＿', '_').replace('－', '-').replace('＋', '+').replace('＊', '*').replace('／', '/').replace('％', '%').replace('＝', '=').replace('＜', '<').replace('＞', '>').replace('［', '[').replace('］', ']').replace('｛', '{').replace('｝', '}').replace('（', '(').replace('）', ')').replace('＿', '_')
                    value = value.replace('，', ',').replace('黄连素04-05/日', '黄连素4-5/日').replace('百分之','%')
                    # 修复无效的十进制字面值
                    value = value.replace('，但......','\"').replace('黄连素4-5/日', '黄连素4-5/日').replace('、', ',').replace('......','').replace('《','(').replace('》',')')
                    value = value.replace('“','').replace('”','').replace('；',';').replace('，',',').replace('！','!').replace('？','?')
                    value = value.replace('由 组成','由_组成').replace('与 相关','与_相关').replace('由 治疗','由_治疗').replace('由 导致','由_导致')                    
                    value = value.replace('与 有关','与_有关').replace('由 建立','由_建立').replace('由 发明','由_发明').replace('由 提出','由_提出')
                    value = value.replace('由 创造','由_创造').replace('由 研发','由_研发').replace('有 功效','有_功效').replace('由 主导','由_主导')
                    清理后的项[key] = value
            
            清理后的数据.append(清理后的项)
        
        return 清理后的数据

    
    # 读取所有pkl文件并处理
    for filename in os.listdir(filepath):
        if filename.endswith('.pkl') and filename == '关系抽取训练集.pkl':
            full_path = os.path.join(filepath, filename)
            with open(full_path, 'rb') as f:
                data = pickle.load(f)
            
            # 确保数据是列表形式
            if not isinstance(data, list):
                data = [data]
            data = 检查并清理数据(data)
            # 写入Neo4j
            with driver.session() as session:
                # 清空Neo4j数据库中的所有数据
                #session.run("MATCH (n) DETACH DELETE n")
                #print("Neo4j数据库已清空。")
                session.write_transaction(create_node_and_relationships, data)

    # 关闭数据库连接
    driver.close()

    print("所有pkl文件已成功写入Neo4j数据库。")

def 连接Neo4j数据库():
    uri = "bolt://10.100.4.14:7687"
    用户名 = "neo4j"
    密码 = "Liuzichen"  # 请替换为您的实际密码
    driver = GraphDatabase.driver(uri, auth=(用户名, 密码))
    return driver
def 清空Neo4j数据库(driver):
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        print("Neo4j数据库已清空。")
    driver.close()

def 写入Neo4j数据库(driver, data):
    def create_node_and_relationships(tx, data):
        for item in data:
            # 为每个字典创建一个唯一标识符
            unique_id = str(hash(frozenset(item.items())))
            
            # 创建节点和关系
            for key, value in item.items(): 
                tx.run(
                    "MERGE (n:%s {name: $value})" % key,
                    value=str(value)
                )
                
                # 创建关系
                tx.run(
                    "MATCH (a:%s {name: $value}), (b:UniqueItem {id: $id}) "
                    "MERGE (b)-[r:HAS_PROPERTY]->(a)" % key,
                    value=str(value), id=unique_id
                )
            
            # 创建一个唯一项节点来连接所有属性
            tx.run(
                    "MERGE (u:UniqueItem {id: $id})",
                    id=unique_id
            )

    with driver.session() as session:
        session.write_transaction(create_node_and_relationships, data)

        print("数据已成功写入Neo4j数据库。")

if __name__ == "__main__":
    #write_pkl_to_neo4j('pkl')
    #driver = 连接Neo4j数据库()
    #清空Neo4j数据库(driver)

    read_neo4j_to_networkx()
