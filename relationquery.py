import streamlit as st
import pandas as pd
import os
def relationHome():
    关系表列表 = [
        "皮肤科医案数据集", "皮肤科知识库临证经验", "皮肤科知识库临床研究", "皮肤科知识库名医", 
        "皮肤科知识库图书", "皮肤科知识库学术思想", "皮肤科知识库师承", "皮肤科知识库特色用药",
        "皮肤科知识库期刊", "皮肤科知识库经验方", "皮肤科知识库医案", "关系抽取训练集",
        "皮肤科知识库名医论文",
    ]

    def 显示关系表(表名):
        st.title(表名)
        文件路径 = os.path.join("pkl", f"{表名}.pkl")
        if os.path.exists(文件路径):
            df = pd.read_pickle(文件路径)
            st.dataframe(df)
            
            # 这里可以添加增删改查的功能
            st.write("增删改查功能待实现")
        else:
            st.error(f"未找到 {表名} 的数据文件")

    
    
    st.container().height = 50
    st.write(" \n")
    st.write(" \n")
    st.write(" \n")
    st.write(" \n")
    列1, 列2, 列3 = st.columns(3)
    
    for i, 表名 in enumerate(关系表列表):
        if i % 3 == 0:
            with 列1:
                if st.button(表名):
                    
                    显示关系表(表名)
        elif i % 3 == 1:
            with 列2:
                if st.button(表名):
                    显示关系表(表名)
        else:
            with 列3:
                if st.button(表名):
                    显示关系表(表名)
        
        