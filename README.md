# Transkribus Web UI
Initial rework of [TSX] TSX for the [READ] READ project.

This project uses python [Django] Django

So far this is a skeletal website to aid design discussion about the architechture of the WebUI. The basic idea is that the project will have 3 apps for each of the three modules described in the specification

* Base module (working title library)
* Publishing module
* Modification module

Though possibly more apps for smaller bits of functioanilty... 

## Building
Here is a short guide with steps that need to be performed to build Transkribus Web UI.

### Requirements
python and pip. Use pip to install the packages below.

### Build Steps
You need to have pip installed. Usage of Virtualenv is recommended. To run Transkribus Web UI install the following with pip:
```sh
pip install django django-bootstrap3 requests xmltodict
```

### Running
To run import the following modules:
```sh
pip install django django-bootstrap3 requests xmltodict
```

and create the database:

```sh
python manage.py makemigrations
python manage.py migrate
```

Then start the server:
```sh
python manage.py runserver
```

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
