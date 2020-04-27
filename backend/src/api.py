import os
import sys

from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, raise_error, ERR, CODE

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

    except Exception as e:
        print(sys.exc_info())
        raise_error(ERR[CODE["500_INTERNAL_SERVER_ERROR"]], e)


# Get full drink details
@app.route('/drinks-details', methods=["GET"])
def get_drinks_detail():
    try:
        if 'get:drinks-detail' not in request.permissions:
            raise_error(ERR[CODE["401_UNAUTHORIZED"]], "Permission to get drinks details is not authorised")

        drinks = Drink.query.all()
        long_drinks = [drink.long() for drink in drinks]

        response = {
            "Success": True,
            "drinks": long_drinks
        }

        return jsonify(response), CODE["200_OK"]

    except Exception as e:
        print(sys.exc_info())
        raise_error(ERR[CODE["500_INTERNAL_SERVER_ERROR"]], e)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

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

## Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
