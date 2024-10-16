import os
import csv
import pickle


import pandas as pd
import pickle

def txt_to_csv_and_pkl(txtfile):
    # 指定目录路径
    directory = 'data/第二批数据'
    
    # 确保 pkl 目录存在
    if not os.path.exists('pkl'):
        os.makedirs('pkl')
    
    # 遍历目录下的所有文件
    for filename in os.listdir(directory):
        if filename.endswith('.txt') and filename == txtfile:
            txt_path = os.path.join(directory, filename)
            csv_path = os.path.join(directory, filename[:-4] + '.csv')
            pkl_path = os.path.join('pkl', filename[:-4] + '.pkl')
            
            # 读取TXT文件
            with open(txt_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # 解析数据
            data = [line.strip().split('\t') for line in lines]
            
            # 创建DataFrame
            try:
                df = pd.DataFrame(data[1:], columns=data[0])
            except Exception as e:
                print(f"Error: {e}")
                print(f"Data: {data}")
            
            # 保存为CSV文件
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            
            # 将数据转换为字典列表
            data_list = []
            for index, row in df.iterrows():
                data_dict = {col: row[col] for col in df.columns}
                data_list.append(data_dict)
            
            # 保存为PKL文件
            with open(pkl_path, 'wb') as pkl_file:
                pickle.dump(data_list, pkl_file)
            
            print(f"已将 {filename} 转换为 CSV 格式并保存，同时保存为 PKL 格式")
def csv_to_pkl_final2(csv_file):
    # 指定目录路径
    directory = 'data/第一批数据'
    
    # 确保 pkl 目录存在
    if not os.path.exists('pkl'):
        os.makedirs('pkl')
    
    # 遍历目录下的所有文件
    for filename in os.listdir(directory):
        if filename == csv_file:
            if filename.endswith('.csv'):
        
                csv_path = os.path.join(directory, filename)
                
                pkl_path = os.path.join('pkl', filename[:-4] + '.pkl')
                
                # 读取TXT文件
                with open(csv_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                
                # 解析数据
                data = [line.strip().split('\t') for line in lines]
                
                # 创建DataFrame
                try:
                    df = pd.DataFrame(data[1:], columns=data[0])
                except Exception as e:
                    print(f"Error: {e}")
                    print(f"Data: {data}")
                
                # 保存为CSV文件
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                
                # 将数据转换为字典列表
                data_list = []
                for index, row in df.iterrows():
                    data_dict = {col: row[col] for col in df.columns}
                    data_list.append(data_dict)
                
                # 保存为PKL文件
                with open(pkl_path, 'wb') as pkl_file:
                    pickle.dump(data_list, pkl_file)
                
                print(f"已将 {filename} 转换为 CSV 格式并保存，同时保存为 PKL 格式")

def read_csv_and_save_pkl_final(csv_file):
    # 指定目录路径
    directory = 'data/第一批数据'
    
    # 确保 pkl 目录存在
    if not os.path.exists('pkl'):
        os.makedirs('pkl')
    # 遍历目录下的所有文件
    for filename in os.listdir(directory):
        if filename == csv_file:
            if filename.endswith('.csv'):
                csv_path = os.path.join(directory, filename)
                pkl_path = os.path.join('pkl', filename[:-4] + '.pkl')
                # 读取CSV文件到DataFrame
                try:    
                    df = pd.read_csv(csv_path, encoding='utf-8', quoting=csv.QUOTE_ALL, error_bad_lines=False)
                except Exception as e:
                    print(f"Error: {e}")
                    #print(f"Data: {data}")
                
                # 将DataFrame转换为字典列表
                data_list = df.to_dict('records')
                
                # 保存为PKL文件
                with open(pkl_path, 'wb') as pkl_file:
                    pickle.dump(data_list, pkl_file)
                
                print(f"已将 {filename} 读取为DataFrame并保存为PKL格式")
    

def read_csv_and_save_pkl():
    # 确保 pkl 目录存在
    if not os.path.exists('pkl'):
        os.makedirs('pkl')

    # 获取 data 目录下所有的 CSV 文件
    csv_files = [f for f in os.listdir('data/第一批数据') if f.endswith('.csv')]

    for csv_file in csv_files:
        data = []
        with open(os.path.join('data/第一批数据', csv_file), 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for i, row in enumerate(csv_reader, 1):
                # 将每一行的列数据赋值给 col1, col2, col3 等变量
                if len(row) > 0:
                    cols = [f'col{j+1}' for j in range(len(row))]
                    row_data = dict(zip(cols, row))
                    
                    # 将行数据封装在 row1, row2 等变量中
                    row_name = f'row{i}'
                    data.append({row_name: row_data})

        # 将数据保存为 pkl 文件
        pkl_filename = os.path.splitext(csv_file)[0] + '.pkl'
        with open(os.path.join('pkl', pkl_filename), 'wb') as pkl_file:
            pickle.dump(data, pkl_file)

        print(f"已将 {csv_file} 处理并保存为 {pkl_filename}")

def read_pkl_files():
    # 确保 pkl 目录存在
    if not os.path.exists('pkl'):
        print("pkl 目录不存在")
        return

    # 获取 pkl 目录下所有的 pkl 文件
    pkl_files = [f for f in os.listdir('pkl') if f.endswith('.pkl')]

    for pkl_file in pkl_files:
        with open(os.path.join('pkl', pkl_file), 'rb') as file:
            data = pickle.load(file)
        
        print(f"文件 {pkl_file} 的数据:")
        print(f"数据类型: {type(data)}")
        print(f"数据长度: {len(data)}")
        
        print("遍历数据元素:")
        n = 0
        for item in data:
            n += 1
            if n < 10:
                print(item)
            else:
                break
        
        print("\n" + "="*50 + "\n")

def read_pklfile(pkl_file):
     with open(os.path.join('pkl', pkl_file), 'rb') as file:
            data = pickle.load(file)
        
            print(f"文件 {pkl_file} 的数据:")
            print(f"数据类型: {type(data)}")
            print(f"数据长度: {len(data)}")
            
            print("遍历数据元素:")
            
            for item in data:
                
                print(item,type(item))  
                
            print("\n" + "="*50 + "\n")
def read_pklfile_and_clear(pkl_file):
      with open(os.path.join('pkl', pkl_file), 'rb') as file:
            data = pickle.load(file)
            print('typedata:',type(data))
            print(f"文件 {pkl_file} 的数据:")
            print(f"数据类型: {type(data)}")
            print(f"数据长度: {len(data)}")
            data1 = []
            print("遍历数据元素:")
            n = 0
            for item in data:
                print(type(item))
                n += 1
                if n <= 104:
                    print(item)
                    data1.append(item)
                else:
                    break
            # 将data1写成pickle文件
            新文件名 = f"清理后_{pkl_file}"
            with open(os.path.join('pkl', 新文件名), 'wb') as 新文件:
                pickle.dump(data1, 新文件)
            print(f"已将清理后的数据写入pickle文件: {新文件名}")
            print("\n" + "="*50 + "\n")         




if __name__ == "__main__":
    # 调用函数
    txt_to_csv_and_pkl('关系抽取训练集.txt')
    #read_pklfile_and_clear('皮肤科知识库师承.pkl')
    #read_csv_and_save_pkl_final('02皮肤科知识库名医.csv')
    #txt_to_csv_and_pkl()
    #txt_to_csv_and_pkl()
    #read_csv_and_save_pkl()
    #read_pkl_files()
    #csv_to_pkl_final2('01皮肤科医案数据集.csv')
    #read_pklfile('01皮肤科医案数据集.pkl')
    #read_pklfile('曲剑华.pkl')
    #read_pklfile('王萍.pkl')
    #read_pklfile('赵炳南.pkl')
    #read_csv_and_save_pkl_final('01皮肤科医案数据集.csv')
    #G = read_neo4j_to_networkx()
    #print(G.nodes)
    #print(G.edges)
    
