FROM node:24-alpine AS builder

WORKDIR /app

ARG NUXT_APP_BASE_URL=/sysplant/
ARG NUXT_SITE_URL=https://docs.circle-cyber.com/sysplant

ENV NUXT_APP_BASE_URL=${NUXT_APP_BASE_URL}
ENV NUXT_SITE_URL=${NUXT_SITE_URL}

COPY package.json ./
RUN npm install

COPY . .
RUN npx nuxt build

FROM node:24-alpine

WORKDIR /app

COPY --from=builder /app/.output ./.output

EXPOSE 3000

ENV PORT=3000
ENV HOST=0.0.0.0
ENV NUXT_APP_BASE_URL=/sysplant/
ENV NUXT_SITE_URL=https://docs.circle-cyber.com/sysplant

CMD ["node", ".output/server/index.mjs"]
