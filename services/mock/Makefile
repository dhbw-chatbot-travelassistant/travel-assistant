# Colors
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
NC     := \033[0m

.PHONY: mock

mock:
	@printf "${YELLOW}Running mock...${NC}\n"
	@printf "${YELLOW}Installing npm packages...${NC}\n" && \
	npm install && \
	printf "${YELLOW}Starting mock server...${NC}\n" && \
	node --max-http-header-size=32768 server.js

mock-build:
	@printf "${YELLOW}Building mock...${NC}\n"
	@docker build -t travel-assistant/mock .;

mock-up:
	@printf "${YELLOW}Starting mock...${NC}\n"
	@docker-compose -f mock-stack.yml up --detach;

mock-down:
	@printf "${YELLOW}Stopping existing container...${NC}\n"
	@docker-compose -f mock-stack.yml down;

mock-docker:
	@printf "${YELLOW}Running mock in Docker...${NC}\n"
	@make mock-down;
	@make mock-build;
	@make mock-up;
