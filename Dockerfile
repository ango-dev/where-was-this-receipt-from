# Static site served by nginx. docs/ holds index.html and rates.csv.
FROM nginx:alpine
COPY docs/ /usr/share/nginx/html/
EXPOSE 80
