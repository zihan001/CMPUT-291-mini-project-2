from pymongo import MongoClient
import json
import os
import operator


def SearchArticles(collection):


    user_input = input("Keywords: ")

    #collection.create_index([('title', 'text'),('authors', 'text'), ('abstract', 'text'), ('venue', 'text'), ('year', 'text')],name='Article_index')
    user_input = " ".join(f'"{w}"' for w in user_input.split())

    result = collection.find({"$text": {"$search": user_input} }, {"_id":0, "id":1, "title":1, "year":1, "venue":1})[:]
    field_list = ["id","title","year","venue"]
    result_list = []
    count = 1
    # print every article
    for i in result:
        print("Article ", count)
        for p in field_list:
            if (p in i):
                print(p+": ", i[p])
            else:
                print(p+": null")
        print()
        result_list.append(i)
        count += 1

    print()
    # selecting an article
    try:
        selection = int(input("Select Article: "))
        assert selection < len(result_list)+1
        assert selection > 0
    except:
        print("Not a number or in range")
        return

    # print detailed article view
    field_list = ["id","abstract","authors","title","year","venue"]
    article_searched = list(collection.find({"id": result_list[selection - 1]["id"]}))[0]
    print("Article ", selection)
    for p in field_list:
        if (p in article_searched):
            print(p+": ", article_searched[p])
        else:
            print(p+": null")
    print()
    print()
    print("Referenced By:")
    references = list(collection.find({"references": article_searched["id"]}))

    field_list = ["id","title","year"]

    # print references
    for i in range(len(references)):
        print("Reference ", i+1)
        for p in field_list:
            if (p in references[i]):
                print(p+": ", references[i][p])
            else:
                print(p+": null")
        print()



def searchauthors():
    global dblp

    done = False
    # input loop
    while not done:
        keyword = input("Please enter keyword: ")
        if len(keyword.split()) == 1:
            keyword = keyword.split()[0]
            done = True
        else:
            print("Please provide only 1 keyword")

    # find authors and how many articles published
    results = dblp.aggregate([
        {
            "$match": {"$text": {"$search": keyword} }
        },
        {
            "$unwind": "$authors" 
        },
        {
            "$match": {"authors": {"$regex": keyword, "$options": "i"}}
        },
        {
            "$group": {
                "_id": {"author": "$authors", }, "count": {"$sum": 1}
            }
        }
    ])

    print("-----------------------------------")
    print("Authors:")
    yes = False
    for result in results:
        print("Name: " +str(result["_id"]["author"]) + " | Articles Published: " + str(result["count"]))
        #print(result)
        yes = True

    # SEARCH MATCHING IS CASE INSENSATIVE, SELECTING AN AUTHOR ISN'T :)
    if yes:
        print("-----------------------------------")
        keyword2 = input("Please enter full name of author (selection is case-sensative): ")

        results = dblp.aggregate([
        {
            "$match": {"$text": {"$search": keyword2} }
        },
        {
            "$unwind": "$authors" 
        },
        {
            "$match": {"authors": keyword2}
        },
        {
            "$project": {"_id": 0, "title": {"$ifNull": ["$title", ""]}, "year": {"$ifNull": ["$year", ""]},"venue": {"$ifNull": ["$venue", ""] }} # "venue": {"$ifNull": ["$venue": ""]
        },
        {
            "$sort": {"year": -1}
        }
        ])

        print("-----------------------------------")
        print(str(keyword2)+"'s Articles")
        for result in results:
            print("Title: " +str(result["title"])+ " | Year: " +str(result["year"])+ " | Venue: " +str(result["venue"]))
    else:
        print("No names match that keyword.")


def listVenues():
    global dblp

    # input loop
    done = False
    while not done:
        try:
            venc = int(input("Enter number n to view top n venues: "))
            if venc > 0:
                done = True
            else:
                print("Invalid Input")
        except:
            print("Invalid Input")

    # find all distinct venues
    result = dblp.distinct('venue')
    test = {}
    test2 = {}
    # for each venue find it's distinct ids
    for i in result:
        # filter out null and empty values
        if (i != "" and i is not None):
            test[i] = dblp.find({"venue": i}, {"_id":0,"id":1}).distinct("id")

    # for each venue find all reference count
    for i in test:
        count = dblp.count_documents({"references": {"$in": test[i]}})
        test2[i] = count

    # sort and limit
    sorted_d = dict( sorted(test2.items(), key=operator.itemgetter(1),reverse=True)[:venc])

    # count how many articles published in venue
    results2 = dblp.aggregate([
        {
            "$group": {"_id": {"venue": "$venue"}, "count": {"$sum": 1}}
        }
    ])
    articlecount = {}
    for result in results2:
        articlecount[result["_id"]["venue"]] = result["count"]

    # print out info
    for i in sorted_d:
        print("Venue: "+str(i) +" | Article's in venue: "+ str(articlecount[i]) +" | Articles referencing venue: "+ str(sorted_d[i]))


def addArticle():
    global dblp

    # make sure unique id is entered
    done = False
    while not done:
        newid = input("Please enter new ID: ")

        res = list(dblp.find({"id":newid}))
        if len(res) == 0:
            done = True
    # new title
    newtitle = input("Please enter a Title: ")

    # keep adding authors until user types 'done'
    done = False
    newauthors = []
    while not done:
        newauthor = input("Please enter an author or type 'done' to stop adding authors: ")
        if newauthor.lower() != "done":
            newauthors.append(newauthor)
            print("Author added!")
            print(newauthors)
        else:
            done = True

    # new year
    newyear = input("Please enter a year: ")
    # add the article
    #dblp.insert_one({"abstract": None,"authors": newauthors, "n_citation": 0,"references": [],"title": newtitle, "venue": None,"year": newyear,"id": newid})
    res = dblp.insert_one({"authors": newauthors, "n_citation": 0,"title": newtitle,"year": newyear,"id": newid})
    print("Article added!")


def seloptions():
    global dblp
    done = False
    while not done:
        print("-----------------------------------")
        print("Select an action")
        print("1: search for articles")
        print("2: search for authors")
        print("3: list the venues")
        print("4: add an article")
        print("5: exit")
        userin = input("Please enter an option (1-5): ")
        print("-----------------------------------")

        if userin == '1':
            SearchArticles(dblp)
        elif userin == '2':
            searchauthors()
        elif userin == '3':
            listVenues()
        elif userin == '4':
            addArticle()
        elif userin == '5':
            print("Exiting...")
            done = True
        else:
            print("Invalid Input.")



def main():
    global db, dblp

    portno = input("Please enter port number: ")

    client = MongoClient("mongodb://localhost:"+portno)

    db = client["291db"]
    dblp = db["dblp"]

    seloptions()


if __name__ == "__main__":
    main()