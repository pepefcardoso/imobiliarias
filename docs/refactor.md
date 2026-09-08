## Estrutura

project/
├── manage.py
├── webapp/ # projeto Django (settings/urls/wsgi/asgi) — renomeado p/ não colidir com config/ existente
│ ├── settings/
│ │ ├── base.py
│ │ ├── dev.py
│ │ └── prod.py
│ ├── urls.py
│ └── wsgi.py
├── apps/
├── accounts/
│ ├── models.py # User custom (AbstractUser, email como login)
│ ├── managers.py # UserManager sem username
│ ├── adapters.py # DefaultAccountAdapter / DefaultSocialAccountAdapter (stub, sem lógica custom ainda)
│ ├── urls.py # inclui allauth.urls
│ └── migrations/
├── search/ # inalterado
templates/
├── account/ # overrides dos templates padrão do allauth (login, signup, logout, password_reset)
├── socialaccount/ # override mínimo, mesmo desabilitado (allauth exige o template base pra não quebrar)
└── base.html
│ └── search/
│ ├── index.html # página completa
│ └── \_results.html # partial p/ swap via HTMX
├── static/
└── tests/

python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
