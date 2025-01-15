TTTT_GREEN := "\033[32m[%s]\033[0m %s\n" # Green text for "printf"
_RED := "\033[31m[%s]\033[0m %s\n" # Red text for "printf"
.SILENT:
.PHONY: all

# So in short:
# $  -> makefile variable => use a single dollar sign
# $$ -> shell variable => use two dollar signs


dummy:
	echo Do not run without arguments! $(_R)

exe:
	pyinstaller --onefile --windowed --add-data="asset:asset" --add-data="settings.ini:." --add-data="settings.local.ini:." --hidden-import "tkinter" mine_tk.py

test:
	pytest

coverage:
	pytest --cov=. --cov-report=html tests/; rm -f .coverage
	"C:\Program Files\Google\Chrome\Application\chrome" "file://C:/Users/swasher/GitHub/minesweeper/htmlcov/index.html"