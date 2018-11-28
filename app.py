import json

from flask import g, Flask, request, make_response
from oauth.oauth_filter import OAuthFilter

_app = Flask(__name__)
_refOauth = OAuthFilter(verify_ssl=False)
#_jwtOauth = OAuthFilter(verify_ssl=False)

@_app.route("/")
def default():
    return "up"

@_app.route("/hello_world", methods=["OPTIONS"])
def hello_world_options():
    response = make_response()

    if request.headers.get("Origin", None):
        response.headers['Access-Control-Allow-Origin'] = request.headers["Origin"]
        response.headers['Access-Control-Allow-Methods'] = "GET, HEAD, OPTIONS"
        response.headers['Access-Control-Allow-Headers'] = "Authorization, WWW-Authenticate"
        #response.headers['Access-Control-Max-Age'] = "3000"
        response.headers["Access-Control-Allow-Credentials"] = "true"

    response.headers["Allow"] = "GET, HEAD, OPTIONS"

    return response

@_app.route('/hello_world', methods=['GET', 'HEAD'])
@_refOauth.protect([""])
def hello_world():
    response = make_response(json.dumps(dict(hello=g.user, scope=g.scope)))

    if request.headers.get("Origin", None):
        response.headers["Access-Control-Allow-Origin"] = request.headers["Origin"]
        response.headers["Access-Control-Allow-Credentials"] = "true"

    response.headers["x-fapi-interaction-id"] = request.headers.get("x-fapi-interaction-id", "E990656F-2C08-4B98-8FDD-BE7D7D9625FD")

    return response

# @_app.route('/hello-jwt')
# @_jwtOauth.protect(["openid"])
# def hello_jwt():
#     return json.dumps(dict(hello=g.user))

tokenServiceBaseUrl = "https://localhost:8443"
tokenServiceIssuer = tokenServiceBaseUrl + "/dev/oauth/anonymous"

_refOauth.configure_with_opaque(tokenServiceBaseUrl + "/introspection", "test_gateway_client", "secret")
#_jwtOauth.configure_with_jwt(tokenServiceIssuer + "/jwks", tokenServiceIssuer, "back-end-api", ["openid"])
#_jwtOauth.configure_with_multiple_jwt_issuers(["https://localhost:8443/oauth/%d/~" % i for i in range(1, 5)], "back-end-api", ["openid"])

if __name__ == "__main__":
    _app.run('0.0.0.0', debug=False, port=5555)