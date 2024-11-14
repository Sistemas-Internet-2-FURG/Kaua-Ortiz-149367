from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity, jwt_required
)
from datetime import datetime, date
from flask_cors import CORS
from bd import (
    createEnterprise, 
    getEnterprise, 
    createEmployee, 
    getEmployee,
    checkFinalPoint,
    startPoint,
    getAllPoints,
    finalPoint,
    getDayPoint,
    deletePoint,
    editPoint
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta'
app.config['JWT_SECRET_KEY'] = 'sua_chave_secreta_jwt'
jwt = JWTManager(app)
CORS(app, supports_credentials=True)

# Tratativas para erros de JWT
@jwt.unauthorized_loader
def unauthorized_callback(callback):
    return jsonify({"message": "Token não foi fornecido. Por favor, faça login para continuar."}), 401

@jwt.invalid_token_loader
def invalid_token_callback(callback):
    return jsonify({"message": "Token inválido. Por favor, faça login novamente."}), 422

@jwt.expired_token_loader
def expired_token_callback(callback, expired):
    return jsonify({"message": "O token expirou. Por favor, faça login novamente."}), 401

@jwt.revoked_token_loader
def revoked_token_callback(callback):
    return jsonify({"message": "O token foi revogado. Por favor, faça login novamente."}), 401

# Função de login para o funcionário
@app.route("/login/employee", methods=['POST'])
def loginEmployee():
    username = request.json.get('username')
    password = request.json.get('password')
    result = getEmployee(username, password)
    data = result.json

    if username == 'admin' and password == 'password':
        access_token = create_access_token(identity={'username': username})
        return jsonify(access_token=access_token), 200
    
    elif data['message'] == "success":
        access_token = create_access_token(identity={'username': username, 'id_user': data['id_user']})
        return jsonify(access_token=access_token), 200

    return jsonify({"message": "Credenciais inválidas"}), 401

@app.route("/register/employee", methods=['POST'])
def registerEmployee():
    new_username = request.json.get('new_username')
    enterprise = request.json.get('enterprise')
    position = request.json.get('position')
    new_password = request.json.get('new_password')
    confirm_password = request.json.get('confirm_password')

    if new_password == confirm_password:
        result = createEmployee(new_username, enterprise, position, new_password)
        data = result.json
        print(data)
        if data['message'] == "success":
            return jsonify({"message": "Login criado!"}), 200
        else:
            return jsonify({"message": "Credenciais inválidas"}), 401

    return jsonify({"message": "Credenciais inválidas"}), 401

# Função de login para a empresa
@app.route("/login/enterprise", methods=['POST'])
def loginEnterprise():
    company = request.json.get('company')
    password = request.json.get('password')
    result = getEnterprise(company, password)
    data = result.json

    if company == 'admin' and password == 'password':
        access_token = create_access_token(identity={'company': company})
        return jsonify(access_token=access_token), 200
    
    elif data['message'] == "success":
        access_token = create_access_token(identity={'company': company, 'id_empresa': data['id_empresa']})
        return jsonify(access_token=access_token), 200

    return jsonify({"message": data.get("message", "Credenciais inválidas")}), 401

@app.route("/register/enterprise", methods=['POST'])
def registerEnterprise():
    new_company = request.json.get('new_company')
    new_password = request.json.get('new_password')
    confirm_password = request.json.get('confirm_password')

    if new_password == confirm_password:
        result = createEnterprise(new_company, new_password)
        data = result.json
        print(data)
        if data['message'] == "success":
            return jsonify({"message": "Empresa criada"}), 200
        else:
            return jsonify({"message":"Credenciais inválidas"}), 401

    return jsonify({"message": data.get("message", "Credenciais inválidas")}), 401

# Rotas protegidas por JWT
@app.route("/dashboard/employee", methods=['POST'])
@jwt_required()
def dashboardEmployee():
    current_user = get_jwt_identity()
    result2 = checkFinalPoint(current_user['id_user'], date.today())
    data2 = result2.json

    if data2["message"] == "success":
        ponto = getDayPoint(current_user['id_user'], date.today())
        dados = ponto.json
        result4 = finalPoint(dados['id_ponto'], getDatetime())
        data4 = result4.json
        if data4['message'] == "success":
            return jsonify({"message": "Ponto de saída registrado"}), 200
    else:
        result = startPoint(current_user['id_user'], getDatetime())
        return jsonify({"message": "Ponto de entrada registrado"}), 200

    return jsonify({"message": "Erro ao processar ponto"}), 400

@app.route("/dashboard/enterprise", methods=['GET', 'POST', 'PUT', 'DELETE'])
@jwt_required()
def dashboardEnterprise():
    current_user = get_jwt_identity()
    if request.method == "GET":
        result = getAllPoints(current_user['id_empresa'])
        return jsonify(result.json), 200

    elif request.method == "PUT":
        id_ponto = request.json.get("id_ponto")
        hora_inicio = request.json.get("hora_inicio")
        hora_final = request.json.get("hora_final")

        result = editPoint(id_ponto, hora_inicio, hora_final)
        if result.json.get('message') == 'success':
            return jsonify({"message": "Ponto atualizado com sucesso"}), 200

    elif request.method == "DELETE":
        id_ponto = request.json.get("id_ponto")
        result = deletePoint(id_ponto)
        if result.json.get('message') == 'success':
            return jsonify({"message": "Ponto deletado com sucesso"}), 200

    return jsonify({"message": "Requisição inválida"}), 400

def getDatetime():
    return datetime.now()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')