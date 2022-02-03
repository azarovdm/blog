from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail


my_app = Flask(__name__)
my_app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
my_app.config['SECRET_KEY'] = '12345' 
my_app.config['MAIL_SERVER'] = 'in-v3.mailjet.com'
my_app.config['MAIL_PORT'] = 587
my_app.config['MAIL_USE_TLS'] = True
my_app.config['MAIL_USERNAME'] = '4359196a7541e723da204131415e7091'
my_app.config['MAIL_DEFAULT_SENDER'] ='demidov.2013@yandex.ru'
my_app.config['MAIL_PASSWORD'] = '79ac0439c64ecea56d7a2f82bdc05c24'
db = SQLAlchemy(my_app)
migrate = Migrate(my_app, db)
login = LoginManager(my_app)
login.login_view = 'login'
mail = Mail(my_app)


from app import routes