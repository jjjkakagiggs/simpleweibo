from datetime import datetime
import hashlib
from flask import current_app,request
from flask_login import UserMixin,AnonymousUserMixin
from werkzeug.security import generate_password_hash,check_password_hash

from simpleweibo.extensions import db,login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


roles_permissions = db.Table('roles_permissions',
                             db.Column('role_id',db.Integer,db.ForeignKey('roles.id'),primary_key=True),
                             db.Column('permission_id',db.Integer,db.ForeignKey('permissions.id'),primary_key=True)
                            )


class Permission(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30),unique = True)
    roles = db.relationship('Role',secondary=roles_permissions,back_populates='permissions')

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(30),unique=True)
    users = db.relationship('User',back_populates='role')
    permissions = db.relationship('Permission',secondary=roles_permissions,back_populates='roles')

    @staticmethod
    def init_role():
        roles_permissions_map = {
            'User': ['FOLLOW','COMMENT', 'WRITE_ARTICLES','SELF_ADMINISTER'],
            'Moderator': ['FOLLOW','COMMENT', 'WRITE_ARTICLES', 'MODERATE_COMMENTS','SELF_ADMINISTER'],
            'Administrator': ['FOLLOW','COMMENT', 'WRITE_ARTICLES', 'MODERATE_COMMENTS', 'ADMINISTER','SELF_ADMINISTER']
        }
        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name = role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.session.add(role)
            role.permissions = []
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(name=permission_name).first()
                if permission is None:
                    permission = Permission(name = permission_name)
                    db.session.add(permission)
                role.permissions.append(permission)
        db.session.commit()


class Follow(db.Model):
    """
    关注者/被关注者模型
    """
    __tablename__ = 'follows'
    # 关注者id
    follower_id = db.Column(db.Integer,db.ForeignKey('users.id'),
                            primary_key=True)
    # 被关注者id
    followed_id = db.Column(db.Integer,db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime,default=datetime.utcnow)
    # 关注者与user关系
    follower = db.relationship('User',foreign_keys=[follower_id],back_populates=
                               'followed',lazy='joined')
    # 被关注者与user关系
    followed = db.relationship('User',foreign_keys=[followed_id],back_populates=
                               'followers',lazy='joined')

