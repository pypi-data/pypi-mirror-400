# starlette-admin-beanie-backend

<div style="display: flex; gap: 10px">
<a href="https://github.com/arnabJ/starlette-admin-beanie-backend/actions">
    <img src="https://github.com/arnabJ/starlette-admin-beanie-backend/actions/workflows/publish.yml/badge.svg" alt="Publish">
</a>
<a href="https://pypi.org/project/starlette-admin-beanie-backend/">
    <img src="https://badge.fury.io/py/starlette-admin-beanie-backend.svg" alt="Package version">
</a>
<a href="https://pypi.org/project/starlette-admin-beanie-backend/">
    <img src="https://img.shields.io/pypi/pyversions/starlette-admin-beanie-backend" alt="Supported Python versions">
</a>
<a href="https://pepy.tech/projects/starlette-admin-beanie-backend">
<img src="https://static.pepy.tech/personalized-badge/starlette-admin-beanie-backend?period=total&units=INTERNATIONAL_SYSTEM&left_color=GRAY&right_color=RED&left_text=downloads" alt="PyPI Downloads">
</a>
</div>

🧪 A package to use Beanie-ODM as a backend with starlette-admin.

## ✴️ Documentation
**Follow the documentation [here](https://arnabJ.github.io/starlette-admin-beanie-backend) or check a quick guide below.**

## 🔧 Install
```bash
  pip install starlette-admin-beanie-backend
```

## ⚙️ Usage
```python
from starlette_admin_beanie_backend import Admin, ModelView
from .auth import AdminAuthProvider
from .models import User

def set_db_admin(app):
    # Create the Admin Interface
    admin = Admin(
        title="Test App",
        base_url="/admin",
        debug=True,
        auth_provider=AdminAuthProvider(),
    )
    
    # Add the Admin Views
    admin.add_view(ModelView(User, icon="fa fa-users"))

    # Mount app
    admin.mount_to(app)
```

## 🤝 Contribute
Contributions are welcome! Whether you’ve spotted a bug, have ideas to improve the Package, or want to extend functionality — I’d love your input. Please fork the repository, work on the dev-colab branch, and open a pull request when ready. Be sure to include clear commit messages and tests where applicable. Let’s build something great together!

- Submit PRs to `dev-colab`
- Please follow the coding style
---

## 🙏🏼 Credits
- jowilf (https://github.com/jowilf)
- BeanieODM (https://github.com/BeanieODM)
- pydantic (https://github.com/pydantic)
