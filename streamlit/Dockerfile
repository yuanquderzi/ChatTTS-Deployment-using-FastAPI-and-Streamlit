# 使用官方Python运行时作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /streamlit

# 将当前目录的内容复制到容器中的/streamlit目录
COPY ui.py /streamlit
COPY requirements.txt /streamlit

# 安装requirements.txt中指定的所有依赖包
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 暴露Streamlit的默认端口
EXPOSE 8501

# 运行Streamlit应用
CMD ["streamlit", "run", "ui.py"]
