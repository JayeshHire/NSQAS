FROM python:3.12-slim

WORKDIR /app

COPY ./project/ ./

COPY ./requirements.txt ./

# upgrade pip and install all dependencies
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt


EXPOSE 8501

RUN python -m database.create_tables

# Run the streamlit app
CMD ["streamlit", "run", "/app/main.py", "--server.port=8501"]
