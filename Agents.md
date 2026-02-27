# agents.md — Codex Cloud (Django Simple E-commerce REST API)

## Goal
Build a minimal e-commerce REST API using **Django + Django REST Framework**.
Keep it small, clean, and beginner-friendly.

## Non-negotiables (my preferences)
- Use **Function-Based Views (FBVs)** only (no ViewSets / GenericViews).
- Use `request.data.get("field")` for POST/PATCH reads (avoid serializers for now unless truly needed).
- Return **JSON responses** with clear status codes and error messages.
- Keep code readable over “clever”.



## Project structure
- Create a single app: `store`
- Models in `store/models.py`
- Admin registration for quick testing


## Out of scope (do NOT add unless asked)
- Auth / users / permissions
- Payments
- Stripe
- Docker
- Complex serializer validation
- Frontend