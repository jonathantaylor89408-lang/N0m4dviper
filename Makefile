.PHONY: all rush seal override status

all: rush

rush:
	@./rush

seal:
	@./viper_self_heal.sh --seal
	@echo "[MAKE] V1P34C0DE baseline sealed."

override:
	@./viper_self_heal.sh --override
	@echo "[MAKE] V1P34C0DE override restored."

status:
	@git status -s | grep -v "ledger/" || true
