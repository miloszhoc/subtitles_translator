from config import db, ma


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_file = db.Column(db.String, nullable=False, default='default')
    translated_file = db.Column(db.String, nullable=False, default='default translated')

    def __init__(self, original_file, translated_file):
        self.original_file = original_file
        self.translated_file = translated_file


class FileSchema(ma.ModelSchema):
    class Meta:
        model = File
        session = db.session
        fields = ('translated_file', 'original_file', 'id')
