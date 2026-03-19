import pymongo
client = pymongo.MongoClient("mongodb://localhost:27017")
for dbname in client.list_database_names():
    db = client[dbname]
    if "logs" in db.list_collection_names():
        count = db["logs"].count_documents({})
        print(f"DB: {dbname!r}  ->  logs: {count} docs")
        db["logs"].drop()
        print(f"  CLEARED.")
client.close()
print("All clear.")
