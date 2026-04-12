FROM node:24-alpine AS base

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app

COPY package.json ./
RUN pnpm install --frozen-lockfile --ignore-scripts

COPY . .

ARG NUXT_APP_BASE_URL=/sysplant/
ARG NUXT_SITE_URL=https://docs.circle-cyber.com/sysplant

RUN NUXT_APP_BASE_URL=${NUXT_APP_BASE_URL} \
    NUXT_SITE_URL=${NUXT_SITE_URL} \
    pnpm run generate

FROM node:24-alpine AS release

WORKDIR /app

COPY --from=base /app/.output ./.output

EXPOSE 3000

ENV PORT=3000
ENV HOST=0.0.0.0
ENV NUXT_APP_BASE_URL=/sysplant/
ENV NUXT_SITE_URL=https://docs.circle-cyber.com/sysplant

CMD ["node", ".output/server/index.mjs"]
