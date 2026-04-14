#!/usr/bin/env bash
# start.sh — Notion File Formatter 서비스 시작

set -euo pipefail

# ── 색상 ──────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "${GREEN}[✓]${NC} $*"; }
fail() { echo -e "${RED}[✗]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
info() { echo -e "${BLUE}[i]${NC} $*"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── 사전 조건 확인 ────────────────────────────────────────────────────────────
if [ ! -f docker-compose.yml ]; then
    fail "docker-compose.yml을 찾을 수 없습니다. 프로젝트 루트에서 실행하세요."
    exit 1
fi

if [ ! -d storage/uploads ] || [ ! -d storage/outputs ]; then
    warn "storage 디렉토리가 없습니다. setup.sh를 먼저 실행합니다..."
    bash "${SCRIPT_DIR}/setup.sh"
fi

if ! docker info &>/dev/null 2>&1; then
    fail "Docker 데몬이 실행되지 않고 있습니다."
    exit 1
fi

# ── 시작 ──────────────────────────────────────────────────────────────────────
echo -e "${BOLD}"
echo "╔══════════════════════════════════════╗"
echo "║   Notion File Formatter — Start      ║"
echo "╚══════════════════════════════════════╝"
echo -e "${NC}"

# 이미 실행 중인 컨테이너 확인
RUNNING=$(docker compose ps --status running --format "{{.Name}}" 2>/dev/null | wc -l)
if [ "$RUNNING" -gt 0 ]; then
    warn "이미 실행 중인 컨테이너가 있습니다. 재시작합니다..."
    docker compose down --remove-orphans
fi

info "컨테이너 빌드 및 시작 중..."
docker compose up --build -d

# ── 헬스체크 ─────────────────────────────────────────────────────────────────
API_URL="http://localhost:8000"
MAX_WAIT=60   # 최대 대기 시간 (초)
INTERVAL=2
elapsed=0

echo ""
info "API 서버 응답 대기 중..."

while [ "$elapsed" -lt "$MAX_WAIT" ]; do
    if command -v curl &>/dev/null; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/api/status/healthcheck" 2>/dev/null || echo "000")
        # PENDING(200) 또는 status 엔드포인트가 응답하면 정상
        if [ "$HTTP_CODE" = "200" ]; then
            break
        fi
    else
        # curl 없으면 컨테이너 상태만 확인
        RUNNING_NOW=$(docker compose ps --status running --format "{{.Name}}" 2>/dev/null | wc -l)
        if [ "$RUNNING_NOW" -ge 3 ]; then
            break
        fi
    fi

    printf "."
    sleep "$INTERVAL"
    elapsed=$((elapsed + INTERVAL))
done

echo ""

if [ "$elapsed" -ge "$MAX_WAIT" ]; then
    warn "헬스체크 타임아웃 (${MAX_WAIT}초). 컨테이너 로그를 확인하세요:"
    warn "  docker compose logs api"
else
    ok "API 서버 정상 응답"
fi

# ── 컨테이너 상태 출력 ────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}── 컨테이너 상태 ──${NC}"
docker compose ps

# ── 완료 메시지 ───────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}서비스가 시작되었습니다.${NC}"
echo -e "  브라우저:  ${BLUE}${BOLD}${API_URL}${NC}"
echo ""
info "로그 확인:    docker compose logs -f"
info "서비스 종료:  docker compose down"
