#!/usr/bin/env bash
# setup.sh — Notion File Formatter 초기 환경 구성 및 의존성 검증

set -euo pipefail

# ── 색상 ──────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "${GREEN}[✓]${NC} $*"; }
fail() { echo -e "${RED}[✗]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
info() { echo -e "${BLUE}[i]${NC} $*"; }
hdr()  { echo -e "\n${BOLD}── $* ──${NC}"; }

ERRORS=0
err() { fail "$*"; ERRORS=$((ERRORS + 1)); }

# ── 프로젝트 루트 고정 ────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BOLD}"
echo "╔══════════════════════════════════════╗"
echo "║   Notion File Formatter — Setup      ║"
echo "╚══════════════════════════════════════╝"
echo -e "${NC}"

# ══════════════════════════════════════════════════════════════════════════════
hdr "1. 필수 의존성 확인"
# ══════════════════════════════════════════════════════════════════════════════

# Docker
if command -v docker &>/dev/null; then
    DOCKER_VER=$(docker --version 2>&1)
    ok "Docker:          $DOCKER_VER"

    # Docker 데몬 실행 여부
    if docker info &>/dev/null 2>&1; then
        ok "Docker 데몬:     실행 중"
    else
        err "Docker 데몬이 실행되지 않고 있습니다. Docker Desktop 또는 dockerd를 시작하세요."
    fi
else
    err "Docker가 설치되지 않았습니다. https://docs.docker.com/get-docker/ 에서 설치하세요."
fi

# docker compose v2 (플러그인 방식)
if docker compose version &>/dev/null 2>&1; then
    COMPOSE_VER=$(docker compose version 2>&1)
    ok "docker compose:  $COMPOSE_VER"
else
    err "docker compose (v2 플러그인)이 없습니다."
    info "  Docker Desktop 최신 버전을 설치하거나, 다음 명령으로 플러그인을 추가하세요:"
    info "  sudo apt-get install docker-compose-plugin  # Ubuntu/Debian"
fi

# curl (헬스체크용)
if command -v curl &>/dev/null; then
    ok "curl:            $(curl --version | head -1)"
else
    warn "curl이 없습니다. start.sh의 헬스체크가 동작하지 않습니다."
fi

# ══════════════════════════════════════════════════════════════════════════════
hdr "2. 스토리지 디렉토리 생성"
# ══════════════════════════════════════════════════════════════════════════════

mkdir -p storage/uploads storage/outputs
ok "storage/uploads, storage/outputs 생성 완료"

# ══════════════════════════════════════════════════════════════════════════════
hdr "3. .env 파일 생성"
# ══════════════════════════════════════════════════════════════════════════════

if [ ! -f .env ]; then
    cat > .env << 'EOF'
# Redis 연결 (docker-compose 기본값)
REDIS_URL=redis://redis:6379/0

# Notion 업로드 제한 (5MB)
TARGET_SIZE_BYTES=5242880

# 업로드 최대 허용 크기 (2GB)
MAX_UPLOAD_BYTES=2147483648

# 임시 파일 만료 시간 (초, 기본 1시간)
JOB_EXPIRE_SECONDS=3600
EOF
    ok ".env 파일 생성 완료"
else
    warn ".env 파일이 이미 존재합니다. 건너뜁니다."
fi

# ══════════════════════════════════════════════════════════════════════════════
hdr "4. Shell alias 등록"
# ══════════════════════════════════════════════════════════════════════════════

# 현재 셸 및 RC 파일 감지
detect_rc() {
    local shell_name
    shell_name="$(basename "${SHELL:-}")"

    case "$shell_name" in
        zsh)  echo "$HOME/.zshrc" ;;
        bash) echo "$HOME/.bashrc" ;;
        *)
            # 프로세스 이름으로 재시도
            local proc
            proc="$(ps -p $$ -o comm= 2>/dev/null | tr -d '-')"
            case "$proc" in
                zsh)  echo "$HOME/.zshrc" ;;
                bash) echo "$HOME/.bashrc" ;;
                *)    echo "" ;;
            esac
            ;;
    esac
}

SHELL_RC="$(detect_rc)"

# 등록할 alias 목록
declare -A ALIASES=(
    ["notion-start"]="${SCRIPT_DIR}/start.sh"
    ["notion-stop"]="docker compose -f ${SCRIPT_DIR}/docker-compose.yml down"
    ["notion-logs"]="docker compose -f ${SCRIPT_DIR}/docker-compose.yml logs -f"
    ["notion-ps"]="docker compose -f ${SCRIPT_DIR}/docker-compose.yml ps"
)

register_alias() {
    local name="$1"
    local cmd="$2"
    local alias_line="alias ${name}='${cmd}'"

    if [ -z "$SHELL_RC" ]; then
        warn "RC 파일 감지 실패 — 수동 추가: $alias_line"
        return
    fi

    # 이미 alias 블록이 있는지 확인 (이름 기준)
    if grep -q "alias ${name}=" "$SHELL_RC" 2>/dev/null; then
        warn "alias '${name}'가 이미 ${SHELL_RC}에 존재합니다. 건너뜁니다."
    else
        echo "$alias_line" >> "$SHELL_RC"
        ok "alias '${name}' → ${SHELL_RC} 추가 완료"
    fi
}

# 헤더 블록 삽입 (최초 1회)
if [ -n "$SHELL_RC" ] && ! grep -q "# Notion File Formatter" "$SHELL_RC" 2>/dev/null; then
    {
        echo ""
        echo "# Notion File Formatter ($(date '+%Y-%m-%d'))"
    } >> "$SHELL_RC"
fi

for alias_name in "${!ALIASES[@]}"; do
    register_alias "$alias_name" "${ALIASES[$alias_name]}"
done

if [ -n "$SHELL_RC" ]; then
    info "alias를 즉시 적용하려면 다음을 실행하세요:"
    info "  source ${SHELL_RC}"
fi

# ══════════════════════════════════════════════════════════════════════════════
hdr "5. 실행 권한 부여"
# ══════════════════════════════════════════════════════════════════════════════

chmod +x "${SCRIPT_DIR}/start.sh"
ok "start.sh 실행 권한 부여 완료"

# ══════════════════════════════════════════════════════════════════════════════
echo ""
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}${BOLD}모든 검사를 통과했습니다.${NC}"
    info "서비스를 시작하려면: ./start.sh"
    info "또는 alias 적용 후:  notion-start"
else
    echo -e "${RED}${BOLD}오류 ${ERRORS}개를 해결한 후 다시 실행하세요.${NC}"
    exit 1
fi
