# threat-frontend — multi-stage: build (Node), runtime (nginx)
# Build from repo root: docker build -f threat-frontend/Dockerfile .
# Compose: context: .  dockerfile: threat-frontend/Dockerfile

# -----------------------------------------------------------------------------
# Stage: build — Vite/React build
# -----------------------------------------------------------------------------
FROM node:20-slim AS build

WORKDIR /app

# Base path e prefixo da API para deploy sob /threat-modeling-ai/ (ex.: portfolio VPS)
ARG VITE_BASE_PATH=/
ARG VITE_API_PREFIX=/api/v1
ENV VITE_BASE_PATH=$VITE_BASE_PATH
ENV VITE_API_PREFIX=$VITE_API_PREFIX

COPY threat-frontend/package*.json ./
RUN npm ci

COPY threat-frontend/ .
RUN npm run build

# -----------------------------------------------------------------------------
# Stage: runtime — nginx + static
# -----------------------------------------------------------------------------
FROM nginx:alpine AS runtime

RUN apk add --no-cache curl

COPY --from=build /app/dist /usr/share/nginx/html
COPY threat-frontend/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY threat-frontend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

LABEL org.opencontainers.image.title="threat-frontend" \
      org.opencontainers.image.description="Threat Modeling AI static frontend" \
      org.opencontainers.image.vendor="Threat Modeling AI"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["runserver"]
