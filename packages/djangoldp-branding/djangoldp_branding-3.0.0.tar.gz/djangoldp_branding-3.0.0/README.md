# DjangoLDP Branding - GBS - Generic Branding System

Branding system based on the `config.json` of Orbit.

## Installation

Ensure that you have a valid `config.json`, the same as for your Orbit, at the root of your server.

`djangoldp_branding` must be on top of every package that you want to overwrite on your `ldppackages`.

Don't forget to run a `./manage.py collectstatic` whenever you update your application.

## Developpers

After plugging in this package, all your other packages will be able to use its templating functionalities.  
If you're unable to modify another package, feel free to overwrite it directly here.

### Access user datas

```html
{% extends "base.html" %}
{% load i18n %}
{% load orbit %}

{% trans "Hello" %}, {{ user.username }}!
```

### Access config.json values

```html
{% extends "base.html" %}
{% load i18n %}
{% load orbit %}

<p>{% trans "Welcome to" %} {{ orbit "client.name" }}!</p>
<img src='{% orbit "client.logo" %}' alt='{% orbit "client.name" %}'>
```

### Debug mode awareness

```html
{% extends "base.html" %}
{% load i18n %}

<p>{% if debug_flag %}{% trans "You are in debug=True!" %}{% endif %}</p>
```

### Client URL

```html
{% extends "base.html" %}
{% load i18n %}

<p>{% trans "Client URL" %}: <a href="{% default_client %}">{% default_client %}</a></p>
```

### Server URL

```html
{% extends "base.html" %}
{% load i18n %}

<p>{% trans "Server URL" %}: <a href="{% base_url %}">{% base_url %}</a></p>
```

## Troubleshooting

### Missing "xyz" template

Set `DEBUG` to `True` to activate a `/templates-registry/` route that'll list all your application templates and which of them are not overrided.

When the template registry list a template as `Exist, Unmanaged`, it means that another package is loaded with the same package **before** djangoldp-branding in your `ldppackages`.

Admin templates are excluded by default, to include them, reach `/templates-registry/with-admin/`.

### Missing style on pages

Ensure to `./manage.py collectstatic` and that you're serving them.

## i18n

Collect every messages to `djangoldp_branding/locale/**/LC_MESSAGES/django.po`:

```bash
./manage.py makemessages --locale=fr --locale=en --locale=es
```

You may need a `locale` folder at the root of your server.

Before commit:

```bash
./manage.py compilemessages --locale=fr --locale=en --locale=es
```
