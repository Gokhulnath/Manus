FROM node:18-bullseye

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install

COPY . .

RUN rm -rf node_modules .next && npm ci && npm run build

EXPOSE 3000
CMD ["npm", "start"]
