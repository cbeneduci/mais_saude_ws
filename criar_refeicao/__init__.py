import logging
import jsonschema
import json
from ..SharedCode.mongo import mongoUtils
from datetime import datetime

import azure.functions as func


BODY_VALIDATION = {
        "title": "Request",
        "type": "object",
        "required": ["user_id", "tipo_refeicao", "data_refeicao", "hora_refeicao", "alimentos"],
        "properties": {
            "user_id": {
                "type": "string"
            },
            "tipo_refeicao": {
                "type": "string"
            },
            "data_refeicao": {
                "type": "string"
            },
            "hora_refeicao": {
                "type": "string"
            },
            "alimentos": {
                "type": "array"
            }
        }
    }

def main(req: func.HttpRequest) -> func.HttpResponse:
    
    STATUS_CODE = 200

    try:

        req_body = req.get_json()

        jsonschema.validate(req_body, BODY_VALIDATION)

        req_body['date'] = datetime. strptime(req_body['data_refeicao'], '%d/%m/%Y')

        mongoUtils.insertDocument(
            database='maissaude',
            collection="refeicoes",
            document=req_body
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