# One time secret service.

Allows to save temporal secret with passphrase and get it back one time. After that, secret is deleted from server.

Developed as trainee task from avito.

## Task

JSON Api service, that creating secret with passphrase and returns one-time key to access to the secret.

### URIs
* `/generate` - takes secret and passphrase and returns `secret_key` by which the secret can be got.
* `/secrets/{secret_key}` - takes passphrase and returns secret.

### Requirements
* Language: Python 3.7.
* Using `Docker`, service must be launched via `docker-compose up`.
* There are no restrictions on using technlogies.
* Code must conform to PEP. Required to use `type hints`. Documentation must be written to public methods.

### Challenges
- [x] Tests written (70% minimum by task, 97% reached)
- [x] Asynchonous request handling (Using aiohttp server)
- [x] Data is stored in external database, that also defined in `docker-compose`
- [x] Secrets and passphrases are stored with encryption (Using [cryptography](https://cryptography.io/en/latest/fernet/) python library)
- [x] Added option to define time-to-live for secrets (Using TTL index as max ttl and additional api for user-defined TTL)


## Installation

Simply clone repository
```shell
$ git clone https://github.com/Saiel/avito-web-secrets
```
And run docker-compose
```shell
$ sudo docker-compose up
```
After 20 seconds service will be ready

## Usage
Save secret
```shell
$ curl \
    http://localhost/generate \
    -d '
    {
        "secret": "some secret",
        "phrase": "some phrase"
    }'
```
It returns JSON response:
```json
{
    "secret_key": "asdasdasda_some_key_asdasdasdasd"
}
```

Then get secret
```shell
$ curl \
    http://localhost/secrets/asdasdasda_some_key_asdasdasdasd \
    -d '
    {
        "phrase": "some phrase"
    }'
```
That returns
```json
{
    "secret": "some secret"
}
```
Or
```json
{
    "Error": "Key not found"
}
```
If secret expired.

By default TTL of secret is 7 days, and this is max value. To save secret with less TTL, add "ttl" field to `/generate` request:
```shell
$ curl \
    http://localhost/generate \
    -d '
    {
        "secret": "some secret",
        "phrase": "some phrase",
        "ttl": {
            "days": 3,
            "hours": 4,
            "minutes": 5
        }
    }'
```


## Technical description

### Core
* Service is developed via Python 3.7 and aiohttp library.
* Aiohttp application can be started via aiohttp/web module:
    ```shell
    $ python -m aiohttp.web src.app:init_app -U <socket> -H <host> -P <port>
    ```
    or via directly running src/app.py

    ```shell
    $ python -m src.app -U <socket> -P <port> --log-level <level>
    ```
* In container service is managed by [supervisord](http://supervisord.org/), that keeps runnig 4 proccess (See [supervisord.conf](confs/supervisor/supervisord.conf)).
* Requests are balanced between proccesses with nginx. (See [nginx.conf](confs/nginx/nginx.conf))
* Communication bettween nginx and service occurs via unix sockets. They are stored in internal docker-compose volume.
* Logs of procceses and supervidord stored in ./logs/web (after first `docker-compose up` run)

### Database
* As database used MongoDB
* Data is stored in ./mongodb (after first `docker-compose up` run)
* Database network is isolated, but can be opened via forwarding the 27017 (by default) port.

### .env
* Contains sensitive and other variable information for service initialization.
* Should be not stores in git normally.

### Testing
Unittesting can be done with 
```shell
$ docker-compose run --rm web python -m unittest src/tests.py
```

Coverage measured via [coverage](https://coverage.readthedocs.io/en/coverage-5.1/) library inside container web:

![coverage screen](https://user-images.githubusercontent.com/32503439/80918705-03a12480-8d6f-11ea-914a-57a1b4390edd.png)

### Code formatting and documentation
*  [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
*  Documented with docstring in [Google style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
