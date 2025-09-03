# AI-Game-Builder

هذا المشروع يستخدم ذكاء اصطناعي لتوليد وبناء ألعاب 3D/4K بشكل تلقائي.  
يدعم توليد الأكواد، تعديل الملفات، وإدارة المشروع عبر GitHub مباشرة مع Copilot.

## مميزات المشروع
- توليد سكربتات اللعبة تلقائيًا.
- إدارة الملفات والمجلدات تلقائيًا.
- التكامل مع GitHub Actions لتشغيل AI بعد أي تعديل.
- دعم Copilot للكتابة المباشرة والتعديل على المستودع.

## المتطلبات
- Python 3.10+
- مكتبات:
  - fastapi
  - uvicorn[standard]
  - gitpython
  - httpx
  - transformers
  - sentence-transformers
  - faiss-cpu
