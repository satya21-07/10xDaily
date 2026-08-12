#!/usr/bin/env bash
set -e

echo "Starting frontend build..."

# Replace the __API_URL__ placeholder with the actual RENDER_API_URL provided by Render
if [ -n "$RENDER_API_URL" ]; then
    echo "Replacing API URL in environment.prod.ts"
    # Using sed to replace the placeholder
    # RENDER_API_URL might look like 10xdaily-api.onrender.com
    # We want to use https://${RENDER_API_URL}/api/v1
    FULL_API_URL="https://${RENDER_API_URL}/api/v1"
    sed -i "s|__API_URL__|${FULL_API_URL}|g" projects/mobile-app/src/environments/environment.prod.ts
else
    echo "RENDER_API_URL is not set. Using fallback relative URL."
    sed -i "s|__API_URL__|/api/v1|g" projects/mobile-app/src/environments/environment.prod.ts
fi

# Install dependencies and build the app
npm ci
npm run build -- --configuration production

echo "Frontend build completed successfully."
