import os
import hashlib

from flask import current_app
from faker import Faker
from simpleweibo.extensions import db
from simpleweibo.models import Permission,Post,Role,Comment,User
from sqlalchemy.exc import IntegrityError
from random import seed,randint


fake = Faker('zh-CN')


def fake_admin():
    email = current_app.config['ADMIN_EMAIL']
    admin = User(username = 'jjj',
                 realname = 'jjj',
                 password = '12345678',
                 confirmed = True,
                 email = email,
                 avatar_hash = hashlib.md5(email.encode('utf-8')).hexdigest(),
                 member_since = fake.date_this_decade()
                 )
    db.session.add(admin)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def faker_user(count = 10):
    for i in range(count):
        email = fake.email()
        user = User(username = fake.name(),
                    realname = 'xuni',
                    password = '123456',
                    confirmed = True,
                    email = email,
                    avatar_hash=hashlib.md5(email.encode('utf-8')).hexdigest(),
                    member_since=fake.date_this_decade()
                    )
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

def faker_post(count = 100):
    seed()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0,user_count - 1)).first()
        p = Post(body=fake.sentence(),
                 timestamp=fake.date_this_decade(),
                 author = u)
        db.session.add(p)
        db.session.commit()

def faker_comment(count = 300):
    user_count = User.query.count()
    post_count = Post.query.count()
    for i in range(count):
        comment = Comment(body=fake.sentence(),
                          author_id = randint(1,user_count),
                          post_id = randint(1,post_count))
        db.session.add(comment)
        db.session.commit()

