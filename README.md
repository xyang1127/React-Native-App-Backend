# React-Native-App-Backend
This is the backend part of a simple React Native application supporting people to meet and do activities together. The backend is built upon python flask framework.

To run the code:
- modeify the `host` option to your ip address at line 221 in the "/app.py" file. (this is necessary because 'Network Request Error' would occur if we used the localhost)
- cd into the root folder of this repository: `cd path_to_the_folder`
- run `pipenv shell`
- run `python3 app.py`
- Finally, the server is running and you should see the url of the server in the termial. This url is also used for the frontend part to connect to the server. To do that, please refer to the [backend part][1]


## Design and Implementation:
This is an API server and it is writen in python flask framework. I used SQLAlchemy to implement the database and Marshmallow for serialization.

### Database:
There are two main part in this app: user and activity. Their relationship is many-to-many. To implement that, I created a User table, an Activity table and a associate table called Participants:
#### activity Table:
| Attribute | Description |
| ----------- | ----------- |
| id | id for this activity  |
| name | name for this activity |
| type | type for this activity |
| location | location for this activity |
| user_id | the id of the user who initiates this activity, this is a foreign key |
| description | detailed description for this activity |

#### user Table:
| Attribute | Description |
| ----------- | ----------- |
| id | id for this user  |
| username | username for this user |
| password | password for this user |

#### paticipants Table:
| Attribute | Description |
| ----------- | ----------- |
| user_id | id for the user who has joined this activity, this is a foreign key |
| activity_id | id for this exact activity, this is a foreign key |

### APIs:
#### log in:
- HTTP method: POST
- path: /user/login
- parameters: username, password

#### add user:
- HTTP method: POST
- path: /user
- parameters: name, username, password

#### add activity:
- HTTP method: POST
- path: /activity
- parameters: name, time, type, location, user_id, description

#### search activities:
- HTTP method: GET
- path: /activity/search
- parameters: type, time, locaion

#### get all activities:
- HTTP method: GET
- path: /activity
- parameters: None

#### join activity:
- HTTP method: GET
- path: /activity/join
- parameters: user_id, activity_id

#### unregister activity:
- HTTP method: GET
- path: /activity/unregister
- parameters: user_id, activity_id

#### delete activity:
- HTTP method: DELETE
- path: /activity/<id>
- parameters: None


[1]: https://github.com/xyang1127/React-Native-App-Frontend/tree/master
