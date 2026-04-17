FROM python:slim

RUN useradd agent-directory

WORKDIR /home/agent-directory

RUN apt-get update && apt-get install -y git

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY app app
COPY agent-directory.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP agent-directory.py

RUN chown -R agent-directory:agent-directory ./
USER agent-directory

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]