# FORK Transkribus Web UI FORK
Initial rework of [TSX] TSX for the [READ] READ project.

This project uses python [Django]

So far this is a skeletal website to aid design discussion about the architechture of the WebUI. The basic idea is that the project will have 3 apps for each of the three modules described in the specification

* Base module (working title library)
* Publishing module
* Modification module

Though possibly more apps for smaller bits of functioanilty... 

UPDATE: More details can be found in the [Synopsis of Transkribus WebUI/Library](https://github.com/Transkribus/TranskribusWebUI/blob/master/library/SYNOPSIS.md)

## Building
Here is a short guide with steps that need to be performed to build Transkribus Web UI.

### Requirements
python and pip. Use pip to install the packages below.

### Build Steps
You need to have pip installed. Usage of Virtualenv is recommended. To run Transkribus Web UI install the following with pip:
```sh
pip install django
pip install djangorestframework
pip install requests
pip install xmltodict
pip install eulxml
pip install django-bootstrap3
pip install nocaptcha_recaptcha
```

### Running
To run, create the database:

```sh
python manage.py makemigrations
python manage.py migrate
```

Then start the server:
```sh
python manage.py runserver --settings read.settings.default
```
### Deployment

Perform the steps in the "Running" section of this Readme except starting the server.
Make sure that Apache httpd and mod_wsgi is installed and that the apache user can read and write the directory where you have checked out the git repository.

Create a file in /etc/httpd/conf.d/ named e.g. library.conf.
Write the following content to this file:
```
WSGIScriptAlias / /path/to/TranskribusWebUI/read/wsgi.py process-group=example.com
WSGIPythonPath /path/to/TranskribusWebUI
WSGIDaemonProcess example.com python-path=/path/to/TranskribusWebUI:/usr/lib/python2.7/site-packages
WSGIProcessGroup example.com

Alias /media/ /path/to/TranskribusWebUI/media/
Alias /static/ /path/to/TranskribusWebUI/static/

<Directory /path/to/TranskribusWebUI/read>
        <Files wsgi.py>
                Require all granted
        </Files>
</Directory>

<Directory /path/to/TranskribusWebUI/static>
        Require all granted
</Directory>

<Directory /path/to/TranskribusWebUI/media>
        Require all granted
</Directory>

```
Restart httpd and check if everything works.

### Internationalisation

The Transkribus Web UI uses django's internationalisation and localisation (note the use of 's' rather than 'z'). The site has been prepared for translations for all the official languages of the EU (https://en.wikipedia.org/wiki/Languages_of_the_European_Union)

#### Conditions for internatioanlisation:
* templates need to ```{% load i18n %}```
* then anything in ```{% trans "some phrase" %}``` will be translated if a translation is available
* .py files need to ```from django.utils.translation import ugettext_lazy as _```
* then anything in _("some phrase") will be translated if a translation is available

#### Translate
To make translations available:
* find the appropriate .po file ```locale/[lang_code]/LC_MESSAGES/django.po```
* In this file you will see msgid's that correspond to the phrases in ```{% trans "..." %}``` or ```_("...")```
* Simply fill in the msgstr with the correct translation eg:
```
#: library/forms.py:7
msgid "Given Name"
msgstr ""
```
* commit the changes to the .po files

#### Adding new phrases

If you have added a new phrase to a template or .py file there are a couple of things to do on the host afterwards. First the new phrases need to be added to the .po files. This is done with the following command:

* ```django-admin makemessages -l [lang_code] (or -a for all languages)```

Then (once the translations have been made in the .po files) the phrases must be be recompiled with:

* ```django-admin compilemessages```

### Links

* [WebUISpec] WebUI spec
* [Django]
* [Python]
* [pip]
* [Virtualenv]

[WebUISpec]: <https://read02.uibk.ac.at/wiki/index.php/WebUI_spec>
[READ]: <http://read.transkribus.eu>
[TSX]: <https://github.com/Transkribus/TSX>
[Django]: <https://www.djangoproject.com/>
[Python]: <https://www.python.org/>
[pip]: <https://pip.pypa.io/>
[Virtualenv]: <https://virtualenv.pypa.io/>
