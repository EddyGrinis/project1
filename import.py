import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

os.environ['DATABASE_URL']='postgres://vwzakfsxqwyeor:1918223b661965c1a6b1967f93bf879dee2f458d249c6c9ccb9ec6d179c7f31a@ec2-54-247-169-129.eu-west-1.compute.amazonaws.com:5432/d7l23edpbnjkl3'

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f=open("books.csv")
    reader =csv.reader(f)
    for isbn, title, author, year in reader:
        if year == "year":
            print('skipped first line')
        else:
            db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:a,:b,:c,:d)",{"a":isbn,"b":title,"c":author,"d":year})
    db.commit()

if __name__=="__main__":
    main()
