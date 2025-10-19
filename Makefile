PYTHON = python3
SCRIPT = admin.py

help:
	@echo "Доступные команды:"
	@echo "  make admin - Создать администратора"

admin:
	@echo "=== Создание администратора ==="
	@$(PYTHON) $(SCRIPT)



