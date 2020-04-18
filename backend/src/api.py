import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
from .auth.auth import get_token_auth_header,verify_decode_jwt , check_permissions

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TOTO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
'''
@TOTO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks' , methods=['GET'])
def get_drinks():
    allDrinks = Drink.query.all()
    print("🍦🍦🍦🍦🍦🍦{}".format(len(allDrinks)))
    shortDrinks = [drink.short() for drink in allDrinks]
    return jsonify({
        "sucess":True , 
        "drinks":shortDrinks
    }) , 200

'''
@TOTO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail' , methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    print ('🍎🍎🍎🍎🍎🍎🍎')
    allDrinks = Drink.query.all()
    formattedDrinks = [drink.long() for drink in allDrinks] 
    return jsonify({
        "success":True , 
        "drinks":formattedDrinks
    }) ,200

'''
@TOTO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks' , methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    body = request.get_json()
    drink = Drink()
    drink.title = body.get('title')
    drink.recipe = body.get('recipe')
    drink.insert()
    return jsonify({
        "success":True  , 
        "drinks":drink.long()
    }) , 200

'''
@TOTO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(drink_id , payload):
    body = request.get_json()
    drink = Drink.query.get(drink_id)
    if drink == None:
        abort(404)
    drink.id = drink_id 
    drink.title = body.get('title')
    drink.recipe = body.get('recipe')
    drink.update()
    return jsonify({
        "success":True , 
        "drinks":drink.long()
    }),200

'''
@TOTO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>',methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(drink_id,payload):
    drink = Drink.query.get(drink_id)
    if drink == None:
        abort(404)
    drink.delete()
    return jsonify({
        "success":True , 
        "delete":drink_id
        }) , 200
    

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
@TOTO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
'''
@TOTO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success":False , 
        "error":404 , 
        "message":"Page not found"
    }) , 404


token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImxBTVdfVmxZRmRMeXlVS0xubkdrZiJ9.eyJpc3MiOiJodHRwczovL2FuZGFsdXNzb2Z0LmF1LmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZTlhNDM2NjA1Yjg3NzBiZTc3ZGExMTMiLCJhdWQiOiJjb2ZmZWVfc2hvcF9hcGkiLCJpYXQiOjE1ODcxNzQ1ODgsImV4cCI6MTU4NzE4MTc4OCwiYXpwIjoiTG1sR29xZlI0SG5FbUYzMnZmbUFzOGVVdVF6ODZQbjIiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImdldDpkcmlua3MtZGV0YWlsIl19.p36Gsh7KCTl_vHjfJtUlEdLRHhbelHww4fNFdmaBZ5e_WqU0a7xq3tJL3f0Xx3xBRjGyOTiZ53U5VLc_qHakFPnwaxkrRdPCIfZGpH8x1tjMQPxZSX2DbcxBOqR5IXPM871FFxlr3nTZ8XjUH2de1HE3ES8rtFXXebiXQsqXU8stHwGBGSB0Fh_gpWRhnaXUr511jxe3mejSmXrQx9U4mIE6Ql9Lrb03bltBG0xx5tgvuNqDN1BNKh1ZLeJtvtupZFj9mxvU-y-Cesx3UclI2Cb9Axs9ouAjCijIVhO-xJlfBDAcTq_BK_FeUobVru_TVJ_ihDylhxG0Vn0uKBGfeg'
@app.route('/temp' , methods=['GET'])
@requires_auth('delete:drinks')
def temp(payload):
    #x = check_permissions()
    
   # x = get_token_auth_header()
    return jsonify({"success":True})
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
