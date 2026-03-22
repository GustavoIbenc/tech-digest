#!/bin/bash
set -e

echo "🚀 Deploying Tech Digest PWA to GitHub Pages..."

# Git setup (token via env or inline in remote)
export GIT_ASKPASS=/bin/echo
git init -q 2>/dev/null || true
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/GustavoIbenc/tech-digest.git

# Commit & push
git add -A
if ! git diff --cached --quiet; then
    git commit -m "Deploy: $(date +'%Y-%m-%d')"
    git branch -M main 2>/dev/null || true
fi

# Push with token
git push -u origin main --force 2>&1 | grep -v "Authorization" || true

echo ""
echo "✅ Deployed!"
echo "📱 Live at: https://gustavoibenc.github.io/tech-digest/"
