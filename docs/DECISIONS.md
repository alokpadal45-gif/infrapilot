# Decisions

## 001: Docker and Compose
- Why: the app runs the same on any machine, and `docker compose up` starts everything.
- Why Postgres in a container: no manual install, and the data survives in a volume.
- Security: non-root user, database exposed only to localhost, password in .env (git-ignored).
- Limitation: Docker restarts a crashed container, but it does not understand app health.

## 002: CI with GitHub Actions
- Why: every push is linted, tested and built on a clean machine, so "works on my laptop" is not enough.
- Why mocks in tests: slow and crash modes would wait 3 seconds or kill the test runner, so the tests replace sleep and exit with fakes.
- Why `needs: test` on the Docker build: don't build an image from code that fails its tests.
- Limitation: CI doesn't deploy anything yet (that's CD, later).
