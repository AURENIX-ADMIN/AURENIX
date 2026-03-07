FROM node:20-alpine AS builder
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy everything for building
COPY . .

# Install dependencies
RUN pnpm install --no-frozen-lockfile

# Generate Prisma Client
RUN cd packages/data-layer/prisma && echo 'DATABASE_URL="postgresql://placeholder:placeholder@localhost:5432/placeholder"' > .env && npx prisma generate --schema=schema.prisma

# Build the app using turbo
RUN npx turbo run build --filter web-portal

# Production runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production

RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Copy standalone build
COPY --from=builder /app/apps/web-portal/.next/standalone ./
COPY --from=builder /app/apps/web-portal/.next/static ./apps/web-portal/.next/static

USER nextjs
EXPOSE 3000
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# Standalone mode in monorepos puts the server.js in a nested path
CMD ["node", "apps/web-portal/server.js"]
