FROM 172.22.111.199:80/itp/python:2.7
WORKDIR /code
COPY requirement.pip ./
ENV PIP_TRUSTED_HOST=mirrors.aliyun.com
RUN pip install -i http://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r requirement.pip
