exe:
	uv sync --extra service --extra publish
	uv run build_watchdog.py

test_exe:
	./dist/aind_watchdog_service.exe -v


pypi-release:
	uv build