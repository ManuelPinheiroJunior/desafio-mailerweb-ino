FROM node:22-alpine

WORKDIR /app

COPY package.json /app/package.json
COPY tsconfig.json /app/tsconfig.json
COPY next.config.ts /app/next.config.ts
COPY next-env.d.ts /app/next-env.d.ts
COPY src /app/src

RUN npm install

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "3000"]
