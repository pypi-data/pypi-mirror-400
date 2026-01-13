# راهنمای انتشار در PyPI

## مراحل انتشار

### 1. نصب ابزارهای لازم

```bash
pip install build twine
```

### 2. ساخت package

```bash
python -m build
```

این دستور فایل‌های `dist/fastapi-filters-standard-0.1.0.tar.gz` و `dist/fastapi_filters_standard-0.1.0-py3-none-any.whl` را می‌سازد.

### 3. بررسی package

```bash
twine check dist/*
```

### 4. آپلود به TestPyPI (اختیاری - برای تست)

```bash
twine upload --repository testpypi dist/*
```

برای تست می‌توانید نصب کنید:
```bash
pip install --index-url https://test.pypi.org/simple/ fastapi-filters-standard
```

### 5. آپلود به PyPI

```bash
twine upload dist/*
```

شما به یک API token از PyPI نیاز دارید. می‌توانید آن را از https://pypi.org/manage/account/token/ دریافت کنید.

### 6. نصب و تست

```bash
pip install fastapi-filters-standard
```

## نکات مهم

- قبل از انتشار، مطمئن شوید که:
  - همه تست‌ها pass می‌شوند: `pytest`
  - version را در `pyproject.toml` به‌روز کرده‌اید
  - README.md را به‌روز کرده‌اید
  - اطلاعات author را در `pyproject.toml` به‌روز کرده‌اید
  - repository URL را در `pyproject.toml` به‌روز کرده‌اید

## به‌روزرسانی نسخه

برای انتشار نسخه جدید:
1. version را در `pyproject.toml` افزایش دهید
2. مراحل بالا را تکرار کنید

