#!/usr/bin/env bash
set -e

echo "Starting frontend build..."

# Replace the __API_URL__ placeholder with the actual PUBLIC_API_URL provided by Render
if [ -n "$PUBLIC_API_URL" ]; then
    echo "Replacing API URL in environment.prod.ts with $PUBLIC_API_URL"
    sed -i "s|__API_URL__|${PUBLIC_API_URL}|g" projects/mobile-app/src/environments/environment.prod.ts
else
    echo "PUBLIC_API_URL is not set. Using fallback relative URL."
    sed -i "s|__API_URL__|/api/v1|g" projects/mobile-app/src/environments/environment.prod.ts
fi

# Install dependencies and build the app
npm ci
npx ng build mobile-app --configuration production

echo "Frontend build completed successfully."
