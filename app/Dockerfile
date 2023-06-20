FROM public.ecr.aws/lambda/python:3.10

COPY app.py requirements.txt ./
COPY model model

RUN python3.10 -m pip install --no-cache-dir --use-pep517 -r requirements.txt -t .

CMD ["app.lambda_handler"]
