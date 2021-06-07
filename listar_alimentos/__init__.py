import logging
import jsonschema
import json
from ..SharedCode.mongo import mongoUtils

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    
    STATUS_CODE = 200

    try:
        
        response = mongoUtils.execFind(
            database='maissaude', 
            collection='alimentos'
        )
        
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