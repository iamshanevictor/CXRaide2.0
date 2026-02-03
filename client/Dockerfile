FROM node:20-alpine as base

WORKDIR /app

# Copy package files for dependency installation
COPY package*.json ./

# Install dependencies
RUN npm install

# Development stage with hot-reloading
FROM base as development
# Set development environment
ENV NODE_ENV=development
# Expose development server port
EXPOSE 8080
# Start Vite dev server; ensure deps present when using bind mounts
CMD ["sh", "-c", "npm install && npm run dev -- --host --port 8080"]

# Build stage for production
FROM base as build-stage
# Copy all project files
COPY . .
# Build app for production
RUN npm run build

# Production stage
FROM nginx:stable-alpine as production-stage
# Copy built files from build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Expose port 80
EXPOSE 80
# Start nginx
CMD ["nginx", "-g", "daemon off;"] 