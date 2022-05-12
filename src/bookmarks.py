import json
from flask import Blueprint, jsonify, request
import validators 
from src.constants import http_status_codes as sc
from src.database import User, Bookmark, db
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

@bookmarks.get('/<int:id>')
@jwt_required()
def get_bookmark_by_id(id):
    current_user_id = get_jwt_identity()

    bookmark = Bookmark.query.filter_by(user_id=current_user_id, id=id).first()
    
    if not bookmark:
        return jsonify(
            {
                'error': 'bookmark not found'
            }
        ), sc.HTTP_404_NOT_FOUND

    else:
        return jsonify(
            {
                'id': bookmark.id, 
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visits': bookmark.visits,
                'body': bookmark.body,
                'created_at': bookmark.created_at,
                'updated_at': bookmark.updated_at,
            }
        )

@bookmarks.put('/<int:id>')
@bookmarks.patch('/<int:id>')
@jwt_required()
def update_bookmark(id):
    
    current_user_id = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user_id, id=id).first()
    
    if not bookmark:
        return jsonify(
            {
                'error': 'bookmark not found'
            }
        ), sc.HTTP_404_NOT_FOUND

    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return jsonify({'error': 'Enter an valid URL'}), sc.HTTP_400_BAD_REQUEST
    
    if Bookmark.query.filter_by(url=url).first():
        return jsonify({
            'error': 'URL already exists'
        }), sc.HTTP_409_CONFLICT

    bookmark.url = url 
    bookmark.body = body 
    db.session.commit()

    return jsonify({'message': 'bookmark updated successfuly',
                    'data': {
                                'id': bookmark.id, 
                                'url': bookmark.url,
                                'short_url': bookmark.short_url,
                                'visits': bookmark.visits,
                                'body': bookmark.body,
                                'created_at': bookmark.created_at,
                                'updated_at': bookmark.updated_at,
                            }}), sc.HTTP_200_OK

@bookmarks.delete('/<int:id>')
@jwt_required()
def delete_bookmark(id):
    
    current_user_id = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user_id, id=id).first()
    
    if not bookmark:
        return jsonify(
            {
                'error': 'bookmark not found'
            }
        ), sc.HTTP_404_NOT_FOUND

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({
        'message': 'bookmark deleted successfuly'
    }), sc.HTTP_204_NO_CONTENT

@bookmarks.get('/stats')
@jwt_required()
def get_stats():
    current_user_id = get_jwt_identity()
    items = Bookmark.query.filter_by(user_id=current_user_id).all()
    
    if not items: 
        return jsonify({'error': 'you dont have any bookmarks yet' }), sc.HTTP_204_NO_CONTENT
    
    visits = []
    total_visits = 0 
    for item in items:
        visits.append(item.visits)
        total_visits = total_visits + item.visits

    max_visits = max(visits)
    min_visits = min(visits)

    data = {
        'total_visists': total_visits, 
        'max_visits': max_visits,
        'min_visits': min_visits
    }
       
    return jsonify({'data': data}), sc.HTTP_200_OK