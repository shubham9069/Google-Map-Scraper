FROM selenium/standalone-firefox:127.0.1-geckodriver-0.34.0-20240621


RUN sudo apt-get update && sudo apt install python3-pip -y

WORKDIR /app
COPY . /app

RUN pip3 install -r requirements.txt

ENV ZIP_CODE=71256

# Pass the name of the function handler as an argument to the runtime
CMD [ "python3","lambda_function.py" ]

# -------- docker build -t gmap-scarper . cmd --platform linux/amd64 ---------for mac