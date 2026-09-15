#!/usr/bin/env bash
# Rebuild the project page and publish it to https://rho-anon.github.io
# Edit content first:  source/app/src/content/article.mdx
set -euo pipefail
cd "$(dirname "$0")"

echo "==> building"
( cd source/app && SITE_URL="https://rho-anon.github.io" npm run build )

echo "==> refreshing the served site at the repo root"
find . -maxdepth 1 ! -name . ! -name .git ! -name source ! -name .gitignore \
       ! -name .nojekyll ! -name publish.sh ! -name README.md -exec rm -rf {} + 2>/dev/null || true
cp -R source/app/dist/. .
find . -name "*.gz" -delete 2>/dev/null || true
touch .nojekyll

echo "==> anonymity check"
LEAKS=$(grep -rliE 'karim|elmaaroufi|berkeley|k\.e@|svegliato|seshia|rho-robotics' . 2>/dev/null \
        | grep -vE '(^|/)\.git/' | grep -vE '(^|/)node_modules/' \
        | grep -vE '(^|/)(publish\.sh|README\.md)$' | head -5 || true)
if [ -n "$LEAKS" ]; then
  echo "!! ABORTING — identity strings found in:"; echo "$LEAKS"; exit 1
fi
echo "   clean"

echo "==> committing as an anonymous author"
git add -A
if git diff --cached --quiet; then echo "   nothing to commit"; else
  git -c user.name="RHO Authors" -c user.email="anonymous@users.noreply.github.com" \
      commit -q -m "${1:-Update project page}"
fi
git push -q origin main
echo "==> done. https://rho-anon.github.io (Pages takes ~1 min)"
