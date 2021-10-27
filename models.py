from config import db, ma


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_file = db.Column(db.String, nullable=False, default='default')
    translated_file = db.Column(db.String, nullable=False, default='default translated')
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __init__(self, original_file, translated_file, user_id):
        self.original_file = original_file
        self.translated_file = translated_file
        self.user_id = user_id


class FileSchema(ma.Schema):
    class Meta:
        model = File
        session = db.session
        include_fk = True
        fields = ('translated_file', 'original_file', 'id')


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)


class UsersSchema(ma.Schema):
    class Meta:
        model = Users
        session = db.session
        fields = ('id', 'login', 'password')
