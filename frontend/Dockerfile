FROM node:20.11.1-alpine3.19 AS development

WORKDIR /app

COPY package.json .

RUN yarn install

COPY . .

ENV NODE_ENV=development

EXPOSE 3000

CMD ["yarn", "dev"]

FROM node:20.11.1-alpine3.19 AS build

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install

COPY . .

RUN yarn build

FROM nginx:1.25.4-alpine3.18

COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /var/www/html/

EXPOSE 80

ENTRYPOINT ["nginx", "-g", "daemon off;"]