FROM node:lts-alpine AS build
WORKDIR /app
COPY package*.json ./
#COPY *js ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:stable-alpine AS production-stage
COPY default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
COPY entrypoint.sh /usr/share/nginx/html/entrypoint.sh
RUN chmod +x /usr/share/nginx/html/entrypoint.sh
EXPOSE 80
WORKDIR /usr/share/nginx/html
ENTRYPOINT ["./entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
