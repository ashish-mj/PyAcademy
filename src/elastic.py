from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError,RequestError,TransportError

class ElasticClient:
    def __init__(self, host, port,index, username, password,logger):
        self.client = None
        self.host = host
        self.port = port
        self.index = index
        self.username = username
        self.password = password
        self.logger = logger

    def connect(self, **kwargs):
        try:
            self.logger.debug("Connecting to Elastic DB")
            connection_str = self.host+":"+self.port
            self.client = Elasticsearch([connection_str],basic_auth=(self.username, self.password),verify_certs=False)
            self.logger.info("Connection to Elastic DB Successfull")

        except ConnectionError as error:
            self.logger.error("Connection to Elastic DB Failed",exc_info=True)

    def search(self,word):
        query = {
            "query": {
                "match": {
                    "courseName": word
                }
            }
        }
        try:
            self.logger.info("Searching for the word "+word)
            result = self.client.search(index=self.index, body=query)
            self.logger.info("Searching for the word " + word+ " is Successfull")
            self.logger.info(result["hits"]["hits"])
            return result["hits"]["hits"]
        except RequestError:
            self.logger.error("Invalid Query",exc_info=True)

    def insert(self,document):
        try:
            self.logger.info("Indexing the document")
            self.logger.info(document)
            res = self.client.index(index=self.index,id=document["courseId"],body=document)
            self.logger.info("Indexing the document Successfull")
            self.logger.info(res)
        except TransportError:
            self.logger.error("Indexing Error",exc_info=True)