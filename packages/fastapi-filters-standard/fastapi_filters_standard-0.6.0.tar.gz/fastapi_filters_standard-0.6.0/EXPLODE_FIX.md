# راهنمای استفاده از explode=False

برای اینکه Swagger UI مقادیر را با کاما جدا کند (به جای ارسال query parameterهای تکراری)، باید `fix_docs` را در پروژه خود فراخوانی کنید:

```python
from fastapi import FastAPI
from fastapi_filters_standard import fix_docs

app = FastAPI()

# این خط را اضافه کنید
fix_docs(app)

# بقیه کد شما...
```

یا می‌توانید مستقیماً در startup event فراخوانی کنید:

```python
@app.on_event("startup")
async def startup():
    fix_docs(app)
```

این کار باعث می‌شود که:
- `explode: False` در OpenAPI schema تنظیم شود
- Swagger UI مقادیر را با کاما جدا کند
- Query parameterهای تکراری ارسال نشوند

**مثال:**
- ✅ درست: `?user__in=uuid1,uuid2,uuid3&sort=+user,+name`
- ❌ غلط: `?user__in=uuid1&user__in=uuid2&user__in=uuid3&sort=+user&sort=+name`


