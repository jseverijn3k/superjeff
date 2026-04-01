---
name: "CLAUDE.md Template — Django Project"
description: "Generieke CLAUDE.md template voor nieuwe Django projecten op basis van SuperJeff conventions"
version: "1.0"
origin: "superjeff"
---

# Claude Rules - {{PROJECT_NAME}}

Dit document beschrijft de architectuur, conventies en regels voor de {{PROJECT_NAME}} repository.
Claude moet deze regels volgen bij het genereren of aanpassen van code.

---

## Project Overzicht

**{{PROJECT_NAME}}** — {{PROJECT_DESCRIPTION}}

- **Stack:** Django 5.x, PostgreSQL, Redis, Celery
- **Frontend:** Django templates + HTMX
- **Infrastructure:** Docker, Traefik, Cloudflare Tunnel

---

## Directory Structuur

```
{{project_slug}}/
├── backend/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   ├── production.py
│   │   │   └── testing.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── celery.py
│   │
│   ├── apps/
│   │   ├── core/
│   │   ├── users/
│   │   └── <feature_apps>/
│   │
│   ├── api/
│   │   ├── urls.py
│   │   └── v1/
│   │       ├── views/
│   │       └── serializers/
│   │
│   ├── templates/
│   ├── static/
│   ├── manage.py
│   ├── pytest.ini
│   ├── conftest.py
│   ├── requirements-dev.txt
│   ├── requirements-prod.txt
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   └── entrypoint.sh
│
├── vps-infra/
│   ├── docker-compose.yml
│   ├── docker-compose.test.yml
│   └── traefik/
│
├── docs/
├── CLAUDE.md
└── README.md
```

---

## Architectuur Patronen

### 1. Layered Architecture

```
┌─────────────────────────────────────┐
│           Views / API               │  ← HTTP handling alleen
├─────────────────────────────────────┤
│            Services                 │  ← Business logic
├─────────────────────────────────────┤
│          Repositories               │  ← Data access (optioneel)
├─────────────────────────────────────┤
│        Models (Django ORM)          │  ← Data definitie
└─────────────────────────────────────┘
```

### 2. Service Layer (VERPLICHT)

**Alle business logic hoort in services, NIET in views.**

```python
# GOED ✓
# apps/<feature>/views.py
from <feature>.services import <Feature>Service

@login_required
def resource_list(request):
    service = <Feature>Service(request.user)
    result = service.list_resources()
    return render(request, "<feature>/list.html", {"items": result["items"]})

# FOUT ✗
@login_required
def resource_list(request):
    items = MyModel.objects.filter(owner=request.user)
    # ... business logic direct in view ...
    return render(request, "<feature>/list.html", {"items": items})
```

**Service locatie:** `apps/<feature>/services/<service_name>.py`

**Service conventies:**
- Één service per domein concept (aggregate root)
- Constructor accepteert `user` of context object
- Methods zijn actions (verbs): `create_`, `update_`, `delete_`, `get_`, `can_`, `list_`
- Return types zijn expliciet (model instances, dicts, tuples)
- Raise domein-exceptions voor business rule violations
- Max ±300 regels per service — split bij sync logic, permissions, side-effects
- Stateless: geen mutable instance state
- Accepteert NOOIT: `request`, `HttpResponse`, serializer instances

```python
# apps/<feature>/services/<feature>.py
from django.db import transaction
from <feature>.models import MyModel

class MyFeatureService:
    def __init__(self, user):
        self.user = user

    def list_resources(self, offset=0, limit=10):
        return {
            "items": MyModel.objects.filter(
                owner=self.user
            ).select_related("category")[offset:offset + limit],
            "total_count": MyModel.objects.filter(owner=self.user).count(),
        }

    def get_resource(self, resource_id):
        return MyModel.objects.get(id=resource_id, owner=self.user)

    @transaction.atomic
    def create_resource(self, data):
        return MyModel.objects.create(owner=self.user, **data)

    @transaction.atomic
    def delete_resource(self, resource):
        resource.delete()
```

### 3. Function-Based Views (VERPLICHT)

