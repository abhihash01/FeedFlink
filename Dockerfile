FROM python:3.11-slim 
EXPOSE 6067
RUN pip install Flask pymongo kafka-python
