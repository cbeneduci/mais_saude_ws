import os
import logging



class mongoUtils():

    @staticmethod
    class __mongoDBConnection():
            
        def __init__(self, collection, database):
            self.connectionString = os.environ['CosmosDB']
            self.collection = collection
            self.database = database
        
        def __enter__(self):
            from pymongo import MongoClient

            try:
                
                self.client = MongoClient(self.connectionString)
                db = self.client[self.database]
                dbcollection = db[self.collection]

                return dbcollection

            except Exception as err:
                logging.error(err)
                return False

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.client.close() 

    @classmethod
    def execFindOne(cls, collection, database , datafilter = {}):


        with cls.__mongoDBConnection(collection, database) as dbcollection:

            data = dbcollection.find_one(datafilter)

        return data

    @classmethod
    def execFind(cls,collection, database , datafilter = {}, projection = None):

        with cls.__mongoDBConnection(collection, database) as dbcollection:
            
            data = list(dbcollection.find(filter=datafilter, projection=projection))

        return data

    @classmethod
    def insertDocument(cls,collection, document, database):

        with cls.__mongoDBConnection(collection, database) as dbcollection:

            dbcollection_id = dbcollection.insert_one(document).inserted_id

        return dbcollection_id

    @classmethod
    def updateDocument(cls,collection, datafilter, update, database, upsert = False):

        with cls.__mongoDBConnection(collection, database) as dbcollection:

            result = dbcollection.update_one(filter=datafilter, update=update, upsert=upsert)

        return result

    @classmethod
    def updateMultiDocument(cls,collection, datafilter, update,database, array_filters=None):

        with cls.__mongoDBConnection(collection, database) as dbcollection:

            result = dbcollection.update_many(filter=datafilter, update=update, array_filters=array_filters)

        return result

    @classmethod
    def bulkUpdate(cls,collection, BulkRequest, database):

        with cls.__mongoDBConnection(collection, database) as dbcollection:

            logging.debug('Executando Bulk Operation')
            result = dbcollection.bulk_write(BulkRequest)

        logging.debug('Finalizando Bulk Operation')
        return result.bulk_api_result

    @classmethod
    def execAgg(cls,collection, database, aggregation = [], allowDiskUse=False):

        with cls.__mongoDBConnection(collection, database) as dbcollection:
            
            data = list(dbcollection.aggregate(aggregation, allowDiskUse=allowDiskUse))

        return data

    @classmethod
    def truncate(cls,collection, database, datafilter={}):

        with cls.__mongoDBConnection(collection, database) as dbcollection:

            dbcollection.remove(datafilter)

