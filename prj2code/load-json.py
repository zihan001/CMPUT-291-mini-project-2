from pymongo import MongoClient
import json
import os

def main():
    # user enters localhost port number
    portno = input("Please enter port number: ")

    # connect to the port inputted on localhost for the mongodb server
    client = MongoClient("mongodb://localhost:"+portno)
    # create or open the 291db database on server
    db = client["291db"]
    # create or open the collection in the db
    dblp = db["dblp"]

    # enter name of file and use mongoimport to import file to db
    filename = input("Enter name of Json file: ")
    dblp.drop_indexes()
    os.system("mongoimport --port "+portno+" --db 291db --collection dblp --drop --file " + filename)

    # converts year into a string
    dblp.update_many({},[{"$set": {"year": {"$toString": "$year"}}}])

    # creates all kinds of indexes and notifie the completion of each index
    print("Year->string completed")
    dblp.create_index("references")
    print("reference index created")
    dblp.create_index("venue")
    print("venue index created")
    dblp.create_index("id")
    print("id index created")
    dblp.create_index([("title", "text"), ("authors","text"),("abstract","text"),("venue","text"),("year","text")], name = "Article_index")
    print("text indexing created")

    print(" ############## PHASE I COMPLETE ############## ")


if __name__ == "__main__":
    main()