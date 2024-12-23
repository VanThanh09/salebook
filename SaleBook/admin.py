from SaleBook.models import Book, User
from flask_admin.contrib.sqla import ModelView
from SaleBook import admin, db



admin.add_view(ModelView(Book, db.session))
admin.add_view(ModelView(User, db.session))
