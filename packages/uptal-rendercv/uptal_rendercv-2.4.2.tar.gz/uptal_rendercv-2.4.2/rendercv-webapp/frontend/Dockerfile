# Stage 1: Build the Vite application
FROM node:20-alpine AS builder

ARG VITE_API_URL=https://cv-render-api.uptal.com/api
ARG VITE_API_URL_PDF=https://cv-render-api.uptal.com

ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_API_URL_PDF=${VITE_API_URL_PDF}

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy application files
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:alpine

# Copy built assets from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]