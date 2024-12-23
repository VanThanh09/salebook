from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary
import stripe
from flask_admin import Admin

app = Flask("__name__")
app.secret_key = "Us8k2s2@#*$jjudj^8&**tgfsgYFS677*&6s8suuuu"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/bookstore?charset=utf8mb4" % quote('123456')
app.config["PAGE_SIZE"] = 8

db = SQLAlchemy(app=app)
login_manager = LoginManager(app)

# Configuration cloudinary
cloudinary.config(
    cloud_name = "drzc4fmxb",
    api_key = "422829951512966",
    api_secret = "ILJ11vG7Q7OqbjxyhWS1lNJMN5U", # Click 'View API Keys' above to copy your API secret
    secure=True
)

stripe.api_key = 'sk_test_51QRAnrCIE1Wc5o2lkTkAnC8o8FVWn1XLfhVm8B5p63pQ3vaFSvMGR6mu4ORd5UQp5Yuudvg9EibVNAQQuyWBQU8I00PtcOTZln'

admin = Admin(app=app, name='Quản trị nhà sách', template_mode='bootstrap4')