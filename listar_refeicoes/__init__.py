import logging
import jsonschema
import json
from ..SharedCode.mongo import mongoUtils
import datetime
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

        week_ago = datetime.datetime.now() - datetime.timedelta(days=7)

        data = mongoUtils.execFind(
            database='maissaude', 
            collection='refeicoes',
            datafilter={"user_id" : user_id, "date" : {"$gte" : week_ago}}
        )

        logging.warn(data)

        meals = []
        dayCalories = 0
        yesterdayCalories = 0
        weekCalories = 0
        weekInfo = {
            'sunday'    : 0,
            'monday'    : 0,
            'tuesday'   : 0,
            'wednesday' : 0,
            'thursday'  : 0,
            'friday'    : 0,
            'saturday'  : 0
        }

        
        for item in data:
            meal = {}
            meal['title'] = item['tipo_refeicao'] + ' ' + item['data_refeicao']
            meal['time'] = {
                "value": item['hora_refeicao'],
                "label": "Horário"
            }

            foods = []
            kcal = 0

            for food in item['alimentos']:
                logging.warn(food)
                foods.append(food['Nome'])
                kcal += food['Calorias']

            meal['caloriesConsumed'] = {
                "value": f'{kcal} Kcal',
                "label": 'Kcal consumidas'
            }
            meal['foods'] = {
            "value": ",".join(foods),
            "label": 'Alimentos consumidos'
            }

            meals.append(meal)

            if item['date'].date() == datetime.datetime.now().date(): dayCalories += kcal
            if item['date'].date() == (datetime.datetime.now() - datetime.timedelta(days=1)).date(): yesterdayCalories += kcal
            if item['date'].date() > (datetime.datetime.now() - datetime.timedelta(days=7)).date(): weekCalories += kcal
            if item['date'].weekday() == 0: weekInfo['monday'] += kcal
            if item['date'].weekday() == 1: weekInfo['tuesday'] += kcal
            if item['date'].weekday() == 2: weekInfo['wednesday'] += kcal
            if item['date'].weekday() == 3: weekInfo['thursday'] += kcal
            if item['date'].weekday() == 4: weekInfo['friday'] += kcal
            if item['date'].weekday() == 5: weekInfo['saturday'] += kcal
            if item['date'].weekday() == 6: weekInfo['sunday'] += kcal



        caloriesPercent = round((dayCalories/2500)*100,2) if dayCalories > 0 else 0
        weekCalories = round(weekCalories/len(data)) if len(data) > 0 else 0
        summary = {
            "title": 'Acompanhamento',
            "caloriesConsumed": {
                "value": f'{dayCalories} Kcal',
                "label": 'Kcal consumidas'
            },
            "caloriesTarget": {
                "value": '2500 Kcal',
                "label": 'Meta Kcal'
            },
            "caloriesPercent": {
                "value": f'{caloriesPercent}%',
                "label": '% Kcal consumida'
            },
            "yesterday": {
                "value": f'{yesterdayCalories} Kcal',
                "label": 'Ontem'
            },
            "averageWeek": {
                "value": f'{weekCalories} Kcal',
                "label": 'Média semana'
            },
            "weekInfo" : weekInfo
        }
        
        response = {
            "summary"   : summary,
            "meals"     : meals

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