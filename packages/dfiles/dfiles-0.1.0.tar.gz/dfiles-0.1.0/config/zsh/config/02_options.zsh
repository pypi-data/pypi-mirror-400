# ==============================================
# Shell Options and Settings
# ==============================================
# Completion Settings
zstyle ':completion:*' menu select

# Auto CD Toggle Function
autocd-toggle() {
    if [[ -o auto_cd ]]; then
        unsetopt auto_cd
        echo "auto_cd disabled"
    else
        setopt auto_cd
        echo "auto_cd enabled"
    fi
}
