# -*- coding: utf-8 -*-
"""
"""
from __future__ import unicode_literals

import os
import sys
import json
import re
import time
from datetime import datetime

from bpdb import set_trace
import robobrowser
import cv2
import pynder

from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import Date, DateTime
from sqlalchemy import Float, ForeignKey
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
        

#MOBILE_USER_AGENT = "Mozilla/5.0 (Linux; U; en-gb; KFTHWI Build/JDQ39) AppleWebKit/535.19 (KHTML, like Gecko) Silk/3.16 Safari/535.19"


Base = declarative_base()

def get_access_token(email, password):
    #s = robobrowser.RoboBrowser(user_agent=MOBILE_USER_AGENT, parser="lxml")
    s = robobrowser.RoboBrowser(parser="lxml")
    s.open(FB_AUTH)
    ##submit login form##
    f = s.get_form()
    print(f)
    f["pass"] = password
    f["email"] = email
    s.submit_form(f)
    ##click the 'ok' button on the dialog informing you that you have already authenticated with the Tinder app##
    f = s.get_form()
    #s.submit_form(f, submit=f.submit_fields['CONFIRM'])
    s.submit_form(f)
    print(s)
    ##get access token from the html response##
    access_token = re.search(r"access_token=([\w\d]+)", s.response.content.decode()).groups()[0]
    #print s.response.content.decode()
    return access_token

def parse_token(access_dict):
    access_token = access_dict['jsmods']['require'][0][3][0].split('access_token=')[1].split('&')[0]
    return access_token




class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    bio = Column(String)
    age = Column(SmallInteger)
    birth_date = Column(Date)
    ping_time = Column(DateTime)
    distance_km = Column(Float)
    get_photos = relationship('Photo')
    schools = relationship('School')
    jobs = relationship('Job')


class Photo(Base):
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    url = Column(String)


class School(Base):
    __tablename__ = 'schools'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)



if __name__ == '__main__':
    """
    go to this page to get authentication
        - https://tinderface.herokuapp.com/
    """
    json_path = 'acc2.json'
    engine = create_engine('sqlite:///tinder.sqlite3', echo=True)
    Session = sessionmaker(bind=engine)
    sql_session = Session()
    Base.metadata.create_all(engine)


    with open(json_path, 'r') as f:
        access_dict = json.load(f)
    access_token = parse_token(access_dict)
    session = pynder.Session(access_token)
    
    for i in session.nearby_users():
        print("="*20)
        print(
                """
                name: {}
                age: {}
                bio: {}
                photos: {}
                schools: {}
                """.format(
                    i.name,
                    i.age,
                    i.bio,
                    [photo for photo in i.photos],
                    i.schools
                    )
                )
        liked = i.like()
        photos = [Photo(url=url) for url in i.get_photos(width='640')]
        schools = [School(name=name) for name in i.schools]
        jobs = [Job(name=name) for name in i.jobs]

        sql_user = User(
            name=i.name,
            bio=i.bio,
            age=i.age,
            birth_date=i.birth_date,
            ping_time=datetime.strptime(i.ping_time, '%Y-%m-%dT%H:%M:%S.%fZ'),
            distance_km=i.distance_km,
            get_photos=photos,
            schools=schools,
            jobs=jobs,
        )
        sql_session.add(sql_user)
        print(liked)
        if liked:
            print("###congrats!!###")
            time.sleep(2)
        time.sleep(0.5)

    sql_session.commit()
    sql_session.close()
            

