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
        
        response = mongoUtils.execFind(
            database='maissaude', 
            collection='users', 
            datafilter={"UserID": user_id},
            projection={
                "_id" : 0,
                "UserID" : 0
            }
        )

        response = response[0] if len(response) > 0 else []
        
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