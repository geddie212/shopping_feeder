import main
from flask_sqlalchemy import SQLAlchemy


# Initial configuration
app = main.app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = 'pobycr4ter2iudyrdgdxxdindo'
db = SQLAlchemy(app)