class User(db.Model, UserMixin):
    """
    用户模型
    """
    __tablename__ = 'users'

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        if not self.role:
            if self.email == current_app.config['MAIL_USERNAME']:
                self.role = Role.query.filter_by(name = 'Administrator').first()
            else:
                self.role = Role.query.filter_by(name = 'User').first()

        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    id = db.Column(db.Integer, primary_key=True)                    # 用户 id
    email = db.Column(db.String(64),unique=True,)                   # 邮箱
    username = db.Column(db.String(20),unique=True)                 # 用户名
    realname = db.Column(db.String(64))                             # 真实姓名
    sex = db.Column(db.String(5), default='男')                         # 性别
    password_hash = db.Column(db.String(128))                       # 密码哈希值
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))       # 角色 id
    confirmed = db.Column(db.Boolean, default=False)                # 是否保持登录
    location = db.Column(db.String(64))                             # 地点
    about_me = db.Column(db.Text)                                   # 自我介绍
    member_since = db.Column(db.DateTime, default=datetime.utcnow)  # 注册时间
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)     # 最新登录时间
    avatar_hash = db.Column(db.String(32))                          # 头像哈希值



    role = db.relationship('Role', back_populates='users')
    posts = db.relationship('Post',back_populates = 'author',cascade='all',lazy='dynamic')
    comments = db.relationship('Comment', back_populates='author', cascade='all')

    # self.user.followed = 用户的粉丝/关注<关系>
    followed = db.relationship('Follow',foreign_keys=[Follow.follower_id],back_populates='follower',
                                lazy='dynamic',cascade='all')
    # self.user.follower =用户关注的人/被关注<关系>
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], back_populates='followed',
                                lazy='dynamic', cascade='all')

    @property
    def password(self):
        """ 密码属性不可被访问
        """
        raise AttributeError('密码不可访问')

    @password.setter
    def password(self, password):
        """ 密码属性可写不可读
        :param password: 用户密码
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
         """ 密码验证
         :param password: 用户密码
         :return: 验证成功返回 True，反之返回 False
         """
         return check_password_hash(self.password_hash, password)


    def set_follow(self,user):
        if not self.is_following(user):
            follow = Follow(follower=self,followed=user)
            db.session.add(follow)
            db.session.commit()

    def set_unfollow(self,user):
        follow = self.folloed.filter_by(followed_id = user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    def is_following(self,user):
        """
        是否关注某用户
        :param user:指定用户
        :return:
        """
        return self.followed.filter_by(followed_id = user.id).first() is not None

    def is_follwed_by(self,user):
        return self.followers.filter_by(follower_id = user.id).first() is not None

    @property
    def followed_posts(self):
        """
        查询关注者微博列表，使用了联结操作，通过 user.id 链接 follow, post 两个数据表
        :return:关注者微博列表
        """
        # print(self.id)
        return Post.query.join(
            Follow,Follow.followed_id == Post.author_id).filter(
            Follow.follower_id == self.id)



    def generate_confirmation_token(self,expiration=3600):
        """
        生成用于确认身份的密令
        :param expiration:密令有效时间，单位秒
        :return:验证密令
        """
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'comfirm':self.id})

    def confirm(self,token):
        """
        利用密令确定账户
        :param token:验证密令
        :return:
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        # db.session.add(self)
        db.session.commit()
        return True

    def generate_auth_token(self,expiration):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in=expiration)
        return s.dumps({'id': self.id})


    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    @property
    def is_administrator(self):
        """
        判断是否为管理员
        :return:是管理员返回 True，反之返回 False
        """
        return self.role.name == 'Administrator'

    def can(self,permission_name):
        permission = Permission.query.filter_by(name = permission_name).first()
        return permission is not None and self.role is not None and \
               permission in self.role.permissions

    def update_last_seen(self):
        """
        更新用于最近一次登录时间
        :return:
        """
        self.last_seen = datetime.utcnow()
        db.session.commit()

    def gravatar(self, size=100, default='identicon', rating='g'):
        """ 利用哈希值生成头像
        :param size: 头像大小
        :param default:
        :param rating:
        :return: 头像链接
        """
        if request.is_secure:  # https 类型
            url = 'https://secure.gravatar.com/avatar'
        else:  # http 类型
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


    def to_json(self,posts):
        return {
            'username': self.username,
            'memberSince': self.member_since,
            'lastSeen': self.last_seen,
            'postCount': self.posts.count(),
            'posts': posts
        }

    def __repr__(self):
        return '<User {}>'.format(self.username)


class AnonymousUser(AnonymousUserMixin):
    """
    匿名用户（游客）模型
    """
    def can(self,permissions):
        """
        游客没有任何权限
        :param permissions:指定权限
        :return: 无任何权限
        """
        return False

    @property
    def is_administrator(self):
        """ 判断是或否为管理员
        :return: 非管理员
        """
        return False

login_manager.anonymous_user = AnonymousUser # 将未登录用户赋予游客模型

@login_manager.user_loader
def load_user(user_id):
    """ Flask-Login 回调函数，用于指定标识符加载用户
        :param user_id: 用户 id
        :return: 查询到的用户对象
    """
    return User.query.get(int(user_id))


class Post(db.Model):
    """
    微博模型
    """
    __tablename__ = 'posts'

    id = db.Column(db.Integer,primary_key=True)                                # 微博 id
    body = db.Column(db.Text)                                                  # 微博内容
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)    # 发布时间
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))               # 作者 id
    author = db.relationship('User',back_populates='posts')
    comments = db.relationship('Comment', back_populates='post',lazy='dynamic', cascade='all, delete-orphan') # 评论

    def to_json(self):
        return {
            'posTime': self.timestamp,
            'post': self.body,
            'authorID': self.author_id
        }

class Comment(db.Model):
    """
    评论模型
    """
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)                             # 评论 id
    body = db.Column(db.Text)                                                # 评论内容
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # 评论时间
    disabled = db.Column(db.Boolean)                           # 是否被屏蔽
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))           # 作者 id
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))                # 微博 id

    post = db.relationship('Post', back_populates='comments')
    author = db.relationship('User',back_populates='comments')
    # replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')
    # replied = db.relationship('Comment', back_populates='replies', remote_side=[id])

    def to_json(self):
        return {
            'postTime': self.timestamp,
            'post': self.body,
            'postID': self.post_id,
            'authorID': self.author_id
        }


