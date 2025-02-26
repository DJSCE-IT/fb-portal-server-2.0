from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from api.main import mongo

class User:
    collection = mongo.db.users

    def __init__(self, username, email, password=None, _id=None):
        self.username = username
        self.email = email
        self._id = _id if _id else ObjectId()
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_active = True
        if password:
            self.set_password(password)

    @staticmethod
    def find_by_email(email):
        user_data = User.collection.find_one({'email': email})
        return User.from_dict(user_data) if user_data else None

    @staticmethod
    def find_by_username(username):
        user_data = User.collection.find_one({'username': username})
        return User.from_dict(user_data) if user_data else None

    @staticmethod
    def find_by_id(user_id):
        if not isinstance(user_id, ObjectId):
            try:
                user_id = ObjectId(user_id)
            except:
                return None
        user_data = User.collection.find_one({'_id': user_id})
        return User.from_dict(user_data) if user_data else None

    def save(self):
        user_data = self.to_dict()
        if not self.exists():
            User.collection.insert_one(user_data)
        else:
            User.collection.update_one(
                {'_id': self._id},
                {'$set': user_data}
            )
        return self

    def exists(self):
        return bool(User.collection.find_one({'_id': self._id}))

    def delete(self):
        User.collection.delete_one({'_id': self._id})

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'password_hash': getattr(self, 'password_hash', None),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active
        }

    @staticmethod
    def from_dict(data):
        if not data:
            return None
        user = User(
            username=data['username'],
            email=data['email'],
            _id=data['_id']
        )
        user.password_hash = data.get('password_hash')
        user.created_at = data.get('created_at', datetime.utcnow())
        user.updated_at = data.get('updated_at', datetime.utcnow())
        user.is_active = data.get('is_active', True)
        return user

    def __repr__(self):
        return f'<User {self.username}>' 