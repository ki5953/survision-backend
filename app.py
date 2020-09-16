import json
from flask import Flask, request
from db import db, User, Survey, Question, UserAnswer, SurveyAnswer, GiftCard
from db import getweeklyList, addtoweeklyList, clearweeklyList
import random

app = Flask(__name__)
db_filename = 'surveys.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
with app.app_context():
    db.create_all()



@app.route('/api/test/')
def test():
    return "test"

@app.route('/api/getsurveys/')
def getSurveys():
    surveys = Survey.query.all()
    get = {'success': True, 'data': [survey.serialize() for survey in surveys]}
    return json.dumps(get), 200

@app.route('/api/getsurvey/<int:surveyid>/')
def getSpecificSurvey(surveyid):
    survey = Survey.query.filter_by(id = surveyid).first()
    if survey is not None:
        return json.dumps({'success': True, 'data': survey.serialize()}), 200
    return json.dumps({'success': False, 'error': 'Survey not found!'}), 404

@app.route('/api/addsurvey/', methods = ['POST'])
def addSurvey():
    surveyBody = json.loads(request.data)
    surveyname = surveyBody.get('name')
    survey = Survey(
        name = surveyname,
        image = surveyBody.get('image')
        )
    db.session.add(survey)
    db.session.commit() # might not need
    survey = Survey.query.filter_by(name = surveyname).first()
    questionBody = surveyBody.get('questions')
    questionText = questionBody['text']
    for num in range(len(questionText)):
        question = Question(text = questionText[num], surveyid = survey.id)
        db.session.add(question)
        survey.questions.append(question)
        db.session.commit() # might not need til very end
        question = Question.query.filter_by(text = questionText[num]).first()
        for answer in questionBody['answers'][num]:
            answer = SurveyAnswer(
                text = answer,
                questionid = question.id
            )
            db.session.add(answer)
            question.surveyAnswers.append(answer)
    db.session.commit()
    return json.dumps({'success': True, 'data': survey.serialize()}), 201

@app.route('/api/<int:surveyid>/', methods = ['Delete'])
def deleteSurvey(surveyid):
    survey = Survey.query.filter_by(id = surveyid).first()
    if survey is not None:
        db.session.delete(survey)
        db.session.commit()
        return json.dumps({'success': True, 'data': survey.serialize()}), 201
    return json.dumps({'success': False, 'error': 'Survey not found!'}), 404



@app.route('/api/adduser/', methods = ['POST'])
def addUser():
    userBody = json.loads(request.data)
    user = User(
        firstName = userBody.get('firstName'),
        lastName = userBody.get('lastName'),
        email = userBody.get('email'),
        year = userBody.get('year'),
        birthday = userBody.get('birthday'),
        ethnicity = userBody.get('ethnicity'),
        sex = userBody.get('sex'),
        sexualOrientation = userBody.get('sexualOrientation'),
        genderIdentity = userBody.get('genderIdentity'),
        image = userBody.get('image')
    )
    db.session.add(user)
    db.session.commit()
    return json.dumps({'success': True, 'data': user.serialize()}), 201

@app.route('/api/getuser/<string:useremail>/')
def getSpecificUser(useremail):
    user = User.query.filter_by(email = useremail).first()
    if user is not None:
        return json.dumps({'success': True, 'data': user.serialize()}), 201
    else:
        return json.dumps({'success': False, 'error': 'User not found!'}), 404


@app.route('/api/<int:surveyid>/submitsurvey/', methods = ['POST'])
def submitsurvey(surveyid):
    survey = Survey.query.filter_by(id = surveyid).first()
    if survey is not None:
        body = json.loads(request.data)
        username = body.get('useremail')
        user = User.query.filter_by(email = username).first()
        answers = body.get('answers')
        questions = survey.questions
        for index in range(len(answers)):
            answer = UserAnswer(
                response = answers[index],
                useremail = username,
                questionid = questions[index].id
            )
            db.session.add(answer)
            questions[index].userAnswers.append(answer)
        user.surveysCompleted += 1
        survey.users.append(user)
        addtoweeklyList([user.email])
        db.session.commit()
        return json.dumps({'success': True, 'data': survey.serialize()}), 201
    else:
        return json.dumps({'success': False, 'error': 'Survey not found!'}), 404



@app.route('/api/addgiftcard/', methods = ['POST'])
def addGiftCard():
    body = json.loads(request.data)
    card = GiftCard(
        company = body.get('company'),
        amount = body.get('amount'),
        image = body.get('image')
    )
    db.session.add(card)
    db.session.commit()
    return json.dumps({'success': True, 'data': card.serialize()}), 201

@app.route('/api/viewgiftcards/')
def getGiftCards():
    cards = GiftCard.query.all()
    get = {'success': True, 'data': [card.serialize() for card in cards]}
    return json.dumps(get), 200


@app.route('/api/deletecard/<string:company>/<string:amount>/', methods = ['Delete'])
def deletegiftcard(company, amount):
    cards = GiftCard.query.filter_by(company = company).all()
    for card in cards:
        if (card.available == True and card.amount == amount):
            db.session.delete(card)
            db.session.commit()
            return json.dumps({'success': True, 'data': card.serialize()}), 201
    return json.dumps({'success': False, 'error': 'Card not found'}), 404



@app.route('/api/choosewinners/')
def chooseWinners():
    cards = GiftCard.query.all()
    availablecards = []
    for card in cards:
        if card.available == True:
            availablecards.append(card)
    winNum = len(availablecards)
    surveys = Survey.query.all()
    userscompleted = getweeklyList()
    if len(userscompleted) > winNum:
        winners = random.sample(userscompleted, winNum)
    else:
        winners = userscompleted
    for num in range(len(winners)):
        user = User.query.filter_by(email = winners[num]).first()
        winners[num] = user
        winners[num].giftCards.append(availablecards[num])
        availablecards[num].user = winners[num].id
        availablecards[num].available = False
    clearweeklyList()
    db.session.commit()
    return json.dumps({'success': True, 'data': [winner.partialSerialize() for winner in winners]}), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
