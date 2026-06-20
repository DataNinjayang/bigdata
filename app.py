import streamlit as st
import jieba
import jieba.analyse
from collections import Counter
import re
import json
import os
import pandas as pd

# ========== AI分析函数（必须在UI之前定义）==========
def ai_analyze(text):
    """AI文本分析：情感分析、关键词提取、风险定级"""
    # 使用jieba进行分词和关键词提取
    words = list(jieba.cut(text))
    
    # 情感词典（简化版）
    positive_words = {'好', '优秀', '满意', '感谢', '支持', '赞', '棒', '不错', '喜欢', '成功', '顺利', '方便', '舒适', '安全'}
    negative_words = {'差', '糟糕', '不满', '投诉', '问题', '故障', '危险', '困难', '麻烦', '失望', '愤怒', '担心', '害怕', '烦', '坏', '慢', '贵'}
    
    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)
    
    if pos_count > neg_count:
        sentiment = "正面"
    elif neg_count > pos_count:
        sentiment = "负面"
    else:
        sentiment = "中性"
    
    # 提取关键词
    keywords = jieba.analyse.extract_tags(text, topK=3, withWeight=False)
    key_word = "、".join(keywords) if keywords else "暂无明确诉求"
    
    # 风险定级
    urgent_words = {'紧急', '危险', '事故', '伤亡', '爆炸', '火灾', '漏电', '坍塌', '中毒'}
    high_risk_words = {'严重', '多次', '长期', '普遍', '群体', '聚集', '上访'}
    
    urgent_count = sum(1 for w in words if w in urgent_words)
    high_risk_count = sum(1 for w in words if w in high_risk_words)
    
    if urgent_count > 0:
        level = "🔴 一级（紧急）"
    elif high_risk_count > 0 or neg_count >= 3:
        level = "🟠 二级（高风险）"
    elif neg_count > 0:
        level = "🟡 三级（中风险）"
    else:
        level = "🟢 四级（低风险）"
    
    return {
        "sentiment": sentiment,
        "key_word": key_word,
        "level": level
    }

def generate_wordcloud_data(text):
    """生成词云数据"""
    # 使用jieba提取关键词和权重
    keywords = jieba.analyse.extract_tags(text, topK=20, withWeight=True)
    
    # 转换为词云需要的格式
    word_list = []
    for word, weight in keywords:
        word_list.append([word, int(weight * 1000)])
    
    return word_list

# ========== 页面配置 ==========
st.set_page_config(
    page_title="AI驱动·城市民生大数据智能分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== 自定义CSS样式 ==========
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #2d5bcc;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 30px;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .block-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 4px solid #2d5bcc;
    }
    .result-box {
        background-color: #e3f2fd;
        border-radius: 8px;
        padding: 15px;
        margin-top: 15px;
        border-left: 4px solid #2196f3;
    }
    .stButton>button {
        background-color: #2d5bcc;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 500;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #1e3a8a;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(45, 92, 204, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ========== 标题 ==========
st.markdown('<h1 class="main-title">AI驱动·城市民生大数据智能分析平台</h1>', unsafe_allow_html=True)

# ========== 1. 大数据来源区块 ==========
with st.container():
    st.markdown('<div class="block-container">', unsafe_allow_html=True)
    st.markdown("### 📊 合规大数据数据源（可溯源）")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        **🏛️ 政务开放API**
        - 12345市民工单
        - 市政投诉台账
        - 公共服务公示数据
        """)
    with col2:
        st.markdown("""
        **🌐 公开网络爬取**
        - 本地论坛数据
        - 短视频平台评论
        - 社交平台公开内容
        """)
    with col3:
        st.markdown("""
        **📡 第三方开放接口**
        - 热搜指数数据
        - 交通流量数据
        - 气象与客流数据
        """)
    with col4:
        st.markdown("""
        **📈 数据体量规模**
        - 日新增: 12万+条
        - 全库结构化: 1100万+条
        - 符合大数据特征
        """)
    st.markdown('</div>', unsafe_allow_html=True)

# ========== 2. AI交互面板 + 图表 ==========
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown('<div class="block-container">', unsafe_allow_html=True)
    st.markdown("### 🤖 AI分析功能区")
    st.markdown("输入民生文本，AI完成：**分词 / 情感判定 / 风险定级 / 关键词提取**")
    
    text_input = st.text_area(
        "粘贴投诉、反馈文本",
        height=120,
        placeholder="例如：小区物业管理不善，电梯经常故障，居民出行不便，希望相关部门介入处理...",
        key="text_input"
    )
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        analyze_btn = st.button("🔍 AI情感&诉求分析", use_container_width=True)
    with col_btn2:
        wordcloud_btn = st.button("☁️ AI生成关键词词云", use_container_width=True)
    
    # 分析结果展示
    if analyze_btn and text_input.strip():
        with st.spinner("AI正在分析中..."):
            result = ai_analyze(text_input)
        
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        sentiment_color = 'green' if result['sentiment'] == '正面' else 'red' if result['sentiment'] == '负面' else 'orange'
        st.markdown(f"""
        **🎯 情感倾向：** <span style="color: {sentiment_color}">{result['sentiment']}</span>
        
        **🔑 核心诉求：** {result['key_word']}
        
        **⚠️ 舆情风险等级：** {result['level']}
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    elif analyze_btn and not text_input.strip():
        st.warning("⚠️ 请输入文本内容后再进行分析")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="block-container">', unsafe_allow_html=True)
    st.markdown("### 📈 舆情热度统计 & AI聚类词云")
    
    # 热度统计图表
    chart_data = pd.DataFrame({
        '类别': ['物价', '交通', '教育', '物业', '水电'],
        '热度指数': [1280, 2150, 960, 1830, 1540]
    })
    
    st.bar_chart(chart_data.set_index('类别'), use_container_width=True)
    
    # 词云展示
    if wordcloud_btn and text_input.strip():
        with st.spinner("AI正在生成词云..."):
            word_list = generate_wordcloud_data(text_input)
        
        if word_list:
            st.markdown("**🎨 AI智能关键词词云**")
            # 使用Streamlit原生方式展示关键词
            word_df = pd.DataFrame(word_list[:15], columns=['关键词', '权重'])
            st.dataframe(word_df, use_container_width=True, hide_index=True)
            
            # 使用条形图展示词频
            chart_word = pd.DataFrame(word_list[:10], columns=['关键词', '权重'])
            st.bar_chart(chart_word.set_index('关键词'), use_container_width=True)
        else:
            st.info("ℹ️ 未能提取到有效关键词，请尝试输入更长的文本")
    
    elif wordcloud_btn and not text_input.strip():
        st.warning("⚠️ 请输入文本内容后再生成词云")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== 3. 部署说明 ==========
with st.container():
    st.markdown('<div class="block-container">', unsafe_allow_html=True)
    st.markdown("### 🌐 对外提供服务方式")
    
    deploy_col1, deploy_col2 = st.columns(2)
    with deploy_col1:
        st.markdown("""
        **① 本地运行**
        ```bash
        pip install -r requirements.txt
        streamlit run app.py
        ```
        浏览器访问：`http://localhost:8501`
        """)
    with deploy_col2:
        st.markdown("""
        **② Streamlit Cloud部署**
        1. 将代码推送到GitHub仓库
        2. 访问 [share.streamlit.io](https://share.streamlit.io)
        3. 连接GitHub仓库并部署
        4. 获得公网访问链接
        """)
    st.markdown('</div>', unsafe_allow_html=True)

# ========== 页脚 ==========
st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>AI大数据民生舆情分析平台 | Powered by Streamlit & Jieba</p>", unsafe_allow_html=True)
