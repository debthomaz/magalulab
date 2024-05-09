from flask import Flask, jsonify
from flask_restful import Api, abort, request
from flask_mysqldb import MySQL
from config import config
from functools import wraps
import requests
import jwt
import datetime

app = Flask(__name__)
api = Api(app)
mysql = MySQL()
mysql.init_app(app)

BASE_PRODUCTS = "http://challenge-api.luizalabs.com/api/product/"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({"message": "O token é necessário para requisição."}), 403
        try:
            data = jwt.decode(token, options={"verify_signature": False})
            print(data)
        except:
            return jsonify({"message": "O token é inválido."}), 403
        return f(*args, **kwargs)
    
    return decorated

def abort_if_email_in_use(clientId, args):
    cursor = mysql.connect.cursor()
    sql = "SELECT email FROM clients WHERE clientId = '{0}'".format(clientId)
    cursor.execute(sql)
    email = cursor.fetchone()
    if email == args["email"]:
        abort(409, message="Este e-mail já está cadastrado.")


@app.route('/clients/<clientId>', methods=['GET'])
@token_required
def get_client(clientId):
    cursor = mysql.connect.cursor()
    sql = "SELECT name, email FROM clients WHERE clientId = '{0}'".format(clientId)
    cursor.execute(sql)
    client = cursor.fetchone()
    if client == None:
        return jsonify({"message": "Usuário não encontrado.", "client": clientId}), 404
    
    return jsonify(client), 200

@app.route('/clients/<clientId>', methods=['PUT'])
@token_required
def update_client(clientId):
    args = request.json
    abort_if_email_in_use(clientId, args)
    cursor = mysql.connect.cursor()
    sql = "UPDATE clients SET name = '{0}' AND email ='{1}' WHERE clientId = '{2}'".format(args["name"], args["email"], clientId)
    cursor.execute(sql)
    mysql.connect.commit()
    sql = "SELECT * FROM clients WHERE clientId = '{0}'".format(clientId)
    cursor.execute(sql)
    client = cursor.fetchone()
    if client == None:
        return jsonify({"message": "Ocorreu um erro ao criar o usuário.", "client": client}), 400
    
    return jsonify({"message": 'O usuário foi atualizado.', "client": client}), 200

@app.route('/clients/<clientId>', methods=['POST'])
@token_required
def create_client(clientId):
    args = request.json
    abort_if_email_in_use(clientId, args)
    cursor = mysql.connect.cursor()
    sql = "INSERT INTO clients (name, email) VALUES ('{0}', '{1}')".format(args["name"], args["email"])
    cursor.execute(sql)
    mysql.connect.commit()
    sql = "SELECT * FROM clients WHERE clientId = '{0}'".format(clientId)
    cursor.execute(sql)
    client = cursor.fetchone()
    if client == None:
        return jsonify({"message": "Ocorreu um erro ao criar o usuário.", "client": client}), 400
    
    return jsonify({"message": 'Usuário criado.', "client": client}), 201

@app.route('/clients/<clientId>', methods=['DELETE'])
@token_required
def delete_client(clientId):
    cursor = mysql.connect.cursor()
    sql = "DELETE FROM clients WHERE clientId = '{0}'".format(clientId)
    cursor.execute(sql)
    mysql.connect.commit()
    sql = "SELECT * FROM clients WHERE clientId = '{0}'".format(clientId)
    cursor.execute(sql)
    client = cursor.fetchall()
    if client != None:
        return jsonify({"message": "Ocorreu um erro ao deletar o usuário.", "client": client}), 400
    
    return jsonify({"message": 'Usuário deletado.'}), 204


def abort_if_product_in_wishlist(productId):
    cursor = mysql.connect.cursor()
    sql = "SELECT productId FROM wishlist WHERE productId = '{0}'".format(productId)
    cursor.execute(sql)
    product = cursor.fetchone()
    if product != None:
        abort(409, message="Este produto já está em sua lista de favoritos.")

def abort_if_product_not_in_wishlist(productId):
    cursor = mysql.connect.cursor()
    sql = "SELECT productId FROM wishlist WHERE productId = '{0}'".format(productId)
    cursor.execute(sql)
    product = cursor.fetchone()
    if product == None:
        abort(404, message="Produto não está em sua lista de favoritos.")



@app.route('/clients/<clientId>/wishlist', methods=['GET'])
@token_required
def get_wishlist(clientId):
    cursor = mysql.connect.cursor()
    sql = "SELECT * FROM wishlist WHERE clientId = '{0}'".format(clientId)
    cursor.execute(sql)
    wishlist = cursor.fetchall()
    product = ""
    products = []
    try:
        for i in range(len(wishlist)):
            productId = wishlist[i][2]
            product = requests.get(BASE_PRODUCTS + str(productId))
        products = products.append(product)
        if products == None:
            return jsonify({"message": "Os produtos não foram encontrados na base da Magalu.", "products": wishlist[:][2]}), 404
        return str(products), 200
    except:
        return jsonify({"message": "Houve um erro ao fazer a requisição."}), 400

@app.route('/clients/<clientId>/wishlist/<productId>', methods=['POST'])
@token_required
def add_product(clientId, productId):
    abort_if_product_in_wishlist(productId)
    cursor = mysql.connect.cursor()
    sql = "INSERT INTO wishlist (clientId, productId) VALUES ('{0}', '{1}')".format(clientId, productId)
    cursor.execute(sql)
    mysql.connect.commit()
    sql = "SELECT * FROM wishlist WHERE clientId = '{0}' AND productId = '{1}'".format(clientId, productId)
    cursor.execute(sql)
    product = cursor.fetchone()
    if product == None:
        return jsonify({"message": "Ocorreu um erro ao adicionar o produto na lista de favoritos.", "product": product}), 400
    
    return jsonify({"message": 'Produto adicionado à lista de favoritos.', "product": product}), 201

@app.route('/clients/<clientId>/wishlist/<productId>', methods=['DELETE'])
@token_required
def delete_product(clientId, productId):
    abort_if_product_not_in_wishlist(productId)
    cursor = mysql.connect.cursor()
    sql = "DELETE FROM wishlist WHERE productId = '{0}' AND clientId = '{1}'".format(productId, clientId)
    cursor.execute(sql)
    mysql.connect.commit()
    sql = "SELECT * FROM wishlist WHERE clientId = '{0}'".format(clientId)
    cursor.execute(sql)
    product = cursor.fetchall()
    if product == None:
        return jsonify({"message": "Ocorreu um erro ao deletar o produto da lista de favoritos.", "product": product}), 404
    
    return jsonify({"message": 'Produto deletado da lista de favoritos.', "product": product}), 204

@app.route('/token')
def get_token():
    key = app.config['SECRET_KEY']
    token = jwt.encode({"user": "magalu", "exp": datetime.datetime.now() + datetime.timedelta(minutes=30)}, key)
    return jsonify({"token": token})

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()
