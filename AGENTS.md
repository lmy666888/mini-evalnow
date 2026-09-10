# Mini EvalNow

## Project Goal

Mini EvalNow is a bilateral feedback platform.

Students and faculty submit feedback independently.
Neither party can see the other party's feedback until both have submitted.
Once both submissions exist, the session becomes unlocked.

The system may use a local LLM to help rewrite feedback into more constructive language, but AI-generated content must always be reviewed by a human before publication.

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT authentication
- Argon2 password hashing
- Ollama
- pytest
- Docker
- Docker Compose

## Development Rules

- Keep the architecture simple and understandable.
- Prefer explicit code over unnecessary abstractions.
- Do not introduce microservices.
- Do not introduce Redis, Kafka, RabbitMQ, or Kubernetes unless explicitly requested.
- Authorization must always be enforced server-side.
- Never expose one party's feedback before the session is unlocked.
- Never overwrite original feedback with AI-generated content.
- Preserve raw user feedback.
- AI output is only a suggestion until reviewed by a human.
- New features should include appropriate tests.
- Do not modify unrelated files.
- Explain significant architectural decisions.

## Development Approach

Implement the project incrementally.

Before making major changes:
1. Inspect the existing codebase.
2. Explain the proposed approach.
3. Make the smallest reasonable change.
4. Run relevant tests.
5. Review the resulting diff.

## Testing

Run the test suite with:

pytest
