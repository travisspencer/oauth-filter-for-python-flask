# An OAuth 2.0 filter for Flask
This library provides an extension for protecting APIs with OAuth when using Flask.

## Usage

This filter can be used in two ways with Flask, either to run before all routes with the same authorization requirement,
which protects all endpoints. Many times however it's desirable to only protect certain endpoints, which then can be done
using the `decorator` pattern described below.

### Using filter as a before_request filter that runs before ALL routes

When running the filter [before_request](http://flask.pocoo.org/docs/0.11/api/#flask.Flask.before_request)  *all* routes, the same configuration will apply to all routes. So if the filter is
 configured to require a scope of "read" then all routes will require that scope. If routes have different needs then
 the decorator pattern should be used (see next section).

**Example using before_request**

```python
from flask import g, Flask
from oauth.oauth_filter import OAuthFilter

_app = Flask(__name__)
_oauth = OAuthFilter(verify_ssl=True)
_app.before_request(_oauth.filter)

@_app.route('/hello_world')
def hello_world():
    """
    :return: Returns a very useful JSON message when accessed.
    """
    print "OAuth Access token used for access"
    return json.dumps({"hello": g.user})
```


### Using filter as a decorator that runs before specific routes

Instead of setting the `before_request` a decorator can be added to the route that should be protected. This also enables the routes to have
 different scope requirements which could be handy.

*Important: The oauth decorator needs to be CLOSEST to the function*

```python
from flask import g, Flask
from oauth.oauth_filter import OAuthFilter

_app = Flask(__name__)
_oauth = OAuthFilter(verify_ssl=True)

@_app.route('/hello_world')
@_oauth.protect(["read"])
def hello_world():
    """
    :return: Returns a very useful JSON message when accessed.
    """
    print "OAuth Access token used for access"
    return json.dumps({"hello": g.user})
```

## Initializing the filter

**Filter global variable**

The OAuth filter should be setup the same way as Flask, a global reference and then initialized in main (or with the application)
The initialization depends on the type of tokens received. See the following examples.

```python
from flask import g, Flask
from oauth.oauth_filter import OAuthFilter

_app = Flask(__name__)
_oauth = OAuthFilter(verify_ssl=True)
```

**Using Opaque tokens**

When using Opaque tokens, the filter needs to resolve the reference by calling the introspection endpoint of the
OAuth server, this endpoint requires client credentials so the API needs to be a client of the OAuth server with the
permission to introspect tokens.

```python
if __name__ == '__main__':
    # configure the oauth filter
    _oauth.configure_with_opaque("https://oauth-server-host/oauth/v2/introspection", "api-client-id", "api-client-secret")

    # initiate the Flask app
    _app.run("localhost", debug=True, port=8000,
             ssl_context="adhoc")
```

**Using JWT tokens**

When using JWT (JWS) tokens, the filter will validate the signature of the token with the key that is provided on the
JWKS (Json Web Key Service) endpoint. The JWT contains a key id (kid) that is matched against the available public keys
on the OAuth server and then validated with that key.

```python
if __name__ == '__main__':
    # configure the oauth filter
    _oauth.configure_with_jwt("https://oauth-server-host/oauth/v2/metadata/jwks", "configured-issuer", "audience-of-token")

    # initiate the Flask app
    _app.run("localhost", debug=True, port=8000,
             ssl_context="adhoc")
```

## The g.user variable

When the filter accepts the request, it sets the `g.user` context local variable for that request with the username that
has been authenticated through the token. This is then accessible in the route.

*Future updates of this filter should add more information from the token into the context.*


## Handling errors

The filter may abort the request if the Access token is invalid or if the scopes in the access token doesn't match the
required scopes for the route.

**401 Unauthorized**

When an invalid token is presented the filter will give a 401 unauthorized.
To customize the response, use Flasks [errorhandler](http://flask.pocoo.org/docs/0.11/api/#flask.Flask.errorhandler) to add a response.

```python
@_app.errorhandler(401)
def unauthorized(error):
    return json.dumps({'error': "unauthorized",
                       "error_description": "No valid access token found"}), \
           401, {'Content-Type': 'application/json; charset=utf-8'}
```

**403 Forbidden**

When a valid token is presented the filter but it's missing the appropriate scopes then the request is aborted
with a 403 Forbidden.

```python
@_app.errorhandler(403)
def forbidden(error):
    return json.dumps({'error': "forbidden",
                       "error_description": "Access token is missing appropriate scopes"}), \
           403, {'Content-Type': 'application/json; charset=utf-8'}
```

## Dependencies

**python 2.x** Tested with python 2.7.10

**OpenSSL 1.0** to be able to do modern TLS versions. Python togheter with 0.9.x has a bug that makes it impossible to select protocol in the handshake, so it cannot connect to servers that have disabled SSLv2.

**Flask** as the web application

**pyjwkest** for JWK validation

Python dependencies can be installed by using Pip.
	pip install -r requirements.txt


## Questions and Support

For questions and support, contact Curity AB:

> Curity AB
>
> info@curity.io
> https://curity.io


Copyright (C) 2016 Curity AB.