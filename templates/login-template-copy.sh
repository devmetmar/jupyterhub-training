# ~/.bashrc (appended by Dockerfile)

TEMPLATE_SRC="/opt/template"
TARGET="$HOME"

if [[ -d "$TEMPLATE_SRC" ]]; then
    for file in "$TEMPLATE_SRC"/*; do
            fname=$(basename "$file")
        if [[ ! -f "$TARGET/$fname" ]]; then
            cp "$file" "$TARGET/"
        fi
    done
fi
