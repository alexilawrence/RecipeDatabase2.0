import pymongo
import sys
'''import flask
from flask import url_for, request
'''
client = pymongo.MongoClient('mongodb+srv://alexilawrence:mongoPW@cluster0.6im0d.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

db = client.myDatabase
coll = db.get_collection('recipes')

#0'''
finished = False

while finished == False:
    reply = str(input("enter your recipe name, or 0 if you are done. "))
    if reply == "0":
        finished = True
        print("printing the contents of the database: ")
        result = coll.find()
        for doc in result:
            print(doc)
        
        
    else:
        recipeName = reply
        ingredients = ''
        done = False
        while done == False:
            print("Ingredients added: \n" + ingredients)
            ingredient = str(input("enter the ingredient as 'quantity | ingredient', or 0 if done. "))
            if ingredient == "0":
                done = True
            else:
                if ingredients == '':
                    ingredients =  ingredient + '\n'
                else: 
                    ingredients += ingredient + '\n'
                    
        quantities = []
        components = []
        
        ingredients = ingredients[:-1] #remove the last \n
        for i in ingredients.split(sep='\n'):
            print(i)
            splitted = i.split(sep="|")
            print(splitted)
            quantities.append(splitted[0].strip())
            components.append(splitted[1].strip())
            
        coll.insert_one({'recipleName':recipeName, 'quantities':quantities, 'components':components})
        print("Successfully inserted the recipe: " + recipeName +'! ')
        
            
#              '''      


#db.drop_collection('recipes')