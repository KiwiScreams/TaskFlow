from src.ext import db

class BaseModel(db.Model):
    __abstract__ = True
    def create(self, commit=True):
        db.session.add(self)
        if commit:
            self.save()

    def save(self):
        db.session.commit()

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            self.save()