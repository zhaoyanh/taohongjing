import streamlit as st
import os
import json
from read_write_Neo4j import read_neo4j_to_networkx
from relationquery import relationHome

import networkx as nx
import plotly.graph_objects as go



def save_file_to_data_dir(file, content):
                    # 确保 data 目录存在
                    if not os.path.exists('data'):
                        os.makedirs('data')
                    
                    # 保存文件内容到 data 目录
                    file_path = os.path.join('data', file.name)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    st.success(f"文件 '{file.name}' 已保存到 data 目录")
def create_streamlit_app():
    # 设置页面布局
    st.set_page_config(layout="wide")
    st.title("朔盟1958-2024年第三届中医药知识图谱大赛")


 
    # 创建左侧导航栏和右侧内容区
    col1, col2 = st.columns([0.15, 0.85])

    # 左侧导航栏
    with col1:
        st.sidebar.title("导航")
        page = st.sidebar.radio("选择页面", ["数据清洗", "关系数据检索", "知识图谱", "RAGonLLM"])

    # 右侧内容区
    
   
    with col2:
        
        if page == "数据清洗":
            #st.header("数据清洗")
            
            # 创建左右两列
            col_left,col_right = st.columns([0.5,0.5])
            file_contents = ""
            # 左侧列：文件提交窗口
            with col_left:
                st.subheader("提交数据文件")
                
                # 下方功能区：文件上传按钮
                uploaded_files = st.file_uploader(
                    "浏览文件上传",
                    accept_multiple_files=True,
                    type=["txt", "md",'csv']
                )
                #print(len(uploaded_files),type(uploaded_files),uploaded_files)
                
                if uploaded_files:
                    for file in uploaded_files:
                        # 处理上传的文件
                        file_contents = file.read()
                        # 尝试使用 UTF-8 解码
                        try:
                            file_contents = file_contents.decode("utf-8")
                        except UnicodeDecodeError:
                            # 如果 UTF-8 解码失败，尝试使用 GBK 解码（常见于中文 Windows 系统）
                            try:
                                file_contents = file_contents.decode("gbk")
                            except UnicodeDecodeError:
                                # 如果 GBK 也失败，使用 latin-1 编码（可以解码任何字节串，但可能导致乱码）
                                file_contents = file_contents.decode("latin-1")
                                st.warning("无法正确识别文件编码，显示的内容可能不正确。")

                        st.write(f"文件 '{file.name}' 已上传")
                        # 调用函数保存文件
                        # 这里可以添加将文件保存到服务器的逻辑
                        save_file_to_data_dir(file, file_contents)
                        
                        
                # 添加文件夹显示框
                def get_file_tree(path):
                    tree = []
                    for root, dirs, files in os.walk(path):
                        level = root.replace(path, '').count(os.sep)
                        indent = ' ' * 4 * (level)
                        tree.append(f"{indent}{os.path.basename(root)}/")
                        subindent = ' ' * 4 * (level + 1)
                        for f in files:
                            tree.append(f"{subindent}{f}")                   
                    return tree

                globaltree = get_file_tree('data')
                
                # 创建一个带有右侧下拉条的容器，用于显示文件树
                with st.container():
                    st.subheader("已上传数据文件")
                    file_tree_container = st.empty()
                    with file_tree_container.container():
                        scrollable_container = st.container()
                        with scrollable_container:
                                                      
                            for i, item in enumerate(globaltree):
                                if item.strip().endswith('/'):
                                    st.markdown(f"**{item.strip()}**")
                                else:
                                    if st.button(item.strip(), key=f"file_{i}"):
                                        if i <= 19:
                                            file_path = 'data/'+globaltree[1].strip()+item.strip()
                                        elif i == 21:
                                            file_path = 'data/'+globaltree[20].strip()+item.strip() 
                                        else:
                                            file_path = 'data/'+globaltree[20].strip()+globaltree[22].strip()+item.strip()
                                        print(file_path)
                                        st.session_state.selected_file = file_path
                                        st.write(f"已选择文件：{file_path}")
                          
                
                
               
            # 右侧列：可以添加其他功能或留空
            with col_right:
                st.write("")
                st.subheader("查看文件内容")
                
                
                if 'selected_file' in st.session_state:
                    selected_file = st.session_state.selected_file
                    with open(selected_file, 'r', encoding='utf-8') as file:
                        file_contents = file.read()
                        st.write(file_contents)
                # 在这里可以添加其他相关功能
            # 在这里添加数据清洗相关的内容
        elif page == "关系数据检索":
            #st.header("关系数据检索")
            relationHome()
        elif page == "知识图谱":
            # 调用函数获取NetworkX图
            G = read_neo4j_to_networkx()

            # 创建节点坐标
            pos = nx.spring_layout(G)

            # 创建边的轨迹
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888fff'),
                hoverinfo='none',
                mode='lines')

            # 创建节点
            node_x = [pos[node][0] for node in G.nodes()]
            node_y = [pos[node][1] for node in G.nodes()]

            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers',
                hoverinfo='text',
                marker=dict(
                    showscale=True,
                    colorscale='agsunset',
                    
                    size=10,
                    colorbar=dict(
                        thickness=15,
                        title='节点连接数',
                        xanchor='left',
                        titleside='right'
                    )
                )
            )

            # 设置节点的颜色
            node_adjacencies = []
            node_text = []
            for node, adjacencies in G.adjacency():
                node_adjacencies.append(len(adjacencies))
                node_text.append(f'节点 {node} 连接数: {len(adjacencies)}')

            node_trace.marker.color = node_adjacencies
            node_trace.text = node_text

            # 创建图形布局
            layout = go.Layout(
                title='知识图谱',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                width=600,
                height=600
            )

            # 创建图形
            fig = go.Figure(data=[edge_trace, node_trace], layout=layout)

            # 在Streamlit中显示图形
            st.plotly_chart(fig)
            # 在这里添加知识图谱相关的内容
        elif page == "RAGonLLM":
            st.header("RAGonLLM")
            # 在这里添加RAGonLLM相关的内容

if __name__ == "__main__":
    create_streamlit_app()