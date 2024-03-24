import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from src.elastic import ElasticClient
from flask import Flask, request,render_template,make_response
from flask_restx import Api, Resource, fields
import logging

app = Flask(__name__)

env_path = "./src/.env"
load_dotenv(env_path)

api = Api(app)
nsCourse = api.namespace("/pyacademy", "CRUD operations for Courses")

courseInsert = api.model(
    "CourseInsert",
    {
        "courseName": fields.String(required=True, description="Course Name"),
        "courseId": fields.String(required=True, description="Course's Unique ID"),
        "duration": fields.Integer(required=True, description="Course Price"),
        "description": fields.String(required=False, description="Description of course"),
        "author": fields.String(required=True, description="Course Author"),
        "url" : fields.String(required=True, description="Url of the Course")
    },
)

course = api.model(
    "Course",
    {
        "id": fields.String(required=True, description="Course's system generated Id"),
        "courseName": fields.String(required=True, description="Course Name"),
        "courseId": fields.String(required=True, description="Course's Unique ID"),
        "duration": fields.Integer(required=True, description="Course Price"),
        "description": fields.String(required=False, description="Description of course"),
        "author": fields.String(required=True, description="Course Author"),
        "url" : fields.String(required=True, description="Url of the Course"),
        "createdAt" : fields.String(required=True, description="Time course is created")
    },
)

@nsCourse.route("/courses")
class Courses(Resource):
    # tag::post[]
    @nsCourse.doc(
        "Create Course",
        reponses={201: "Created", 500: "Unexpected Error"},
    )
    @nsCourse.expect(courseInsert, validate=True)
    @nsCourse.marshal_with(course)
    def post(self):
        try:
            logger.info("Creating Course")
            data = request.json
            id = uuid.uuid4().__str__()
            data["id"] = id
            data["createdAt"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            es.insert(data)
            logger.info("Created Course Successfully")
            return data, 201
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return f"Unexpected error: {e}", 500

@nsCourse.route("/home")
class CourseHome(Resource):
    @nsCourse.doc(
        "Home Page",
        reponses={200: "Success", 404: "Not Found", 500: "Unexpected Error"},
    )
    def get(self):
        logger.info("Rendering the Home Page")
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('home.html'), 200,headers)

    def post(self):
        logger.info("Searching for the requested course")
        courseName = request.form['courseName']
        logger.info(courseName)
        data = es.search(courseName)
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('result.html',data=data), 200, headers)

db_info = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("PORT"),
    "index": os.getenv("INDEX"),
    "username": os.getenv("USERNAME"),
    "password": os.getenv("PASSWORD"),
}

format = '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s'
logging.basicConfig(filename="./logs/audit.log",filemode='a',format=format,datefmt='%H:%M:%S',level = logging.DEBUG)
logger = logging.getLogger()
es = ElasticClient(*db_info.values(),logger)
es.connect()

if __name__ == "__main__":
    logger.debug("Application Started ...")
    app.run(debug=True,port=5000)