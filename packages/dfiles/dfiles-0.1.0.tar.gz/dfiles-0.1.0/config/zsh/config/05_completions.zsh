# ==============================================
# Shell Completions
# ==============================================
# Docker CLI completions (from current .zshrc)
fpath=(/Users/carlosferreyra/.docker/completions $fpath)

# Zsh function path
fpath+=~/.zfunc

# Initialize completions
autoload -Uz compinit
compinit

# Tool Completions
# Angular CLI (only if installed)
if command -v ng >/dev/null 2>&1; then
  source <(ng completion script)
fi

# UV completions (only if installed)
if command -v uv >/dev/null 2>&1; then
  eval "$(uv generate-shell-completion zsh)"
  eval "$(uvx --generate-shell-completion zsh)"
fi
