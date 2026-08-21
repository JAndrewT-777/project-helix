#!/usr/bin/env bash
# Manage the Helix conda environment (create / activate / remove).
#
# Usage:
#   ./helix_env.sh create
#   source helix_env.sh activate    # must be sourced
#   ./helix_env.sh remove
#
# Place this script in the project root (next to environment.yaml) or in scripts/.

set -euo pipefail

ENV_NAME="${HELIX_ENV_NAME:-helix}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$(basename "${SCRIPT_DIR}")" == "scripts" ]]; then
  PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
else
  PROJECT_ROOT="${SCRIPT_DIR}"
fi
PROJECT_ROOT="${HELIX_ROOT:-${PROJECT_ROOT}}"
ENV_FILE="${PROJECT_ROOT}/environment.yaml"

usage() {
  cat <<EOF
Usage: $0 {create|activate|remove|status}

  create    Create the '${ENV_NAME}' conda env from environment.yaml
            and install the project in editable mode (pip install -e .)
  activate  Activate the env (run as: source $0 activate)
  remove    Delete the '${ENV_NAME}' conda env
  status    Show whether the env exists and is active

Environment variables:
  HELIX_ROOT       Project root (default: this script's dir, or parent if in scripts/)
  HELIX_ENV_NAME   Conda env name (default: helix)
EOF
}

require_conda() {
  if ! command -v conda >/dev/null 2>&1; then
    echo "Error: conda not found. Install Miniconda/Anaconda and retry." >&2
    exit 1
  fi
}

init_conda_shell() {
  local conda_base
  conda_base="$(conda info --base)"
  # shellcheck source=/dev/null
  source "${conda_base}/etc/profile.d/conda.sh"
}

env_exists() {
  conda env list | awk '{print $1}' | grep -qx "${ENV_NAME}"
}

cmd_create() {
  require_conda
  if [[ ! -f "${ENV_FILE}" ]]; then
    echo "Error: ${ENV_FILE} not found." >&2
    echo "Put environment.yaml in the project root or set HELIX_ROOT." >&2
    exit 1
  fi

  if env_exists; then
    echo "Environment '${ENV_NAME}' already exists."
    echo "Activate with:  source $0 activate"
    echo "Or remove first: $0 remove"
    exit 0
  fi

  echo "Creating conda env '${ENV_NAME}' from ${ENV_FILE} ..."
  conda env create -f "${ENV_FILE}"

  if [[ ! -f "${PROJECT_ROOT}/pyproject.toml" && ! -f "${PROJECT_ROOT}/setup.py" ]]; then
    echo
    echo "Warning: no pyproject.toml or setup.py in ${PROJECT_ROOT}."
    echo "Editable install (pip install -e .) will fail until one exists."
  fi

  echo
  echo "Done. Activate with:"
  echo "  source $0 activate"
  echo "or:"
  echo "  conda activate ${ENV_NAME}"
}

cmd_activate() {
  require_conda
  if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: activate must be sourced so it can change the current shell:" >&2
    echo "  source $0 activate" >&2
    echo "or:" >&2
    echo "  conda activate ${ENV_NAME}" >&2
    exit 1
  fi

  if ! env_exists; then
    echo "Error: environment '${ENV_NAME}' does not exist. Run: $0 create" >&2
    return 1
  fi

  init_conda_shell
  conda activate "${ENV_NAME}"
  echo "Activated '${ENV_NAME}' (Python $(python --version 2>&1))"
}

cmd_remove() {
  require_conda
  if ! env_exists; then
    echo "Environment '${ENV_NAME}' does not exist. Nothing to remove."
    exit 0
  fi

  if [[ "${CONDA_DEFAULT_ENV:-}" == "${ENV_NAME}" ]]; then
    echo "Deactivate the env first:  conda deactivate"
    exit 1
  fi

  echo "Removing conda env '${ENV_NAME}' ..."
  conda env remove -n "${ENV_NAME}" -y
  echo "Removed '${ENV_NAME}'."
}

cmd_status() {
  require_conda
  if env_exists; then
    echo "Environment '${ENV_NAME}': exists"
  else
    echo "Environment '${ENV_NAME}': not created"
  fi
  echo "Active env: ${CONDA_DEFAULT_ENV:-none}"
  echo "Project root: ${PROJECT_ROOT}"
  echo "Env file: ${ENV_FILE} $([[ -f ${ENV_FILE} ]] && echo '[found]' || echo '[missing]')"
}

if [[ $# -eq 0 ]]; then
  usage >&2
  exit 1
fi

case "$1" in
  create)   cmd_create ;;
  activate) cmd_activate ;;
  remove)   cmd_remove ;;
  status)   cmd_status ;;
  -h|--help|help) usage; exit 0 ;;
  *) echo "Unknown command: $1" >&2; usage >&2; exit 1 ;;
esac