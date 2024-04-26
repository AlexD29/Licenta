from flask import Blueprint

bp = Blueprint('news', __name__, template_folder='templates')

from app.news import routes
