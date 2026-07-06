# Next.js development image. For production use a multi-stage build with
# `next build` + `next start`; this image targets the docker-compose dev flow.
FROM node:20-alpine

WORKDIR /app

# Install dependencies first for better layer caching.
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the app (overridden by the bind mount in docker-compose dev).
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
