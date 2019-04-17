FROM python:3
RUN mkdir -p /database
WORKDIR /usr/cso
COPY requirements.txt ./
COPY CoSimulationManager.py CoSimulationOrchestrator.py DatabaseManager.py ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 3030
CMD [ "python" , "./CoSimulationOrchestrator.py" ]