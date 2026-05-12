#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/aop68/historial-academico-intec"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$APP_DIR/.venv"
PORT=5050

# ── Colores ──────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; exit 1; }

echo -e "\n${GREEN}══════════════════════════════════════════${NC}"
echo -e "${GREEN}   Historial Académico INTEC — Launcher   ${NC}"
echo -e "${GREEN}══════════════════════════════════════════${NC}\n"

# ── 1. Verificar Python ──────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    warn "Python3 no encontrado. Instalando con pacman..."
    sudo pacman -S --noconfirm python || error "No se pudo instalar Python3"
fi
info "Python3: $(python3 --version)"

# ── 2. Verificar pip ─────────────────────────────────────────
if ! python3 -m pip --version &>/dev/null; then
    warn "pip no encontrado. Instalando..."
    sudo pacman -S --noconfirm python-pip || error "No se pudo instalar pip"
fi

# ── 3. Entorno virtual ───────────────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    info "Creando entorno virtual..."
    python3 -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
info "Entorno virtual activado"

# ── 4. Instalar dependencias ─────────────────────────────────
info "Instalando dependencias..."
pip install --quiet --upgrade pip
pip install --quiet flask reportlab
info "Dependencias instaladas"

# ── 5. Verificar que app.py existe ───────────────────────────
if [ ! -f "$APP_DIR/app.py" ]; then
    error "No se encontró app.py en $APP_DIR\nAsegúrate de ejecutar este script dentro del repositorio."
fi

# ── 6. Liberar puerto si está ocupado ────────────────────────
if lsof -ti tcp:$PORT &>/dev/null; then
    warn "Puerto $PORT ocupado. Liberando..."
    kill "$(lsof -ti tcp:$PORT)" 2>/dev/null || true
    sleep 1
fi

# ── 7. Abrir navegador ───────────────────────────────────────
URL="http://localhost:$PORT"
(sleep 2 && xdg-open "$URL" 2>/dev/null || true) &

# ── 8. Lanzar app ────────────────────────────────────────────
echo ""
info "Iniciando servidor en ${URL}"
warn "Presiona Ctrl+C para detener\n"
cd "$APP_DIR"
python3 app.py
