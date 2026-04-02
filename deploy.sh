#!/bin/bash
# boss-checklist index.html 자동 배포
# Claude Code PostToolUse 훅에서 호출됨

REPO="/Users/salgi/boss-checklist"
FILE="$REPO/index.html"

# 변경 없으면 조용히 종료
cd "$REPO"
if git diff --quiet index.html; then
  exit 0
fi

git add index.html

TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
git commit -m "auto-deploy: $TIMESTAMP"

if git push origin main; then
  echo "✅ boss-checklist 배포 완료 ($TIMESTAMP)"
else
  echo "❌ push 실패 — 수동으로 확인 필요"
  exit 1
fi
