FROM python:3.9
RUN apt update -qq && apt upgrade -y
WORKDIR /gene_expression_api
COPY requirements.txt requirements.txt
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8000
COPY . .
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "480"]