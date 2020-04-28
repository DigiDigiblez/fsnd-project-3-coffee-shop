import json
import sys

from flask import Flask, request, jsonify, abort
from flask_cors import CORS

from .auth.auth import AuthError, RESPONSE_CODE, requires_auth
from .database.models import db_drop_and_create_all, setup_db, Drink

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()


# Get all drinks
@app.route("/", methods=["GET"])
def index():
    return "Open for business!"


# Get basic drink details
@app.route("/drinks", methods=["GET"])
def get_drinks():
    try:
        drinks = Drink.query.all()
        short_drinks = [drink.short() for drink in drinks]

        response = {
            "Success": True,
            "drinks": short_drinks
        }

        return jsonify(response), RESPONSE_CODE["200_OK"]

    except:
        print(sys.exc_info())
        abort(RESPONSE_CODE["500_INTERNAL_SERVER_ERROR"])


# Get full drink details
@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drinks_detail(jwt):
    try:
        drinks = Drink.query.all()
        long_drinks = [drink.long() for drink in drinks]

        response = {
            "Success": True,
            "drinks": long_drinks
        }

        return jsonify(response), RESPONSE_CODE["200_OK"]

    except:
        print(sys.exc_info())
        abort(RESPONSE_CODE["500_INTERNAL_SERVER_ERROR"])


# POST a new drink
@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def post_drink(jwt):
    body = request.get_json()

    if "title" not in body or "recipe" not in body:
        abort(RESPONSE_CODE["422_UNPROCESSABLE_ENTITY"])

    drink_title = body.get("title", None)
    drink_recipe = body.get("recipe", None)

    # Instantiate new drink
    new_drink = Drink(
        title=drink_title,
        recipe=json.dumps(drink_recipe)
    )

    # Add new drink to db
    new_drink.insert()

    response = {
        "success": True,
        "drinks": [new_drink.short()],
    }

    return jsonify(response), RESPONSE_CODE["200_OK"]


# Update a drink
@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def patch_drink(jwt, drink_id):
    try:
        # Error handling for id
        drink_count = len(Drink.query.all())
        if drink_id is None or drink_id <= 0 or drink_id > drink_count:
            abort(RESPONSE_CODE["404_RESOURCE_NOT_FOUND"])

        # Error handling for existing drink
        existing_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if existing_drink is None:
            abort(RESPONSE_CODE["404_RESOURCE_NOT_FOUND"])

        # Retrieving values for updating
        body = request.get_json()

        # Check if body contains any data
        if body is not False:
            drink_new_title = ""
            drink_new_recipe = ""

            # Retrieve and update the existing record with new data if provided
            if "title" in body:
                drink_new_title = body.get("title")
                existing_drink.title = drink_new_title
            if "recipe" in body:
                drink_new_recipe = body.get("recipe")
                existing_drink.recipe = json.dumps(drink_new_recipe)

            # Update record only if it's data has changed
            if existing_drink.title == drink_new_title or \
                    existing_drink.recipe == json.dumps(drink_new_recipe):
                existing_drink.update()

        response = {
            "success": True,
            "drinks": [existing_drink.long()],
        }

        return jsonify(response), RESPONSE_CODE["200_OK"]

    except:
        print(sys.exc_info())
        abort(RESPONSE_CODE["500_INTERNAL_SERVER_ERROR"])


# Delete a drink
@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(jwt, drink_id):
    drink_count = len(Drink.query.all())

    if drink_id is None or drink_id <= 0 or drink_id > drink_count:
        abort(RESPONSE_CODE["404_RESOURCE_NOT_FOUND"])

    target_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if target_drink is None:
        abort(RESPONSE_CODE["404_RESOURCE_NOT_FOUND"])

    target_drink.delete()

    response = {
        "success": True,
        "delete": drink_id,
    }

    return jsonify(response), RESPONSE_CODE["200_OK"]


# Error Handling
@app.errorhandler(RESPONSE_CODE["400_BAD_REQUEST"])
def bad_request(error):
    print(error)

    return jsonify({
        "success": False,
        "error": RESPONSE_CODE["400_BAD_REQUEST"],
        "message": "Bad request",
    }), RESPONSE_CODE["400_BAD_REQUEST"]


@app.errorhandler(RESPONSE_CODE["404_RESOURCE_NOT_FOUND"])
def resource_not_found(error):
    print(error)

    return jsonify({
        "success": False,
        "error": RESPONSE_CODE["404_RESOURCE_NOT_FOUND"],
        "message": "Resource not found",
    }), RESPONSE_CODE["404_RESOURCE_NOT_FOUND"]


@app.errorhandler(RESPONSE_CODE["405_METHOD_NOT_ALLOWED"])
def resource_not_found(error):
    print(error)

    return jsonify({
        "success": False,
        "error": RESPONSE_CODE["405_METHOD_NOT_ALLOWED"],
        "message": "Method not allowed",
    }), RESPONSE_CODE["405_METHOD_NOT_ALLOWED"]


@app.errorhandler(RESPONSE_CODE["422_UNPROCESSABLE_ENTITY"])
def unprocessable_entity(error):
    print(error)

    return jsonify({
        "success": False,
        "error": RESPONSE_CODE["422_UNPROCESSABLE_ENTITY"],
        "message": "Unprocessable entity",
    }), RESPONSE_CODE["422_UNPROCESSABLE_ENTITY"]


@app.errorhandler(RESPONSE_CODE["500_INTERNAL_SERVER_ERROR"])
def internal_server_error(error):
    print(error)

    return jsonify({
        "success": False,
        "error": RESPONSE_CODE["500_INTERNAL_SERVER_ERROR"],
        "message": "Internal server error",
    }), RESPONSE_CODE["500_INTERNAL_SERVER_ERROR"]


@app.errorhandler(AuthError)
def auth_error(exception):
    print(exception)

    response = jsonify(exception.error)
    response.status_code = exception.status_code
    return response
