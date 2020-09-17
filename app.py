from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
import os

# init app
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
# databse
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# init db
db = SQLAlchemy(app)
# init marshmallow
ma = Marshmallow(app)

# database model
participants = db.Table('participants',
                        db.Column('activity_id', db.Integer, db.ForeignKey(
                            'activity.id'), primary_key=True),
                        db.Column('user_id', db.Integer, db.ForeignKey(
                            'user.id'), primary_key=True)
                        )


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    location = db.Column(db.String(10000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True,)
    password = db.Column(db.String(100), nullable=False)

    organizes = db.relationship(
        'Activity', backref='organizer', lazy=True)
    join_ins = db.relationship('Activity', secondary=participants, backref=db.backref(
        'participants', lazy='dynamic'))

# Schema


class ActivitySchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'type', 'time',
                  'location', 'user_id', 'description')


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name')


# init schema
activity_schema = ActivitySchema()
activities_schema = ActivitySchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)


# @app.route('/register', methods=['GET'])
# def register():
#     return null


@app.route('/activity', methods=['GET'])
def get_all_activities():
    all_activities = Activity.query.all()
    result = activities_schema.dump(all_activities)  # list data type
    return jsonify(result)


# check if the given user has registerd the given activity
@app.route('/activity/check', methods=['GET'])
def check_activity():
    user_id = int(request.args.get("user_id"))
    activity_id = int(request.args.get("activity_id"))
    query = User.query.join(participants).join(Activity).filter(
        User.id == user_id).filter(Activity.id == activity_id)
    if(query.count() == 1):
        return jsonify({"info": "registered"})
    else:
        return jsonify({"info": "unregistered"})


@app.route('/activity/search', methods=['GET'])
def search_activities():
    type = request.args.get("type")
    time = datetime.strptime(request.args.get(
        "time"), "%a, %d %b %Y %H:%M:%S %Z")
    location = request.args.get("location")

    query = Activity.query.filter(Activity.time >= time).filter(
        Activity.location.like("%{}%".format(location)))
    if(type != 'all'):
        query = query.filter(Activity.type == type)

    result = activities_schema.dump(query.all())
    return jsonify(result)


@app.route('/activity/join', methods=['GET'])
def join_activity():
    user_id = int(request.args.get("user_id"))
    activity_id = int(request.args.get("activity_id"))
    activity = Activity.query.filter_by(id=activity_id).first()
    user = User.query.filter_by(id=user_id).first()
    activity.participants.append(user)
    db.session.commit()

    return jsonify({"info": "success"})


@app.route('/activity/unregister', methods=['GET'])
def unregister_activity():
    user_id = int(request.args.get("user_id"))
    activity_id = int(request.args.get("activity_id"))
    activity = Activity.query.filter_by(id=activity_id).first()
    user = User.query.filter_by(id=user_id).first()
    activity.participants.remove(user)
    db.session.commit()

    return jsonify({"info": "success"})


@app.route('/activity', methods=['POST'])
def add_activity():
    name = request.json['name']
    time = datetime.strptime(request.json['time'], "%a, %d %b %Y %H:%M:%S %Z")
    type = request.json['type']
    location = request.json['location']
    user_id = request.json['user_id']
    description = request.json['description']

    new_activity = Activity(name=name, time=time, type=type,
                            location=location, user_id=user_id, description=description)
    db.session.add(new_activity)
    user = User.query.filter_by(id=user_id).first()
    new_activity.participants.append(user)
    db.session.commit()

    return activity_schema.jsonify(new_activity)


@app.route('/activity/<id>', methods=['DELETE'])
def delete_activity(id):
    activity = Activity.query.get(id)
    db.session.delete(activity)
    db.session.commit()
    return activity_schema.jsonify(activity)


@app.route('/user/check', methods=['GET'])
def check_username():
    username = request.args.get("username")
    user = User.query.filter(User.username == username)
    if(user.count() == 1):
        return jsonify({"message": "fail"})
    else:
        return jsonify({"message": "success"})


@app.route('/user', methods=['POST'])
def add_user():
    name = request.json['name']
    username = request.json['username']
    password = request.json['password']

    new_user = User(name=name, username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user)


@app.route('/user/login', methods=['POST'])
def login_user():
    username = request.json['username']
    password = request.json['password']

    user = User.query.filter(User.username == username).filter(
        User.password == password).first()

    return user_schema.jsonify(user)


@app.route('/user', methods=['GET'])
def get_all_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)


@app.route('/user/<id>', methods=['GET'])
def get_single_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)


@app.route('/user/<id>', methods=['DELETE'])
def delete_product(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user)


# run server
if __name__ == '__main__':
    app.run(host='192.168.2.10', debug=True)
