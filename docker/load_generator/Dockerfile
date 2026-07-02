FROM python:3.10.20-trixie

RUN python3 -m pip install psycopg2

COPY loadgen.py .

CMD ["python3", "loadgen.py"]
