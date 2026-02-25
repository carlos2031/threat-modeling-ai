#!/usr/bin/env sh

set -eu

cli_help() {
  cli_name="${0##*/}"
  echo "
$cli_name — Threat Modeling AI (threat-frontend)
Usage: $cli_name [command]

Commands:
  runserver   Serve static with nginx (default)
  health      Check health (curl :80)
  *           This help
"
  exit 1
}

case "${1:-runserver}" in
  runserver)
    exec nginx -g "daemon off;"
    ;;
  health)
    curl -sf "http://localhost:80/" || exit 1
    exit 0
    ;;
  *)
    cli_help
    ;;
esac
