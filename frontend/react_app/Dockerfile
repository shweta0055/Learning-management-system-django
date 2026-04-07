# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN npm install --legacy-peer-deps --no-audit --no-fund

COPY . .

ARG REACT_APP_DJANGO_API_URL=http://localhost:8000
ARG REACT_APP_FASTAPI_URL=http://localhost:8001

ENV REACT_APP_DJANGO_API_URL=$REACT_APP_DJANGO_API_URL
ENV REACT_APP_FASTAPI_URL=$REACT_APP_FASTAPI_URL
ENV CI=false
ENV GENERATE_SOURCEMAP=false

RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
