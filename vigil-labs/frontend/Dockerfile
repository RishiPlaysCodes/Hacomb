# VIGIL LABS - Frontend Dockerfile
# Multi-stage build: Node.js build → Nginx serve

# ─── Build Stage ──────────────────────────────────────────────────────────────
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* yarn.lock* ./

# Install dependencies
RUN npm ci --production=false

# Copy source
COPY . .

# Build for production
ENV VITE_API_URL=/api
RUN npm run build

# ─── Production Stage ─────────────────────────────────────────────────────────
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Security headers via nginx (see nginx.conf)
# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
