from crypt import methods
import os
# from turtle import title
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys


from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks",methods=["GET"])
# @requires_auth("get:drinks")
def get_drinks():

    req_drinks = Drink.query.all()
    drinks = [drink.short() for drink in req_drinks]

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": drinks})
          
'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drinks_detail(payload):
    
    req_drinks = Drink.query.all()
    drinks = [drink.long() for drink in req_drinks]

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": drinks})
     
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def add_drinks(payload):

    body = request.get_json()

    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)

    try:
        new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        new_drink.insert()

        req_drink = Drink.query.filter(Drink.title == new_title).one()
        
        return jsonify({
           "success": True,
           "drinks": [req_drink.long()]})
    except:
        abort(422)       
        

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

@app.route("/drinks/<id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drinks(payload, id):
    body = request.get_json()
    patch_drink = Drink.query.filter(Drink.id == id).one_or_none()

    if patch_drink is None:
        abort(404)

    try:
        if "title" in body:
           patch_drink.title = body.get("title", None)

        if "recipe" in body:    
           patch_drink.recipe = body.get("recipe", None)
    
        patch_drink.update()

        return jsonify({
           "success": True,
           "drinks": [patch_drink.long()]})
    except:
        abort(422)    

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

@app.route("/drinks/<id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drinks(payload,id):

    try:
        delete_drink = Drink.query.filter(Drink.id == id).one_or_none()

        if delete_drink is None:
          abort(404)

        delete_drink.delete()

        return jsonify({
           "success": True,
           "delete": id})
    except:
        abort(422)    


# Error Handling
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

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500

@app.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
