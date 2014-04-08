import requests
import json
import time
from datetime import date

class Object(object):
    def __init__(self, session, identifier):
        self.__session = session
        self.__identifier = identifier

    @property
    def session(self):
        return self.__session

    @property
    def identifier(self):
        return self.__identifier

        
class Task(Object):
    def __init__(self, project, data):
        super(Task, self).__init__(project.session, data['id'])
        self.__url = project.url + '/tasks/' + str(self.identifier)
        self.__data = data

    @property
    def name(self):
        return self.__data['name']

    @name.setter
    def name(self, name):
        self.__data['name'] = name

    @property
    def description(self):
        return self.__data['description']

    @description.setter
    def description(self, description):
        self.__data['description'] = description

    @property
    def parent(self):
        return self.__data['parent']

    @parent.setter
    def parent(self, parent):
        self.__data['parent'] = parent

    @property
    def estimated(self):
        return { 'effort'   : self.__data['estimated_effort'],
                 'duration' : self.__data['estimated_duration'],
                 'start'    : date.fromtimestamp(self.__data['estimated_start']),
                 'end'      : date.fromtimestamp(self.__data['estimated_end']) }

    @property
    def planned(self):
        return { 'effort'   : self.__data['planned_effort'],
                 'duration' : self.__data['planned_duration'],
                 'start'    : date.fromtimestamp(self.__data['planned_start']),
                 'end'      : date.fromtimestamp(self.__data['planned_end']) }

    @property
    def current(self):
        return { 'start'  : date.fromtimestamp(self.__data['starts_on']),
                 'effort' : self.__data['current_effort'] }

    @current.setter
    def current(self, current):
        assert (type(current['start']) is datetime.date)
        self.__data['starts_on'] = int(time.mktime(current['start'].timetuple()))
        self.__data['current_effort'] = current['effort']

    @property
    def dependencies(self):
        return self.__data['outgoing_dependencies']

    @property
    def closed(self):
        return self.__data['closed']
        
    def subtask(self, name, description, planned_effort, starts_on):
        assert (type(starts_on) is datetime.date)

        data = { 'name': name, 
                 'description': description, 
                 'planned_effort' : planned_effort,
                 'starts_on': int(time.mktime(starts_on.timetuple())) }
        return self.session.rawRequest(self.__url + '/subtasks', Session.POST, data)

    def update(self):
        return self.session.rawRequest(self.__url, Session.PUT, self.__data)


class Project(Object):
    def __init__(self, session, identifier):
        super(Project, self).__init__(session, identifier)
        self.__url = '/api/projects/' + identifier

    def activate(self):
        return self.session.rawRequest('/api/session/project', Session.POST, { 'identifier': self.identifier })

    def tasks(self):
        response = self.session.rawRequest(self.url + '/tasks')
        return map(lambda t: Task(self, t),
                   json.loads(response.text))

    def summary(self):
        response = self.session.rawRequest(self.url + '/summary')
        return json.loads(response.text)

    def chats(self, identifier=None):
        if identifier is None:
            response = self.session.rawRequest(self.url + '/chats/status')
        else:
            response = self.session.rawRequest(self.url + '/chats/' + str(identifier))
        return json.loads(response.text)

    @property
    def url(self):
        return self.__url

    def commit(self):
        return self.session.rawRequest(self.url + '/commit', Session.POST, { 'identifier': self.identifier })


class User(Object):
    def __init__(self, session, username):
        super(User, self).__init__(session, username)
        self.__url = '/api/users/' + self.identifier
        self.__data = json.loads(self.session.rawRequest(self.__url).text)

    @property
    def first_name(self):
        return self.__data['first_name']

    @property
    def last_name(self):
        return self.__data['last_name']
        
    @property
    def email(self):
        return self.__data['email']


class Session:
    GET = 0
    POST = 1
    PUT = 2
    DELETE = 3

    def __init__(self, url):
        self.__session = requests.Session()
        self.__urlRoot = url

    def login(self, username, password):
        data = { 'username': username,
                 'password': password }
        self.__username = username;
        return self.rawRequest('/api/session/login', Session.POST, data)

    def logout(self):
        return self.rawRequest('/api/session/logout', Session.POST)

    def rawRequest(self, url_api, method=GET, data=None):
        url = self.__urlRoot + url_api

        if method == Session.POST:
            return self.__session.post(url, json.dumps(data))

        elif method == Session.PUT:
            return self.__session.put(url, json.dumps(data))

        elif method == Session.GET:
            return self.__session.get(url)

        elif method == Session.DELETE:
            return self.__session.delete(url)

    def user(self, username=None):
        if username:
            return User(self, username)
        else:
            return User(self, self.__username)

    def projects(self):
        response = self.rawRequest('/api/users/' + self.__username + '/projects')
        return map(lambda p: Project(self, p['identifier']),
                   json.loads(response.text))
