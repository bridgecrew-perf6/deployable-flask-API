from flask import Flask, jsonify, session, redirect
import os 
from src.auth import auth 
from src.bookmarks import bookmarks
from src.constants import http_status_codes as sc
from src.database import Bookmark, db
from flask_jwt_extended import JWTManager
from flasgger import Swagger, swag_from
from src.config.swagger import template, swagger_config


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DB_URI'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'),
            SWAGGER = {
                "title": "Flask Bookmarks API",
                "uiversion": 3
            }
        )
    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)

    Swagger(app=app, config=swagger_config, template=template)


    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    
    @app.route('/<short_url>')
    @swag_from('./docs/bookmarks/short_url.yaml')
    def redirect_to_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()

        if bookmark:
            bookmark.visits = bookmark.visits + 1 
            db.session.commit()

            return redirect(bookmark.url)

    @app.errorhandler(sc.HTTP_404_NOT_FOUND)
    def handler_404(e):
        return jsonify({'error': 'not found'}), sc.HTTP_404_NOT_FOUND

    @app.errorhandler(sc.HTTP_500_INTERNAL_SERVER_ERROR)
    def handler_500(e):
        return jsonify({'message': 'sorry, you found an server error, we are working on it',
        'error': e}), sc.HTTP_500_INTERNAL_SERVER_ERROR



    return app

    
