from django.apps import apps as django_apps


def test_apps_del_dominio_estan_registradas() -> None:
    nombres_apps = {app.name for app in django_apps.get_app_configs()}

    assert "apps.productos" in nombres_apps
    assert "apps.clientes" in nombres_apps
    assert "apps.pedidos" in nombres_apps
