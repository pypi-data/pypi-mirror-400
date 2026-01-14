# ==============================================
# Carlos Ferreyra's ZSH Configuration
# Modular setup - loads configuration from ~/.zsh/
#
# Sourced files:
# - file:///Users/carlosferreyra/.zsh/00_environment.zsh
# - file:///Users/carlosferreyra/.zsh/01_plugins.zsh
# - file:///Users/carlosferreyra/.zsh/02_options.zsh
# - file:///Users/carlosferreyra/.zsh/03_aliases.zsh
# - file:///Users/carlosferreyra/.zsh/04_functions.zsh
# - file:///Users/carlosferreyra/.zsh/05_completions.zsh
# - file:///Users/carlosferreyra/.zsh/06_init.zsh
# ==============================================

# Source all .zsh files from the ~/.zsh directory in numerical order
if [ -d ~/.zsh ]; then
  for file in ~/.zsh/*.zsh; do
    source "$file"
  done
  unset file
fi

# bun completions
[ -s "/Users/carlosferreyra/.bun/_bun" ] && source "/Users/carlosferreyra/.bun/_bun"
