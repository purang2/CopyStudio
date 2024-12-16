import streamlit as st
from openai import OpenAI
import google.generativeai as genai
from anthropic import Anthropic
from datetime import datetime
import pandas as pd
import json
import pathlib
from typing import Dict, List, Optional
from dataclasses import dataclass

from PIL import Image
import plotly.express as px 
import plotly.graph_objects as go
from typing import Dict, List, Optional, Union

from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google.api_core.exceptions import ResourceExhausted

import folium
from streamlit_folium import folium_static
import random
import re 


# Page config must be the first Streamlit command
st.set_page_config(
    page_title="광고카피 문구 생성 AI - Copybara", 
    page_icon="🐾", 
    layout="wide"
)

# 앱 제목

st.markdown("""
<style>
    .header-title {
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
    }
    .sub-header {
        font-size: 1.2em;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
<h1 class="header-title">Copybara - 광고 카피 생성 AI</h1>
<p class="sub-header">당신의 광고 카피를 감성적이고 창의적으로 변신시키는 AI 도우미</p>
""", unsafe_allow_html=True)

# **튜토리얼 섹션**
st.markdown("""
### 👋 처음 오셨나요?
1️⃣ 지역과 세대를 선택하세요  
2️⃣ 필요하면 계절과 MBTI를 추가 설정하세요  
3️⃣ 원하는 프롬프트를 수정하거나 기본 설정을 그대로 사용하세요  
4️⃣ 광고 카피를 생성하고, 평가를 확인하세요  
""")

