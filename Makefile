test:
	PYTHONPATH=. pytest tests/ -v

cov:
	PYTHONPATH=. pytest --cov=app --cov-report=html tests/

report:
	firefox htmlcov/index.html

ci: cov report
	@echo "✅ Тесты GREEN! Отчёт готов!"