**Gebruik ALTIJD Function-Based Views (FBVs), GEEN Class-Based Views of ViewSets.**

```python
# GOED ✓
@login_required
def resource_list(request):
    service = MyFeatureService(request.user)
    result = service.list_resources()
    return render(request, "feature/list.html", result)

# FOUT ✗
class ResourceListView(ListView):      # NOOIT
class ResourceViewSet(ModelViewSet):   # NOOIT
class ResourceAPIView(APIView):        # NOOIT
```

### 4. API Layer (Separaat van Apps)

**API endpoints leven in `api/`, NIET in `apps/`. Gebruik `@api_view` decorators.**

```python
# api/v1/views/<feature>.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from apps.<feature>.services import MyFeatureService
from api.v1.serializers.<feature> import ResourceSerializer

@extend_schema(summary="List resources", responses={200: ResourceSerializer(many=True)})
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_resources(request):
    service = MyFeatureService(request.user)
    result = service.list_resources(
        offset=int(request.GET.get("offset", 0)),
        limit=int(request.GET.get("limit", 10)),
    )
    serializer = ResourceSerializer(result["items"], many=True)
    return Response({"items": serializer.data, "total": result["total_count"]})

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def resource_detail(request, resource_id):
    service = MyFeatureService(request.user)
    resource = service.get_resource(resource_id)

    if request.method == "GET":
        return Response(ResourceSerializer(resource).data)
    elif request.method == "PUT":
        serializer = ResourceSerializer(resource, data=request.data)
        serializer.is_valid(raise_exception=True)
        service.update_resource(resource, serializer.validated_data)
        return Response(ResourceSerializer(resource).data)
    elif request.method == "DELETE":
        service.delete_resource(resource)
        return Response(status=204)
```

**Expliciete URL routes (geen routers):**
```python
# api/v1/urls.py
from django.urls import path
from api.v1.views import <feature>

urlpatterns = [
    path("<feature>/", <feature>.list_resources),
    path("<feature>/<int:resource_id>/", <feature>.resource_detail),
]
```

### 5. OpenAPI Documentation (drf-spectacular)

**Alle API endpoints MOETEN gedocumenteerd zijn met `@extend_schema`.**

---

## VERBODEN — Never Use These

1. **Class-Based Views** — `class SomeView(APIView)`, `class SomeView(View)`, elk CBV patroon
2. **ViewSets** — `class SomeViewSet(ModelViewSet)`, elk ViewSet patroon
3. **Generic Views** — `CreateAPIView`, `ListAPIView`, `RetrieveAPIView`, etc.
4. **DRF Routers** — `DefaultRouter`, `SimpleRouter`
5. **Business logic in views** — alles via services
6. **Direct model queries in views** — alles via services
7. **API endpoints in `apps/`** — alles in `api/`
8. **Django signals voor business logic** — alleen voor cache invalidation en auditing
9. **`print()` statements** — gebruik `logging`
10. **`request.user.is_staff` direct in views** — ownership checks in services
11. **`eval()` of `exec()`**
12. **Hardcoded credentials**

---

## Model Rules

- Models zijn "dumb" — geen business methods, geen cross-model queries, geen permissions logic
- Properties mogen alleen afgeleide velden zijn — GEEN database queries in properties
- Gebruik `UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` voor publieke resources
- Altijd `__str__` implementeren
- Altijd `created_at = DateTimeField(auto_now_add=True)` en `updated_at = DateTimeField(auto_now=True)`
- Altijd `Meta.ordering` definiëren voor list views
- Nooit `null=True` op `CharField` of `TextField` — gebruik `blank=True, default=""`

---

## Serializer Rules

- Bevatten GEEN business logic
- Doen GEEN ownership checks
- `create()` / `update()`: alleen mapping van data → model; complexe logic altijd via services
- Gebruik GEEN `CurrentUserDefault` voor ownership
- Nooit `fields = "__all__"` — altijd expliciet opsommen

---

## Query Performance

Services zijn verantwoordelijk voor `select_related` en `prefetch_related`. Views mogen dit NIET doen.
Elke service method die een QuerySet teruggeeft voor een list view MOET N+1-safe zijn.

