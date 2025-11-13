FROM python:slim

RUN useradd agent-directory

WORKDIR /home/agent-directory

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY agent-directory.py config.py boot.sh ./
COPY conf conf
RUN chmod +x boot.sh

ENV FLASK_APP agent-directory.py

RUN chown -R agent-directory:agent-directory ./
USER agent-directory

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]