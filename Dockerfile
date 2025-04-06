FROM amazonlinux:latest

RUN yum update -y && yum install -y zip bash awscli
COPY .env /app/
COPY scripts/setup.sh /app/

WORKDIR /app

RUN chmod +x setup.sh

CMD ["bash", "./setup.sh"]