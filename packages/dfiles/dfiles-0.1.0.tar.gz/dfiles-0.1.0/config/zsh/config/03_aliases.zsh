# ==============================================
# Development Tools and Aliases
# ==============================================
# Python Version Aliases
alias python="python3.10"  # default global python
alias py="python3.10"
alias py10="python3.10"
alias py11="python3.11"
alias py12="python3.12"

# Python related Aliases
alias pyhelp="python3.10 -m pydoc"
alias pyrun="python3.10 -m runpy"
alias pyserve="python3.10 -m http.server"

# UV Package Management
alias uvrun='uv run'
alias uvpip='uv pip'
alias uvadd='uv add'
alias uvs='uv sync'
alias uvsu='uvs --upgrade'
alias uvsa='uvs --all-extras'
alias uvup='uv self update'

# UV Virtual Environment
alias venv='uv venv'
alias venva='source .venv/bin/activate'
alias venvr='rm -rf .venv'
alias venvd='deactivate'

# UV Tools and Development
alias uvt='uv tool'
alias uvtadd='uvt install'
alias uvtrm='uvt uninstall'
alias uvtup='uvt upgrade --all'
alias uvtls='uvt list'
alias uvtr='uvt run'
alias uvdev='uv pip install -e ."[dev]"'
alias uvreq='uv pip freeze > requirements.txt'

# ==============================================
# Git Commands
# ==============================================
# Basic Git Operations
alias gitp='git pull'
alias gitc='git checkout'
alias gitm='git merge'
alias gitl='git log --oneline --graph --decorate'
alias gits='git status'
alias gitb='git branch'
alias gitr='git remote -v'
alias gitf='git fetch --all --prune'
alias gitpf='git push --force-with-lease'

# ==============================================
# Docker Commands
# ==============================================
alias dps='docker ps'
alias dimgs='docker images'
alias dimg='docker image'
alias dstart='docker start $(docker ps -aq)'
alias dstop='docker stop $(docker ps -aq)'
alias drmc='docker rm $(docker ps -aq)'
alias drmi='docker rmi $(docker images -q)'
alias dclean='docker system prune -a --volumes'
alias dvol='docker volume ls'
alias dvolrm='docker volume rm $(docker volume ls -q)'
alias dnet='docker network ls'
alias dnetrm='docker network rm $(docker network ls -q)'

# ==============================================
# System and File Operations
# ==============================================
# Directory Navigation
alias up='cd ..'
alias ..='up'
alias dev='cd ~/Development'
alias proj='cd ~/Projects'
alias docs='cd ~/Documents'
alias downloads='cd ~/Downloads'
alias desktop='cd ~/Desktop'
alias home='cd ~'

# File Operations
alias lsa='ls -a'
alias lsl='ls -1'
alias lsla='ls -1a'
alias lsf='ls -laF'
alias lsd='ls -d */'
alias show='cat'
alias showf='cat -n'
alias size='du -sh'

# System Commands
alias cls='clear'
alias clsall='clear && history -p'
alias reset='exec zsh'
alias refresh='source ~/.zshrc'
alias refreshall='source ~/.zshrc && source ~/.bash_profile && source ~/.bashrc'

# Process Management
alias ports='lsof -i -P -n | grep LISTEN'
alias killport='kill -9 $(lsof -ti:'$1')'
alias ps='ps aux | grep'
alias cpu='top -o cpu'
alias mem='top -o rsize'

# ==============================================
# Package Management
# ==============================================
# Homebrew
alias bup='brew update && brew upgrade'
alias bcl='brew cleanup && brew autoremove && brew doctor'
alias binfo='brew info'
alias bfind='brew search'
alias badd='brew install'
alias baddc='brew install --cask'
alias brm='brew uninstall'
alias brmc='brew uninstall --cask'
alias bls='brew list'
alias bdeps='brew deps'

# System Updates
alias update='bup && uvup && uvtup && npm update -g && bun upgrade && cargo install-update -a'
alias cleanup='bcl && npm -g cache clean --force && cargo cache -a'

# ==============================================
# Application Quick Launchers
# ==============================================
alias vsc='code -r'
alias vscode='vsc .'
alias vsci='code-insiders -r'
alias vscodei='vsci .'
alias finder='open -a Finder'
alias openapp='open -a'
alias dockerapp='open -a Docker'
alias wpp='open -a "WhatsApp"'
alias chrome='open -a "Google Chrome"'
alias safari='open -a "Safari"'
alias iterm='open -a "iTerm"'
alias terminal='open -a "Terminal"'
alias slack='open -a "Slack"'
alias obsidian='open -a "Obsidian"'

# Editor Configuration
alias zshrci='code-insiders -r -d ~/.zshrc'
alias zshrc='code -r -d ~/.zshrc'
alias bashrc='code -r -d ~/.bashrc'

# ==============================================
# Automation and Quick Actions
# ==============================================
# Quick Directory Size Analysis
alias biggest='du -sh * | sort -hr | head -10'  # Show 10 largest files/folders in current directory
alias space='df -h'  # Show disk space usage

# Quick File Operations
alias latest='ls -t | head -5'  # Show 5 most recently modified files
alias backup='cp -r "$1" "$1.backup"'  # Quick file/folder backup
alias extract='tar -xvf'  # Quick extract tar files
alias compress='tar -czvf'  # Quick compress to tar.gz
alias zip='zip -r'  # Quick zip files
alias zippass='zip -e'  # Quick zip with password

# Quick Development Setup
alias gitinit='git init && git add . && git commit -m "Initial commit"'  # Initialize git repo
alias npmstart='npm install && npm run start'  # Quick npm project setup
alias bunstart='bun install && bun run start'  # Quick bun project setup

# Quick System Operations
alias cleands='find . -type f -name ".DS_Store" -delete'  # Remove .DS_Store files
alias flushdns='sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder'  # Flush DNS cache

# Quick File Search and Replace
alias findtext='find . -type f -exec grep -l "$1" {} \;'  # Find files containing text
alias replaceinfile='find . -type f -exec sed -i "" "s/$1/$2/g" {} \;'  # Replace text in files

# Quick Network Tools
alias ports='sudo lsof -iTCP -sTCP:LISTEN -P'  # Show all listening ports
alias publicip='curl -4 icanhazip.com'  # Show public IP address

# Quick System Info
alias sysinfo='system_profiler SPHardwareDataType SPSoftwareDataType'  # Show system info

# Auto CD Toggle
alias ccd='autocd-toggle'

# Quick Server
alias pyhttp='python3 -m http.server'
alias servethis='python3 -m http.server 8000'

# Miscellaneous
alias here='pwd | pbcopy'
alias ff='find . -name'
alias gg='grep -r'
alias hh='tldr'

# Terminal Management
alias qshell='if [ "$TERM_PROGRAM" = "Apple_Terminal" ]; then killall Terminal; else exit 0; fi;'
alias quit='qshell'
alias q='qshell'
