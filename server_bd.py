""" База данных сервера """

""" SQLite, SQLAlchemy, Declarative """

import datetime
import sys
import os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), './common'))

SERVER_LOGGER = logging.getLogger('server')

try:
    import sqlalchemy
    from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    print(sqlalchemy.__version__)
except ImportError as e:
    SERVER_LOGGER.error(f'Библиотека SQLAlchemy не найдена: {e}')
    sys.exit(1)

from common.setting import SERVER_DATABASE


class ServerDB:
    Base = declarative_base()

    class Users(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        login = Column(String, unique=True)
        last_conn = Column(DateTime)

        def __init__(self, login):
            self.login = login
            self.last_conn = datetime.datetime.now()

    class ActiveUsers(Base):
        __tablename__ = 'active_users'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('users.id'), unique=True)
        ip = Column(String)
        port = Column(Integer)
        time_conn = Column(DateTime)

        def __init__(self, user, ip, port, time_conn):
            self.user = user
            self.ip = ip
            self.port = port
            self.time_conn = time_conn

    class LoginHistory(Base):
        __tablename__ = 'login_history'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('users.id'))
        ip = Column(String)
        port = Column(Integer)
        last_conn = Column(DateTime)

        def __init__(self, user, ip, port, last_conn):
            self.user = user
            self.ip = ip
            self.port = port
            self.last_conn = last_conn

    def __init__(self):
        self.engine = create_engine(SERVER_DATABASE, echo=False, pool_recycle=7200)

        self.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip, port):
        print(username, ip, port)
        result = self.session.query(self.Users).filter_by(login=username)
        print(result)
        if result.count():
            user = result.first()
            user.last_conn = datetime.datetime.now()
        else:
            user = self.Users(username)
            self.session.add(user)
            self.session.commit()

        new_active_user = self.ActiveUsers(user.id, ip, port, datetime.datetime.now())
        self.session.add(new_active_user)

        history = self.LoginHistory(user.id, ip, port, datetime.datetime.now())
        self.session.add(history)

        self.session.commit()

    def user_logout(self, username):
        user = self.session.query(self.Users).filter_by(login=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def users_list(self):
        result = self.session.query(self.Users.login, self.Users.last_conn).all()
        return result

    def active_users_list(self):
        result = self.session.query(self.Users.login, self.ActiveUsers.ip, self.ActiveUsers.port,
                                    self.ActiveUsers.time_conn).join(self.Users).all()
        return result

    def login_history(self, username=None):
        result = self.session.query(self.Users.login, self.LoginHistory.ip, self.LoginHistory.port,
                                    self.LoginHistory.last_conn).join(self.Users)

        if username:
            result = result.filter(self.Users.login == username)

        return result.all()


if __name__ == '__main__':
    db = ServerDB()
    db.user_login('client_1', '192.168.1.4', 8888)
    db.user_login('client_2', '192.168.1.5', 7777)
    # выводим список кортежей - активных пользователей
    print(f'{db.active_users_list()=}')
    # выполняем 'отключение' пользователя
    db.user_logout('client_1')
    print(f'{db.users_list()=}')
    # выводим список активных пользователей
    print(f'{db.active_users_list()=}')
    db.user_logout('client_2')
    print(f'{db.users_list()=}')
    print(f'{db.active_users_list()=}')

    # запрашиваем историю входов по пользователю
    print(f'{db.login_history(username="client_1")=}')
    # выводим список известных пользователей
    print(f'{db.users_list()=}')
