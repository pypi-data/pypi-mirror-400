# REST-RPC

REST-RPC is a Python library that makes writing type-checked REST APIs easy (by allowing you to define your API once and use it on both the server and the client).

It automatically creates convenient front-end bindings to your API for you, so from the front-end developer's perspective it's indistinguishable from an RPC library, hence the name.

REST-RPC's type-checking is based on Pydantic. For the back-end, it used FastAPI. For the front-end, it supports `requests`, `urllib3`, `httpx`, and `aiohttp` (or provide your own transport layer). If you want to use REST-RPC in the webbrowser, you can: It supports `pyodide`'s `pyfetch` and `pyscript`'s `fetch`!
This means that the only "hard" dependency is `pydantic`. Of course, you'll need FastAPI in the back-end and one of the mentioned HTTP libraries for the front-end.

REST-RPC is for you, if you:
- …like FastAPI and Pydantic.
- …just want to write simple type-checked REST APIs without frills.
- …don't want to repeat yourself when writing the front-end code.

Visit the [GitHub page](https://github.com/felsenhower/rest-rpc) for more information.


