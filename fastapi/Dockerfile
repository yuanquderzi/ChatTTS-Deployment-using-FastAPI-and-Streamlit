# 使用官方Python运行时作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /fastapi

# 将当前目录的内容复制到容器中的/fastapi目录
COPY . /fastapi
COPY requirements.txt /fastapi

# 安装requirements.txt中指定的所有依赖包
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 暴露8000端口
EXPOSE 8000

# 运行FastAPI应用的uvicorn服务器
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]