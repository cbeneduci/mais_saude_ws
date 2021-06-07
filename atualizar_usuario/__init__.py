import logging
import jsonschema
import json
from ..SharedCode.mongo import mongoUtils

import azure.functions as func


BODY_VALIDATION = {
        "title": "Request",
        "type": "object",
        "required": [ "user_id"],
        "properties": {
            "user_id": {
                "type": "string"
            }
        }
    }

def main(req: func.HttpRequest) -> func.HttpResponse:
    
    STATUS_CODE = 200

    try:

        req_body = req.get_json()

        jsonschema.validate(req_body, BODY_VALIDATION)

        user_id = req_body['user_id']

        user_info = {}

        if "Nome" in req_body: user_info['Nome'] = req_body['Nome']
        if "Sobrenome" in req_body: user_info['Sobrenome'] = req_body['Sobrenome']
        if "Nascimento" in req_body: user_info['Nascimento'] = req_body['Nascimento']
        if "Cidade" in req_body: user_info['Cidade'] = req_body['Cidade']
        if "E-mail" in req_body: user_info['E-mail'] = req_body['E-mail']
        if "Telefone" in req_body: user_info['Telefone'] = req_body['Telefone']
        if "Sexo" in req_body: user_info['Sexo'] = req_body['Sexo']
        if "Peso" in req_body: user_info['Peso'] = req_body['Peso']
        if "Altura" in req_body: user_info['Altura'] = req_body['Altura']

        mongoUtils.updateDocument(
            database='maissaude',
            collection="users",
            datafilter={"UserID": user_id},
            update={"$set" : user_info},
            upsert=True
        )
        
        response = {
            "completed" : True
        }
        
    except ValueError:
        STATUS_CODE = 400
        response = {
            "error" : "JSON inválido"
        }

    except jsonschema.exceptions.ValidationError as error:
        STATUS_CODE = 400
        response = {
            "error" : f"JSON inválido - {error.message}"
        }

    except Exception as err:
        logging.error(err)
        STATUS_CODE = 500
        response = {
            "error" : "Erro para processar o request"
        }

    finally:

        return func.HttpResponse(body=json.dumps(response, default=str), status_code=STATUS_CODE, mimetype='Aplication/json')