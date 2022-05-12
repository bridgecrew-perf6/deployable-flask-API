from flask import Blueprint, jsonify, request
import validators 
from src.constants import http_status_codes as sc
from src.database import Bookmark, db
from flask_jwt_extended import get_jwt_identity, jwt_required

bookmarks = Blueprint(name="bookmarks", import_name=__name__, url_prefix="/api/v1/bookmarks")


@bookmarks.route('/', methods=['POST', 'GET'])
@jwt_required()
def bookmarks_main():
    current_user_id = get_jwt_identity()

    if request.method == 'POST':
        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({'error': 'Enter an valid URL'}), sc.HTTP_400_BAD_REQUEST
        
        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                'error': 'URL already exists'
            }), sc.HTTP_409_CONFLICT
        
        bk = Bookmark(url=url, body=body, user_id=current_user_id)
        
        db.session.add(bk)
        db.session.commit()
        
        return jsonify({
            'id': bk.id, 
            'url': bk.url,
            'short_url': bk.short_url,
            'vistits': bk.visits,
            'body': bk.body,
            'created_at': bk.created_at,
            'updated_at': bk.updated_at,
        }), sc.HTTP_201_CREATED

    else: 
        # return bookmarks created by the user

        #get pagination variables 
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        #WITHOUT PAGINATION: bks = Bookmark.query.filter_by(user_id=current_user_id)
        bookmarks = Bookmark.query.filter_by(user_id=current_user_id).paginate(page=page, per_page=per_page)

        data = []
        for bk in bookmarks.items:
            data.append(
                {
                    'id': bk.id, 
                    'url': bk.url,
                    'short_url': bk.short_url,
                    'visits': bk.visits,
                    'body': bk.body,
                    'created_at': bk.created_at,
                    'updated_at': bk.updated_at,
                }
            )
        
        meta = {
            "current_page": bookmarks.page,
            "pages": bookmarks.pages,
            "total_count": bookmarks.total,
            "has_prev": bookmarks.has_prev,
            "prev_page": bookmarks.prev_num, 
            "has_next": bookmarks.has_next,
            "next_page": bookmarks.next_num,
        }
        
        if len(data) is not 0:
            return jsonify({
                'bookmarks': data, 
                "meta": meta
            }), sc.HTTP_200_OK
        else:
            return jsonify({'message': 'You do not have any bookmarks yet'}), sc.HTTP_204_NO_CONTENT

