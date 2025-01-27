_GREEN := "\033[32m[%s]\033[0m %s\n" # Green text for "printf"
_RED := "\033[31m[%s]\033[0m %s\n" # Red text for "printf"
.SILENT:
.PHONY: all

# So in short:
# $  -> makefile variable => use a single dollar sign
# $$ -> shell variable => use two dollar signs


dummy:
	echo Do not run without arguments! $(_R)

exe1:
	pyinstaller --onefile --windowed --add-data="assets/asset_tk:assets/asset_tk" --add-data="settings.ini:." --add-data="settings.local.ini:." --hidden-import "tkinter" mine_tk.py

# дома - 40.2s

exe:
	@echo "Время выполнения команды:"
	@powershell -Command "Measure-Command { \
        pyinstaller \
        --onefile \
        --windowed \
        --add-data="assets/asset_tk:assets/asset_tk" \
        --add-data="settings.ini:." \
        --add-data="settings.local.ini:." \
        --hidden-import "tkinter" \
        mine_tk.py \
    } | Select-Object -ExpandProperty TotalSeconds"

test:
	pytest

coverage:
	pytest --cov=. --cov-report=html tests/; rm -f .coverage
	"C:\Program Files\Google\Chrome\Application\chrome" "file://C:/Users/swasher/GitHub/minesweeper/htmlcov/index.html"

