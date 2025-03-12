# travel-assistant

This monorepo contains all components of our chatbot

## Structure

- **services**
  - **frontend**
    - Dockerfile
  - **backend**
    - Dockerfile
  - **data**
    - Dockerfile

## Developer Usage

### Conventional Commits

This repositories follows [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary).

The commit message should be structured as follows:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

The commit contains the following structural elements, to communicate intent to the consumers of your library:

- fix: a commit of the type fix patches a bug in your codebase (this correlates with PATCH in Semantic Versioning).
- feat: a commit of the type feat introduces a new feature to the codebase (this correlates with MINOR in Semantic Versioning).
- BREAKING CHANGE: a commit that has a footer BREAKING CHANGE:, or appends a ! after the type/scope, introduces a breaking API change (correlating with MAJOR in Semantic Versioning). A BREAKING CHANGE can be part of commits of any type.
- types other than fix: and feat: are allowed, for example @commitlint/config-conventional (based on the Angular convention) recommends build:, chore:, ci:, docs:, style:, refactor:, perf:, test:, and others.
- footers other than BREAKING CHANGE: <description> may be provided and follow a convention similar to git trailer format.

Source: [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary).

### Merge/Pull Requests

As multiple developers use this repository at the same time, the **main** branch should remain executable.

All changes to **main** must be requested and documented through a PR and approved by one other team member.

### Docker

For easy use, please add a Dockerfile to your service and add it to the `docker-compose.yml`.

Example:
```yaml
  frontend:
    build:
      context: ./services/frontend
    container_name: frontend-service
    ports:
      - "8081:8080"
    environment:
      - XYZ=abc
    restart: unless-stopped
```