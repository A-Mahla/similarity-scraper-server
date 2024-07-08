FROM python:3.10-slim as builder

WORKDIR /docs

COPY mkdocs/requirements.txt .

RUN pip install -r requirements.txt

COPY mkdocs .

RUN mkdocs build

FROM nginx:latest

COPY --from=builder /docs/site /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]