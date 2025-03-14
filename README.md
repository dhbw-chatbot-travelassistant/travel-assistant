# Travel Assistant

**Travel Assistant** is a student project at DHBW Stuttgart. This repository contains the neccessary source-code for a proof of concept.

## Structure

The repository is structured as a monorepo and contains all relevant services.

- **services**
  - **frontend**
    - Dockerfile
  - **backend**
    - Dockerfile
  - **data**
    - Dockerfile

## Developer Usage

Contact [**Johannes**](https://github.com/Jopeeee) for any issues and concerns with the dev environment. The given specifications should help us to create a well-structured and organized project.

#### Conventional Commits

This repositories follows [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary).

The commit message should be structured as follows:

```
<type>([optional scope]): <description>

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

#### Branching

Based on [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary), the branches should resemble the main purpose in their name. Use the following structure for your branches:

```
<type>/<scope>

i.e. fix/error-on-login, docs/frontend-readme
```

The corresponding pull requests will be labeled accordingly.



#### Merge/Pull Requests

As multiple developers use this repository at the same time, the **main** branch should remain executable.

All changes to **main** must be requested and documented through a PR and approved by one other team member.

#### Docker

For easy use, please add a Dockerfile to your service and add it to the `docker-compose.yml`.

*Example:*
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

#### Usage

*Run:*
```bash
docker-compose -f docker-compose.yml up
```
