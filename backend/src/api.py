import os
import sys

from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, raise_error, ERR, CODE, abort_error

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()


# Get all drinks
@app.route('/', methods=['GET'])
def index():
    return "Open for business!"


# Get basic drink details
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()
        short_drinks = [drink.short() for drink in drinks]

        response = {
            "Success": True,
            "drinks": short_drinks
        }

        return jsonify(response), CODE["200_OK"]

    except:
        print(sys.exc_info())
        abort_error(CODE["500_INTERNAL_SERVER_ERROR"])


# Get full drink details
@app.route('/drinks-detail', methods=["GET"])
# @requires_auth('get:drinks-detail')
def get_drinks_detail():
    try:
        drinks = Drink.query.all()
        long_drinks = [drink.long() for drink in drinks]

        response = {
            "Success": True,
            "drinks": long_drinks
        }

        return jsonify(response), CODE["200_OK"]

    except:
        print(sys.exc_info())
        abort_error(CODE["500_INTERNAL_SERVER_ERROR"])


# POST a new drink
@app.route("/drinks", methods=["POST"])
def post_drink():
    try:
        body = request.get_json()

        if "title" not in body or "recipe" not in body:
            abort_error(CODE["422_UNPROCESSABLE_ENTITY"])

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
            "message": "Drink successfully created.",
        }

        return jsonify(response), CODE["200_OK"]

    except:
        print(sys.exc_info())
        abort_error(CODE["500_INTERNAL_SERVER_ERROR"])


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# Error Handling
@app.errorhandler(CODE["400_BAD_REQUEST"])
def bad_request(error):
    print(error)

    return jsonify({
        "success": False,
        "error": CODE["400_BAD_REQUEST"],
        "message": "Bad request",
    }), CODE["400_BAD_REQUEST"]


@app.errorhandler(CODE["404_RESOURCE_NOT_FOUND"])
def resource_not_found(error):
    print(error)

    return jsonify({
        "success": False,
        "error": CODE["404_RESOURCE_NOT_FOUND"],
        "message": "Resource not found",
    }), CODE["404_RESOURCE_NOT_FOUND"]


@app.errorhandler(CODE["405_METHOD_NOT_ALLOWED"])
def resource_not_found(error):
    print(error)

    return jsonify({
        "success": False,
        "error": CODE["405_METHOD_NOT_ALLOWED"],
        "message": "Method not allowed",
    }), CODE["405_METHOD_NOT_ALLOWED"]


@app.errorhandler(CODE["422_UNPROCESSABLE_ENTITY"])
def unprocessable_entity(error):
    print(error)

    return jsonify({
        "success": False,
        "error": CODE["422_UNPROCESSABLE_ENTITY"],
        "message": "Unprocessable entity",
    }), CODE["422_UNPROCESSABLE_ENTITY"]


@app.errorhandler(CODE["500_INTERNAL_SERVER_ERROR"])
def internal_server_error(error):
    print(error)

    return jsonify({
        "success": False,
        "error": CODE["500_INTERNAL_SERVER_ERROR"],
        "message": "Internal server error",
    }), CODE["500_INTERNAL_SERVER_ERROR"]


@app.errorhandler(AuthError)
def auth_error(exception):
    print(exception)

    response = jsonify(exception.error)
    response.status_code = exception.status_code
    return response
