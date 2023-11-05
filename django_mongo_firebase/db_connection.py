import pymongo
import os
import dotenv
dotenv.load_dotenv()

url = os.getenv('MONGO_URL')
client = pymongo.MongoClient(url)

db = client['test_mongo']