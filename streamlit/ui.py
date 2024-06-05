import streamlit as st
import requests
import json
import re
from cn2an import an2cn

def convert_arabic_to_chinese_in_string(s):
    def replace_func(match):
        number = match.group(0)
        return an2cn(number)

    # 匹配所有的阿拉伯数字
    converted_str = re.sub(r'\d+', replace_func, s)
    return converted_str

def synthesize_speech(text, output_path, seed, url="http://localhost:8000/tts"):  # docker部署localhost改为fastapi
    payload = {
        "text": text,
        "output_path": output_path,
        "seed": seed
    }
    
    headers = {
        "content-type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            st.success(f"语音合成成功，输出保存到 {output_path}.")
            return True
        else:
            st.error(f"语音合成失败，状态码: {response.status_code}")
            st.error(f"响应: {response.text}")
            return False
    
    except Exception as e:
        st.error(f"发生错误: {e}")
        return False

# 初始化session state
if 'synthesized' not in st.session_state:
    st.session_state.synthesized = False
if 'output_path' not in st.session_state:
    st.session_state.output_path = ""

st.title("ChatTTS语音合成接口")
st.write("输入文本、输出文件路径和种子值，生成语音文件。")

text = st.text_area("输入文本")
text = convert_arabic_to_chinese_in_string(text)
output_path = st.text_input("输出文件路径", "output.wav")
seed = st.number_input("种子值", value=0)

if st.button("合成语音"):
    if synthesize_speech(text, output_path, seed):
        st.session_state.synthesized = True
        st.session_state.output_path = '/fastapi/' + output_path

if st.session_state.synthesized:
    # 播放生成的音频文件
    audio_file = open(st.session_state.output_path, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/wav')
    
    # 提供下载链接
    with open(st.session_state.output_path, 'rb') as f:
        st.download_button(
            label="下载生成的语音文件",
            data=f,
            file_name=output_path,
            mime='audio/wav'
        )

