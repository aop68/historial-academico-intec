#!/usr/bin/env bash
set -e

REPO="https://github.com/aop68/historial-academico-intec"
BRANCH="claude/launch-app-I9Kwb"
DIR="$HOME/historial-academico-intec"
PORT=5050

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; exit 1; }

echo -e "\n${GREEN}══════════════════════════════════════════${NC}"
echo -e "${GREEN}   Historial Académico INTEC              ${NC}"
echo -e "${GREEN}══════════════════════════════════════════${NC}\n"

# ── Python ───────────────────────────────────────────────────
command -v python3 &>/dev/null || sudo pacman -S --noconfirm python || error "Instala Python3 manualmente"
info "Python: $(python3 --version)"

# ── Git ──────────────────────────────────────────────────────
command -v git &>/dev/null || sudo pacman -S --noconfirm git || error "Instala git manualmente"

# ── Clonar o actualizar repo ─────────────────────────────────
if [ -d "$DIR/.git" ]; then
    info "Actualizando repositorio..."
    git -C "$DIR" pull origin "$BRANCH" --quiet
else
    info "Descargando app..."
    git clone -b "$BRANCH" "$REPO" "$DIR" --quiet
fi

cd "$DIR"

# ── Entorno virtual ──────────────────────────────────────────
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
info "Entorno virtual listo"

# ── Dependencias ─────────────────────────────────────────────
pip install --quiet --upgrade pip
pip install --quiet flask reportlab
info "Dependencias instaladas"

# ── Liberar puerto ───────────────────────────────────────────
if command -v lsof &>/dev/null && lsof -ti tcp:$PORT &>/dev/null; then
    warn "Liberando puerto $PORT..."
    kill "$(lsof -ti tcp:$PORT)" 2>/dev/null || true
    sleep 1
fi

# ── Abrir navegador ──────────────────────────────────────────
(sleep 2 && xdg-open "http://localhost:$PORT" 2>/dev/null || true) &

# ── Lanzar ───────────────────────────────────────────────────
info "App disponible en http://localhost:$PORT"
warn "Presiona Ctrl+C para detener\n"
python3 app.py
