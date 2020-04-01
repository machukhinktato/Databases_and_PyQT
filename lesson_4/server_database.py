from sqlalchemy import *
from sqlalchemy.orm import mapper, sessionmaker
from shared.variables import *
import datetime


class ServerStorage:
    class AllUsers:
        def __init__(self, username):
            self.name = username
            self.last_login = datetime.datetime.now()
            self.id = None

    # class list of active users maker
    class ActiveUsers:
        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

    # instance of that class = logging
    class LoginHistory:
        def __init__(self, name, date, ip, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip = ip
            self.port = port

    # class - display table of users contacts
    class UsersContacts:
        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

    # class - display table of action history
    class UsersHistory:
        def __init__(self, user):
            self.id = None
            self.user = user
            self.sent = 0
            self.accepted = 0

    def __init__(self, path):
        print(path)
        self.database_engine = create_engine(
            f'sqlite:///{[path]}',
            echo=False,
            pool_recycle=7200,
            connect_args={'check_same_thread': False}
        )
        self.metadata = MetaData()

        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String, unique=True),
                            Column('last_login', DateTime)
                            )

        active_users_table = Table('Active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('Users.id'), unique=True),
                                   Column('ip_address', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime)
                                   )

        user_login_history = Table('Login_history', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('name', ForeignKey('Users.id')),
                                   Column('date_time', DateTime),
                                   Column('ip', String),
                                   Column('port', String)
                                   )

        contacts = Table('Contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user', ForeignKey('Users.id')),
                         Column('contact', ForeignKey('Users.id'))
                         )

        users_history_table = Table('History', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user', ForeignKey('Users.id')),
                                    Column('sent', Integer),
                                    Column('accepted', Integer),
                                    )

        self.metadata.create_all(self.database_engine)
        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)
        mapper(self.UsersContacts, contacts)
        mapper(self.UsersHistory, users_history_table)
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    # function which wrote logs
    def user_login(self, username, ip_address, port):
        rez = self.session.query(self.AllUsers).filter_by(name=username)
        if rez.count():
            user = rez.first()
            user.last_login = datetime.datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()
            user_in_history = self.UsersHistory(user.id)
            self.session.add(user_in_history)

        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)
        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)
        self.session.commit()

    # function which control users logout
    def user_logout(self, username):
        user = self.session.query(self.AllUsers).filter_by(name=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    # function fixes message sending and wrote it in db
    def process_message(self, sender, recipient):
        sender = self.session.query(self.AllUsers).filter_by(
            name=sender).first().id
        recipient = self.session.query(self.AllUsers).filter_by(
            name=recipient).first().id
        sender_row = self.session.query(self.UsersHistory).filter_by(
            user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(self.UsersHistory).filter_by(
            user=recipient).first()
        recipient_row.accepted += 1
        self.session.commit()

    #   function add contact for user
    def add_contact(self, user, contact):
        user = self.session.query(
            self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(
            self.AllUsers).filter_by(name=contact).first()

        if not contact or self.session.query(
                self.UsersContacts).filter_by(user=user.id, contact=contact.id).count():
            return

        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    # function to delete contact data from db
    def remove_contact(self, user, contact):
        user = self.session.query(
            self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(
            self.AllUsers).filter_by(name=contact).first()

        if not contact:
            return

        print(self.session.query(self.UsersContacts).filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id
        ).delete())
        self.session.commit()

    # call list of users which was online from last log
    def users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login
        )
        return query.all()

    # call list with users online
    def active_users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    # call log history of user(s)
    def login_history(self, username=None):
        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port
                                   ).join(self.AllUsers)
        if username:
            query = query.filter(self.AllUsers.name == username)
        return query.all()

    # function return list of user contact
    def get_contacts(self, username):
        user = self.session.query(
            self.AllUsers).filter_by(name=username).one()
        query = self.session.query(
            self.UsersContacts, self.AllUsers.name).filter_by(
            user=user.id).join(
            self.AllUsers, self.UsersContacts.contact == self.AllUsers.id)

        return [contact[1] for contact in query.all()]

    # function returns number of sent and received messages
    def message_history(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.UsersHistory.sent,
            self.UsersHistory.accepted,
        ).join(self.AllUsers)
        return query.all()


# debug
if __name__ == '__main__':
    test_db = ServerStorage()
    test_db.user_login('1111', '192.168.1.4', 8888)
    test_db.user_login('McG2', '192.168.1.5', 7777)
    print(test_db.users_list())
    # print(test_db.active_users_list())
    # test_db.user_logout('McG')
    # print(test_db.login_history('re'))
    # test_db.add_contact('test2', 'test1')
    # test_db.add_contact('test1', 'test3')
    # test_db.add_contact('test1', 'test6')
    # test_db.remove_contact('test1', 'test3')
    test_db.process_message('McG2', '1111')
    print(test_db.message_history())
