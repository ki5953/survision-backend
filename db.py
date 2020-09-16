#add counter for number surveys user does that resets every Friday
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

weeklyList = []

def getweeklyList():
    return weeklyList

def addtoweeklyList(list):
    global weeklyList
    weeklyList += list

def clearweeklyList():
    global weeklyList
    for user in weeklyList:
        user.surveysCompleted = 0
    weeklyList = []

association_table = db.Table('association', db.Model.metadata,
    db.Column('surveys_id', db.Integer, db.ForeignKey('surveys.id')),
    db.Column('users_id', db.Integer, db.ForeignKey('users.id')))

specificUser = None

class Survey(db.Model):
    __tablename__ = 'surveys'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    image = db.Column(db.String, nullable = False)
    users = db.relationship("User", secondary = association_table, back_populates = "surveys")
    questions = db.relationship('Question', cascade = 'delete')

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.image = kwargs.get('image')
        self.users = []
        self.questions = []

    def partialSerialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'image': self.image,
            'questions': [question.userSerialize() for question in self.questions]
        }

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'image': self.image,
            'users': [user.partialSerialize() for user in self.users],
            'questions': [question.serialize() for question in self.questions]
        }

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    firstName = db.Column(db.String, nullable = False)
    lastName = db.Column(db.String, nullable = False)
    email = db.Column(db.String, nullable = False)
    year = db.Column(db.String, nullable = False)
    birthday = db.Column(db.String, nullable = False)
    ethnicity = db.Column(db.String, nullable = False)
    sex = db.Column(db.String, nullable = False)
    sexualOrientation = db.Column(db.String, nullable = False)
    genderIdentity  = db.Column(db.String, nullable = False)
    surveysCompleted = db.Column(db.Integer, nullable = False)
    image = db.Column(db.String, nullable = False)
    surveys = db.relationship("Survey", secondary = association_table, back_populates = "users")
    giftCards = db.relationship('GiftCard', cascade = 'delete')

    def __init__(self, **kwargs):
        self.firstName = kwargs.get('firstName')
        self.lastName = kwargs.get('lastName')
        self.email = kwargs.get('email')
        self.year = kwargs.get('year')
        self.birthday = kwargs.get('birthday')
        self.ethnicity = kwargs.get('ethnicity')
        self.sex = kwargs.get('sex')
        self.sexualOrientation = kwargs.get('sexualOrientation')
        self.genderIdentity = kwargs.get('genderIdentity')
        self.surveysCompleted = 0
        self.image = kwargs.get('image')
        self.surveys = []
        self.giftCards = []

    def partialSerialize(self):
        return {
            'id': self.id,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'email': self.email,
            'year': self.year,
            'birthday': self.birthday,
            'ethnicity': self.ethnicity,
            'sex': self.sex,
            'sexualOrientation': self.sexualOrientation,
            'genderIdentity': self.genderIdentity,
            'surveyscompleted': self.surveysCompleted,
            'image': self.image
        }

    def serialize(self):
        global specificUser
        specificUser = self.email
        response = {
            'id': self.id,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'email': self.email,
            'year': self.year,
            'birthday': self.birthday,
            'ethnicity': self.ethnicity,
            'sex': self.sex,
            'sexualOrientation': self.sexualOrientation,
            'genderIdentity': self.genderIdentity,
            'surveyscompleted': self.surveysCompleted,
            'image': self.image,
            'surveys': [survey.partialSerialize() for survey in self.surveys],
            'giftcards': [giftcard.serialize() for giftcard in self.giftCards]
        }
        specificUser = None
        return response

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String, nullable = False)
    userAnswers = db.relationship('UserAnswer', cascade = 'delete')
    surveyAnswers = db.relationship('SurveyAnswer', cascade = 'delete')
    surveyid = db.Column(db.Integer, db.ForeignKey('surveys.id'))

    def __init__(self, **kwargs):
        self.text = kwargs.get('text')
        self.userAnswers = []
        self.surveyAnswers = []
        self.surveyid = kwargs.get('surveyid')

    def userSerialize(self):
        answerlist = []
        global specificUser
        for answer in self.userAnswers:
            if answer.useremail == specificUser:
                answerlist.append(answer.serialize())
        return {
            'id': self.id,
            'text': self.text,
            'surveyAnswers': [answer.serialize() for answer in self.surveyAnswers],
            'useranswer': answerlist
        }

    def serialize(self):
        return {
            'id': self.id,
            'text': self.text,
            'surveyAnswers': [answer.serialize() for answer in self.surveyAnswers],
            'userAnswers': [answer.serialize() for answer in self.userAnswers]
        }

class SurveyAnswer(db.Model):
    __tablename__ = 'surveyAnswers'
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String, nullable = False)
    questionid = db.Column(db.Integer, db.ForeignKey('questions.id'))

    def __init__(self, **kwargs):
        self.text = kwargs.get('text')
        self.questionid = kwargs.get('questionid')

    def serialize(self):
        return {
            'id': self.id,
            'text': self.text
        }


class UserAnswer(db.Model):
    __tablename__ = 'userAnswers'
    id = db.Column(db.Integer, primary_key = True)
    response = db.Column(db.Integer, nullable = False)
    useremail = db.Column(db.String, nullable = False)
    questionid = db.Column(db.Integer, db.ForeignKey('questions.id'))

    def __init__(self, **kwargs):
        self.response = kwargs.get('response')
        self.useremail = kwargs.get('useremail')
        self.questionid = kwargs.get('questionid')

    def serialize(self):
        return {
            'id': self.id,
            'response': self.response,
            'useremail': self.useremail
        }

class GiftCard(db.Model):
    __tablename__ = 'giftcards'
    id = db.Column(db.Integer, primary_key = True)
    company = db.Column(db.String, nullable = False)
    amount = db.Column(db.String, nullable = False)
    image = db.Column(db.String, nullable = False)
    available = db.Column(db.Boolean, nullable = False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, **kwargs):
        self.company = kwargs.get('company')
        self.amount = kwargs.get('amount')
        self.image = kwargs.get('image')
        self.available = True

    def serialize(self):
        return {
            'id': self.id,
            'company': self.company,
            'amount': self.amount,
            'image': self.image,
            'available': self.available
        }
