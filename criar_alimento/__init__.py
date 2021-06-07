import logging
import jsonschema
import json
from ..SharedCode.mongo import mongoUtils

import azure.functions as func


BODY_VALIDATION = {
        "title": "Request",
        "type": "object",
        "required": ["Nome", "Calorias"],
        "properties": {
            "Nome": {
                "type": "string"
            },
            "Calorias": {
                "type": "integer"
            }
        }
    }

def main(req: func.HttpRequest) -> func.HttpResponse:
    
    STATUS_CODE = 200

    try:

        req_body = req.get_json()

        jsonschema.validate(req_body, BODY_VALIDATION)

        mongoUtils.insertDocument(
            database='maissaude',
            collection="alimentos",
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