---
name: "Django App Specification"
description: "Expand an app definition into production-ready Django models, serializers, views, and test specifications"
version: "1.0"
origin: "superjeff"
---

## When to Activate

- Requirements Agent is processing an app definition
- User runs `/superjeff:specify <app_name>`

## Model Generation Pattern

```python
# Always this structure:
import uuid
from django.db import models

class MyModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # ... domain fields ...
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['<frequently_filtered_field>'])]

    def __str__(self):
        return self.<name_field>
```

## Serializer Generation Pattern

```python
# Always explicit fields — never __all__
class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = ['id', 'field1', 'field2', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_field1(self, value):
        # Business rule validation
        return value

    def validate(self, data):
        # Cross-field validation
        return data
```

## ViewSet Generation Pattern

```python
class MyModelViewSet(viewsets.ModelViewSet):
    serializer_class = MyModelSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    authentication_classes = [JWTAuthentication]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'category']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        # Always scope to authenticated user context
        return MyModel.objects.filter(owner=self.request.user)
```

## Permission Generation Pattern

```python
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
```

## Anti-Patterns

Avoid:
- `fields = '__all__'` in any serializer
- Missing `permission_classes` on any view
- `AllowAny` on write endpoints
- `null=True` on `CharField`
- Missing `__str__` on any model
- Auto-increment integer PKs on API-exposed models

## Related Skills

- [Business Case Decomposition](../decomposition/SKILL.md)
- [TDD Workflow](../testing/SKILL.md)
