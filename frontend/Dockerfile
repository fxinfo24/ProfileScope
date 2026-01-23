# ProfileScope Frontend Dockerfile (Development)

FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 5173

# Start development server
# --host 0.0.0.0 is required for Docker networking
CMD ["npm", "run", "dev", "--", "--host"]
