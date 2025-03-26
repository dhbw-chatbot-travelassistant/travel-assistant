# Colors
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
NC     := \033[0m

.PHONY: init check_python create_venv install_precommit

init: check_python create_venv install_precommit

check_python:
	@printf "${YELLOW}Checking Python3 installation...${NC}\n"
	@if command -v python3 >/dev/null 2>&1; then \
		printf "${GREEN}✓ Python3 is installed${NC}\n"; \
	else \
		printf "${RED}✗ Python3 not found. Please install Python3 and try again.${NC}\n"; \
		exit 1; \
	fi

create_venv:
	@if [ -d ".venv" ]; then \
		printf "${YELLOW}Virtual environment exists. Skipping creation.${NC}\n"; \
	else \
		printf "${YELLOW}Creating virtual environment...${NC}\n"; \
		python3 -m venv .venv && printf "${GREEN}✓ Virtual environment created${NC}\n" || { printf "${RED}✗ Failed to create venv. Install python3-venv and try again.${NC}\n"; exit 1; }; \
	fi

install_precommit:
	@printf "${YELLOW}Installing pre-commit...${NC}\n"
	@.venv/bin/pip install pre-commit >/dev/null 2>&1 && printf "${GREEN}✓ pre-commit installed${NC}\n" || { printf "${RED}✗ Failed to install pre-commit${NC}\n"; exit 1; }
	@.venv/bin/pre-commit install >/dev/null 2>&1 && printf "${GREEN}✓ pre-commit hooks installed${NC}\n" || { printf "${RED}✗ Failed to install pre-commit hooks${NC}\n"; exit 1; }

mock:
	@cd services/mock && \
	make mock

mock-docker:
	@cd services/mock && \
	make mock-docker