```python
# GOED ✓
def list_resources(self):
    return MyModel.objects.filter(
        owner=self.user
    ).select_related("category").prefetch_related("tags")

# FOUT ✗
def list_resources(self):
    return MyModel.objects.filter(owner=self.user)  # N+1!
```

---

## Exception & Error Handling

**Definieer domein-exceptions per app:**
```python
# apps/<feature>/exceptions.py
class FeatureError(Exception):
    pass

class ValidationError(FeatureError):
    pass

class PermissionDenied(FeatureError):
    pass
```

**Services raisen domein-exceptions. Views vertalen ze:**
```python
# HTML view
try:
    service.perform_action()
    messages.success(request, "Done!")
except FeatureValidationError as e:
    messages.error(request, str(e))
return redirect("feature:index")

# API view
try:
    service.perform_action()
    return Response({"status": "ok"})
except FeatureValidationError as e:
    raise DRFValidationError(detail={"detail": str(e)})
```

**Geen try/except in services behalve voor transacties.**

---

## Caching Pattern

Cache expensive queries (>500ms, frequently accessed, not per-request-changing):

```python
from django.core.cache import cache
import json, logging
from django.core.serializers.json import DjangoJSONEncoder

logger = logging.getLogger(__name__)

CACHE_KEY = "resource_list_{user_id}_{offset}_{limit}"
CACHE_TTL = 900  # 15 minutes

def get_cached_resources(user_id, offset, limit):
    key = CACHE_KEY.format(user_id=user_id, offset=offset, limit=limit)
    cached = cache.get(key)
    if cached:
        logger.info(f"Cache HIT: {key}")
        return json.loads(cached)
    data = _compute_expensive_query(user_id, offset, limit)
    cache.set(key, json.dumps(data, cls=DjangoJSONEncoder), CACHE_TTL)
    logger.info(f"Cache MISS: {key}, cached {CACHE_TTL}s")
    return data
```

**Cache invalidation via signals (alleen voor technische concerns):**
```python
@receiver([post_save, post_delete], sender=MyModel)
def invalidate_caches(sender, instance, **kwargs):
    cache.delete(f"resource_list_{instance.owner_id}_*")
```

---

## Celery & Background Tasks

- Alleen services triggeren Celery tasks — views triggeren NOOIT direct tasks

```python
# tasks.py
@shared_task
def perform_heavy_task(user_id):
    from apps.<feature>.services import MyFeatureService
    MyFeatureService(user_id).do_heavy_work()

# service.py — trigger async
def trigger_async(self):
    from .tasks import perform_heavy_task
    perform_heavy_task.delay(self.user.id)
```

---

## Database Transacties

Gebruik `@transaction.atomic` bij create/update flows met meerdere writes, sync flows, delete cascades.

---

## Idempotente Migraties (VERPLICHT voor raw SQL)

Migraties die raw SQL gebruiken MOETEN volledig idempotent zijn:

```python
def add_columns_idempotent(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = '<table>'")
        existing = {row[0] for row in cursor.fetchall()}
        if "<column>" not in existing:
            cursor.execute("ALTER TABLE <table> ADD COLUMN <column> boolean DEFAULT true NOT NULL")
        cursor.execute("SELECT indexname FROM pg_indexes WHERE schemaname = 'public'")
        existing_indexes = {row[0] for row in cursor.fetchall()}
        if "<index_name>" not in existing_indexes:
            cursor.execute("CREATE INDEX IF NOT EXISTS <index_name> ON <table>(<column>)")

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(add_columns_idempotent, migrations.RunPython.noop),
        migrations.SeparateDatabaseAndState(
            state_operations=[migrations.AddField(model_name="<model>", name="<field>", field=models.BooleanField(default=True))],
            database_operations=[],
        ),
    ]
```

---

## Logging

```python
import logging
logger = logging.getLogger(__name__)

# Niveaus:
# logger.info()    — business events (create, delete, sync)
# logger.warning() — recoverable issues
# logger.error()   — exceptions

# NOOIT loggen: passwords, tokens, API keys, PII
```

