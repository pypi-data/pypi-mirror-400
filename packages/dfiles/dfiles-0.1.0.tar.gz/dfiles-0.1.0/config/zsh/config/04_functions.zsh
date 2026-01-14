# ==============================================
# Utility Functions
# ==============================================
# Directory Navigation with List
function cdd() {
    builtin cd "$@" && ls
}

# Network Functions
alias localip='ipconfig getifaddr en0'
alias whatport='netstat -vanp tcp | grep'
alias ip='ifconfig | grep "inet "'

# Exit Shortcuts
alias q='exit'
alias qq='clsall && exit'

# Update All Function
function uall() {
    echo "🔄 Updating all package managers..."

    update

    echo "\n🧹 Cleaning up..."

    cleanup

    echo "\n✅ All updates and cleanup complete!"
}

# OPTIONS
function showopts() {
    echo "Current Zsh Options:"
    for opt in $(setopt | awk '{print $1}'); do
        echo "- $opt"
    done
}

# ==============================================
# Command Help
function helpdev() {
    echo "Zsh Commands:"
    echo "  - cdd: Change directory and list contents"
    echo "  - up: Go up one directory"
    echo "  - dev: Go to Development directory"
    echo "  - proj: Go to Projects directory"
    echo "  - docs: Go to Documents directory"
    echo "  - downloads: Go to Downloads directory"
    echo "  - desktop: Go to Desktop directory"
    echo "  - home: Go to Home directory"
    echo "  - cls: Clear terminal"
    echo "  - clsall: Clear terminal and history"
    echo "  - q: Exit shell"
    echo "  - qq: Clear and exit shell"
    echo "  - reset: Reset terminal"
    echo "  - refresh: Refresh zsh configuration"
    echo "  - showopts: Show current zsh options"
    echo "  - uall: Update all package managers (brew, uv, cargo, npm)"
}
