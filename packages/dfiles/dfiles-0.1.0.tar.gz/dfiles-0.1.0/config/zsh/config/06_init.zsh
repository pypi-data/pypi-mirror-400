# ==============================================
# Shell Initialization (runs last)
# ==============================================
# Starship prompt (only if installed)
if command -v starship >/dev/null 2>&1; then
  eval "$(starship init zsh)"
fi

if command -v rustup >/dev/null 2>&1; then
  source "$HOME/.cargo/env"
fi

[[ "$TERM_PROGRAM" == "vscode" ]] && . "$(code --locate-shell-integration-path zsh)"