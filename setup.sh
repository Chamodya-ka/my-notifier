#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ALIAS_DEF="alias my_notifier=\"python '$SCRIPT_DIR/main.py'\""

add_alias() {
    local rc_file="$1"
    if grep -qF "alias my_notifier=" "$rc_file" 2>/dev/null; then
        echo "Alias already present in $rc_file — skipping."
    else
        printf '\n# my-notifier\n%s\n' "$ALIAS_DEF" >> "$rc_file"
        echo "Alias added to $rc_file"
    fi
}

if [ -n "$ZSH_VERSION" ] || [ "$(basename "$SHELL")" = "zsh" ]; then
    add_alias "$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ] || [ "$(basename "$SHELL")" = "bash" ]; then
    if [ -f "$HOME/.bash_profile" ]; then
        add_alias "$HOME/.bash_profile"
    else
        add_alias "$HOME/.bashrc"
    fi
else
    echo "Unsupported shell: $SHELL"
    echo "Add this line manually to your shell rc file:"
    echo "  $ALIAS_DEF"
    exit 1
fi

echo ""
echo "Done. Restart your terminal or run:  source ~/.zshrc  (or your rc file)"
