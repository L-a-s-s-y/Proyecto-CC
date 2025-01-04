FROM node:lts-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
#COPY *js ./
RUN npm install
COPY . .
RUN npm run build
#EXPOSE 8080
#CMD ["http-server", "dist"]
#CMD ["npm", "run", "serve"]
#CMD ["npm", "run", "build"]
FROM nginx:stable-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
#COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]