FROM python:3
WORKDIR /fmu
COPY requirements.txt ./
COPY RuleBasedController_Linux.fmu REST2FMI.py ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8081
CMD [ "python" , "./REST2FMI.py" ]