---

## Testing Strategy

```
apps/<feature>/tests/
├── __init__.py
├── conftest.py
├── factories.py
├── test_models.py
├── test_services.py
├── test_views.py
└── test_api.py
```

**Factories (Factory Boy) — altijd, nooit handmatige object creatie:**
```python
class MyModelFactory(DjangoModelFactory):
    class Meta:
        model = MyModel
    owner = factory.SubFactory("apps.users.tests.factories.UserFactory")
    name = factory.Sequence(lambda n: f"Resource {n}")
```

**Service tests:**
```python
@pytest.mark.django_db
class TestMyFeatureService:
    def test_list_resources_scoped_to_user(self, user, other_user):
        MyModelFactory.create_batch(3, owner=user)
        MyModelFactory(owner=other_user)
        result = MyFeatureService(user).list_resources()
        assert result["total_count"] == 3

    def test_get_resource_ownership_enforced(self, user, other_user):
        resource = MyModelFactory(owner=user)
        with pytest.raises(MyModel.DoesNotExist):
            MyFeatureService(other_user).get_resource(resource.id)
```

**Pytest configuratie:**
```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.testing
addopts = --reuse-db --nomigrations --cov=apps --cov-report=term-missing
```

---

## Git Workflow (VERPLICHT)

Elke stap in de feature-ontwikkeling produceert een eigen commit. Nooit meerdere stappen samenvoegen.

### Commit Format

```
<type>(<feature>): <beschrijving>
```

| Type | Wanneer |
| --- | --- |
| `model` | Na aanmaken/aanpassen models + migraties |
| `service` | Na aanmaken/aanpassen service layer |
| `test` | Na schrijven van failing tests (RED) |
| `implement` | Na implementatie die tests doet slagen (GREEN) |
| `refactor` | Na code review en opschonen |
| `api` | Na aanmaken API views + serializers |
| `view` | Na aanmaken HTML views + templates |
| `fix` | Na bugfix |
| `config` | Na settings/infra wijzigingen |

### Voorbeelden

```
model(orders): Order en OrderItem modellen + migraties

service(orders): OrderService met create, list, cancel methoden

test(orders): failing tests voor order CRUD en cancel flow

implement(orders): OrderService implementatie — alle tests groen

refactor(orders): select_related toevoegen, N+1 opgelost

api(orders): GET/POST /api/v1/orders/ met OpenAPI documentatie

view(orders): order list en detail HTML views
```

### Regels

- MUST commit na elke stap — nooit stappen samenvoegen in één commit
- MUST `implement` commit alleen doen als alle tests slagen
- MUST NIET `--no-verify` gebruiken
- MUST migraties meenemen in dezelfde commit als de bijbehorende model wijziging

---

## Docker & Deployment

```bash
# Test environment
cd vps-infra
docker-compose -f docker-compose.test.yml up -d
docker-compose -f docker-compose.test.yml logs -f <service>
docker-compose -f docker-compose.test.yml down
```

---

## Checklist voor Nieuwe Features

- [ ] Model(s) aangemaakt in `apps/<feature>/models.py`
- [ ] Migraties aangemaakt en getest (idempotent indien raw SQL)
- [ ] **git commit:** `model(<feature>): ...`
- [ ] Service(s) aangemaakt in `apps/<feature>/services/`
- [ ] **git commit:** `service(<feature>): ...`
- [ ] Failing tests geschreven
- [ ] **git commit:** `test(<feature>): ...`
- [ ] Implementatie compleet — alle tests groen
- [ ] **git commit:** `implement(<feature>): ...`
- [ ] Views gebruiken services (geen directe model access)
- [ ] URL patterns toegevoegd
- [ ] Templates aangemaakt
- [ ] **git commit:** `view(<feature>): ...`
- [ ] API serializers en views (indien API nodig)
- [ ] OpenAPI documentatie (`@extend_schema`)
- [ ] **git commit:** `api(<feature>): ...`
- [ ] Cache invalidation toegevoegd indien nodig
- [ ] N+1 queries opgelost in services

---

**Enforced By:** All developers and AI assistants working on this project.
