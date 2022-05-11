from flask import Blueprint

bookmarks = Blueprint(name="bookmarks", import_name=__name__, url_prefix="/api/v1/bookmarks")


@bookmarks.get('/')
def get_all():
    return []