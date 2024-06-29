import random

import streamlit as st
import requests
import json
import re
from cn2an import an2cn
import os

# 通过env检测是否为docker环境
try:
    if os.environ['docker_env'] == True:
        hostname = 'fastapi'
except KeyError:
    hostname = "localhost"


def convert_arabic_to_chinese_in_string(s):
    def replace_func(match):
        number = match.group(0)
        return an2cn(number)

    # 匹配所有的阿拉伯数字
    converted_str = re.sub(r'\d+', replace_func, s)
    return converted_str


def synthesize_speech(text, promt, url=f"http://{hostname}:8000/tts"):
    payload = {
        "text": text,
        "prompt": promt
    }

    headers = {
        "content-type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            with open('temp_audio.wav', 'wb') as f:
                f.write(response.content)
            st.success(f"语音合成成功.")
            return True
        else:
            st.error(f"语音合成失败，状态码: {response.status_code}")
            st.error(f"响应: {response.text}")
            return False

    except Exception as e:
        st.error(f"发生错误: {e}")
        return False


def get_voices():
    try:
        response = requests.get(f"http://{hostname}:8000/get_voices")
        voices = json.loads(response.text)
        return voices
    except Exception as e:
        st.error(f"发生错误: {e}")
        return False


# 初始化session state
if 'synthesized' not in st.session_state:
    st.session_state.synthesized = False

st.title("ChatTTS语音合成接口")
st.write("输入文本、输出文件路径和种子值，生成语音文件。")

text = st.text_area("输入文本")
text = convert_arabic_to_chinese_in_string(text)

col1, col2, col7 = st.columns(3)
if 'seed' not in st.session_state:
    st.session_state.seed = 0
if 'use_voice' not in st.session_state:
    st.session_state.use_voice = False
    st.session_state.speaker_id = 0
with col1:
    seed = st.number_input("种子值", value=st.session_state.seed, min_value=0, max_value=1000000000, key='seed_input')

with col2:
    if st.button("随机"):
        st.session_state.use_voice = False
        # 按钮被点击时，生成一个随机数
        random_number = random.randint(1, 1000000000)
        st.session_state.seed = random_number
        st.rerun()
    use_voice = st.checkbox("使用预设", value=st.session_state.use_voice)
with col7:
    if use_voice:
        print(use_voice)
        voices = get_voices()
        if voices is not False:
            options = list(voices.keys())
            description = [f'{key}: {value["gender"]}, {value["describe"]}' for key, value in voices.items()]
            st.session_state.speaker_id = st.selectbox('请选择一个选项:', options=options, format_func=lambda x: description[int(x) - 1])
    skip_refine_text_value = st.checkbox("跳过预处理文本", value=True, key='refine_text')
if st.session_state.speaker_id:
    st.write(f"使用预设的声音: {voices[str(st.session_state.speaker_id)]['describe']}")
col3, col4 = st.columns(2)
with col3:
    temperature = st.slider("temperature（使用预设时失效）", min_value=0.01, max_value=2.0, value=0.3, step=0.01)
with col4:
    top_p = st.slider("top_p（使用预设时失效）", min_value=0.1, max_value=1.0, value=0.7, step=0.1)
col5, col6 = st.columns(2)
with col5:
    top_k = st.slider("top_k（使用预设时失效）", min_value=1, max_value=50, value=20, step=1)
with col6:
    speed = st.slider("speed", min_value=0, max_value=9, value=2, step=1)

if st.button("合成语音"):
    print(st.session_state.speaker_id)
    if synthesize_speech(text, {
        "seed": seed,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "prompt": speed,
        "skip_refine_text_value": skip_refine_text_value,
        "speaker_id": int(st.session_state.speaker_id)
    },
                         ):
        st.session_state.synthesized = True

if st.session_state.synthesized:
    # 播放生成的音频文件
    audio_file = open('temp_audio.wav', 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/wav')

    # 提供下载链接
    with open('temp_audio.wav', 'rb') as f:
        st.download_button(
            label="下载生成的语音文件",
            data=f,
            file_name='temp_audio.wav',
            mime='audio/wav'
        )
