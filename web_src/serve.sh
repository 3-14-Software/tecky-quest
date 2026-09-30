#!/usr/bin/env bash
# Sert Tecky Quest sur le réseau local pour y jouer depuis un téléphone.
#   ./serve.sh          (port 8080)
#   ./serve.sh 9000     (autre port)
set -euo pipefail
cd "$(dirname "$0")"
PORT="${1:-8080}"
IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
URL="http://${IP:-localhost}:${PORT}/"

# Fedora : firewalld bloque les ports entrants par défaut
if command -v firewall-cmd >/dev/null 2>&1; then
  if ! firewall-cmd --query-port="${PORT}/tcp" >/dev/null 2>&1; then
    echo "Ouverture du port ${PORT} dans le pare-feu (jusqu'au prochain redémarrage)…"
    sudo firewall-cmd --add-port="${PORT}/tcp" || echo "  -> impossible : lance à la main  sudo firewall-cmd --add-port=${PORT}/tcp"
  fi
fi

echo
echo "  Tecky Quest est servi sur :  ${URL}"
echo "  Ouvre cette adresse sur le téléphone (même Wi-Fi que ce PC)."
if command -v qrencode >/dev/null 2>&1; then
  qrencode -t ansiutf8 "${URL}"
else
  echo "  (astuce : sudo dnf install qrencode  pour afficher un QR code à scanner)"
fi
echo "  Ctrl+C pour arrêter."
echo
exec python3 -m http.server "${PORT}" --bind 0.0.0.0
