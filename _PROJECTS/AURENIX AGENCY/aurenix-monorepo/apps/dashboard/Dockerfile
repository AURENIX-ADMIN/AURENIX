FROM node:20-alpine AS builder
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy everything for building
COPY . .

# Install dependencies
RUN pnpm install --no-frozen-lockfile

# Build the app using turbo
RUN npx turbo run build --filter aurenix-dashboard

# Production runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production

RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Copy standalone build
COPY --from=builder /app/apps/dashboard/.next/standalone ./
COPY --from=builder /app/apps/dashboard/.next/static ./apps/dashboard/.next/static

USER nextjs
EXPOSE 3001
ENV PORT 3001
ENV HOSTNAME "0.0.0.0"

# Standalone mode in monorepos puts the server.js in a nested path
CMD ["node", "apps/dashboard/server.js"]
