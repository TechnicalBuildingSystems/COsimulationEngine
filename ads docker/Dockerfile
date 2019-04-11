FROM python:3
WORKDIR /ads
COPY requirements.txt ./
COPY REST2ADS.py ./
RUN pip install --no-cache-dir -r requirements.txt
CMD [ "python" , "./REST2ADS.py" ]