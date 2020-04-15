**Common package** `documentation`
=================================================

Пакет общих утилит, использующихся в разных модулях проекта.

**__init__.py**
--------------------
.. automodule:: common.__init__
   :members:

**decos.py**
---------------

.. automodule:: common.decos
   :members:

**descryptors.py**
---------------------

.. autoclass:: common.descryptors.Port
   :members:

**errors.py**
---------------------

.. autoclass:: common.errors.ServerError
   :members:

**metaclasses.py**
-----------------------

.. autoclass:: common.metaclasses.ServerMaker
   :members:



**utils.py**
---------------------


common.utils. **get_message** (client)

    Функция приёма сообщений от удалённых компьютеров. Принимает сообщения JSON,
    декодирует полученное сообщение и проверяет что получен словарь.

common.utils. **send_message** (sock, message)

    Функция отправки словарей через сокет. Кодирует словарь в формат JSON и отправляет через сокет.


**variables.py**
---------------------

    Глобальные переменные используемые в проекте



