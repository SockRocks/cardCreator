from flask import Flask, url_for, request, render_template, Response, redirect
from flask_sqlalchemy import SQLAlchemy
from os import mkdir, listdir, remove
'''Library Citations:'''
'''
Title: flask
Author: Armin Ronacher
Date: 4/3/20
Version: 1.1.2
Source: https://pypi.org/project/Flask/#description
'''
'''
Title: Flask-SQLalchmey
Authors: davidism and ThiefMaster
Date: 7/14/20
Version: 2.4.4
Source: https://pypi.org/project/Flask-SQLAlchemy/#description
'''


'''App Setup'''
# Creates an app object
app = Flask(__name__)
# Adjusts the settings for the database
app.config['TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///static/userDatabase/users.sqlite3'
# Creates database object
db = SQLAlchemy(app)

'''Databases:'''


# Purpose: Log username and password credentials together
class userTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(40), nullable=False)


# Purpose: Log previously applied card settings
# so that they may be loaded when the user leaves the page for the card side they have altered
class userCardSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(30), nullable=False)
    cardBackColor = db.Column(db.String(50), default='white')
    cardFrontColor = db.Column(db.String(50), default='white')
    cardBackTitleText = db.Column(db.String(50), default='Your Title')
    cardFrontTitleText = db.Column(db.String(50), default='Your Title')
    cardBackTitleCol = db.Column(db.String(10), default='black')
    cardFrontTitleCol = db.Column(db.String(10), default='black')
    cardBackTitleFontFam = db.Column(db.String(50), default='Times')
    cardFrontTitleFontFam = db.Column(db.String(50), default='Times')
    cardBackIconPath = db.Column(db.String(50), default='none')
    cardFrontIconPath = db.Column(db.String(50), default='none')
    cardBackBorderStyle = db.Column(db.String(10), default='none')
    cardFrontBorderStyle = db.Column(db.String(10), default='none')
    cardBackBorderCol = db.Column(db.String(10), default='orange')
    cardFrontBorderCol = db.Column(db.String(10), default='orange')
    cardDesc = db.Column(db.String(100), default='Your Description')
    cardDescCol = db.Column(db.String(10), default='black')
    cardDescFontFam = db.Column(db.String(50), default='Times')


# Purpose: A class to hold all functions that are used in a
# wide variety of tasks throughout the program
class generalFunctions:
    def __init__(self):
        self.username = None
        # Variables that change rapidly
        self.sideOfCard = None
        self.isDesc = False

        # Card Settings Variables where the first element in each list matched with each key is the back side setting
        # and the second element is the front side setting
        self.cardSettings = {'cardColor': [None, None], 'cardTitleText': [None, None],
                             'cardTitleCol': [None, None], 'cardTitleFontFam': [None, None],
                             'cardIconPath': [None, None], 'cardBorderStyle': [None, None],
                             'cardBorderCol': [None, None], 'cardDesc': [None, None],
                             'cardDescCol': [None, None], 'cardDescFontFam': [None, None]}

        # Option Display Settings
        self.visSettings = {'bord': 'none', 'icon': 'none', 'text': 'none', 'cardT': 'none'}

    # Purpose: Checks which side of the card is currently being edited
    def cardSideChecker(self, sideOfCard):

        if sideOfCard == 'front':
            self.sideOfCard = 'frontSideOfCard.html'
        elif sideOfCard == 'back':
            self.sideOfCard = 'backSideOfCard.html'

    # Purpose: Creates the default background color settings (white) within the database if they are not already logged
    def cardBackgroundColor(self):
        if not self.newBackColorCheck():
            defaultSetting = userCardSettings(user=self.username)
            db.session.add(defaultSetting)
            db.session.commit()

    # Purpose: Checks if the current side of the card has a
    # background color setting logged in the userCardSettings database
    def newBackColorCheck(self):
        color = userCardSettings.query.filter_by(user=self.username).first()

        if not color:
            return False
        else:
            return True

    # Purpose: Updates each of the attributes of the generalFunctions
    # class to be accurate to the user's changes to the card
    def settingApply(self):
        self.cardBackgroundColor()
        settings = userCardSettings.query.filter_by(user=self.username).first()

        # Iterates through the columns in the card settings database and matches each column with the
        # corresponding setting in the self.cardSettings dictionary and assigns the correct value to
        # each dictionary value and the correct side of the card
        '''__dict__ accesses all of the attributes of a class and returns them in an associative array
        Where each attribute name is a key that accesses the value of the corresponding  attribute 
        in the associative array'''
        for setting in settings.__dict__:
            if setting != '_sa_instance_state' and setting != 'id' and setting != 'user':
                if 'Front' in setting or 'cardDesc' == setting:
                    side = 1
                else:
                    side = 0
                self.cardSettings[setting.replace('Front', '').replace('Back', '')][side] = settings.__dict__[setting]


glob = generalFunctions()


# The index function of a Flask program.
# The function decorator @app.route('/') tells Flask what function to call first
@app.route('/')
def index():
    return render_template('index.html')


# Purpose: Updates the editor page with all of the current changes applied; including changes to the user's card
# and changes to the editor itself, ie. option menus
@app.route('/pageUpdater', methods=['GET'])
def pageUpdater():
    glob.settingApply()
    tempSettings = [None, None, None, None, None, None, None, None, None, None]

    # Checks which side of the card is being updated and assigns the values appropriately

    if glob.sideOfCard == 'frontSideOfCard.html':
        # If side equals one, then the for loop will access the front side setting for the attribute
        # This process works the same way for when side equals zero except it accesses the back side attribute
        side = 1
        sideOfCard = 'front'
        if glob.isDesc:
            textEditText = 'Description Editor'
        else:
            textEditText = 'Title Editor'

    else:
        side = 0
        sideOfCard = 'back'
        textEditText = 'Title Editor'

    counter = 0
    # Fills the tempSettings array with the settings from the cardSettings array
    for setting in glob.cardSettings:
        tempSettings[counter] = glob.cardSettings[setting][side]
        counter += 1

    # Returns the correct side of the card with every part of the card updated
    # with the appropriate values taken from the database

    return render_template(glob.sideOfCard, newBackColor=tempSettings[0], userText=tempSettings[1],
                           newVisBord=glob.visSettings['bord'],
                           newVisIcon=glob.visSettings['icon'], newVisText=glob.visSettings['text'],
                           newVisCardT=glob.visSettings['cardT'],
                           newColor=tempSettings[2], newFontFam=tempSettings[3], userImg=tempSettings[4],
                           sideOfCard=sideOfCard,
                           borderStyle=tempSettings[5], borderColor=tempSettings[6], userDescription=tempSettings[7],
                           descCol=tempSettings[8], descFont=tempSettings[9], textEditorTitle=textEditText)


# Handles all attempted logins
# Checks to see if the username and password entered are valid
@app.route('/loginHandler', methods=['POST'])
def loginHandler():
    try:
        credentials = (request.form['username'], request.form['password'])
    except:
        return Response(status=400)
    # Querys database for rows within the column that have a
    # username equal to the one entered by the person attempting to sign up.
    # The first row found that matches this condition is saved within the variable
    user = userTable.query.filter_by(username=credentials[0]).first()
    if user:
        # checks to see if the password associated with the username
        # found in the database matches the password entered by the user
        # if the conditions stated above are true, then the user is taken to the editor for the back side of the card
        if user.password == credentials[1]:
            glob.username = user.username
            glob.cardSideChecker('back')
            return redirect('/pageUpdater')
        else:
            return render_template('index.html', invalidPass='Wrong Password Associated With that Account')
    else:
        return render_template('index.html', invalidUser='There are No Users by that Name')


# Sends the sign up page to the user
@app.route('/signUpPageRedirector', methods=['GET'])
def signUpPageRedirector():
    return render_template('signUp.html')


# Receives the data submitted from the sign up page
@app.route('/signUpHandler', methods=['POST'])
def signUpHandler():
    try:
        credentials = (request.form['user'], request.form['pass'])
    except:
        return Response(status=400)
    # Querys the entire database
    entireTable = userTable.query.all()
    duplicate = False
    for curUsername in entireTable:
        # Checks if the current username the loop is on matches the user's username
        if curUsername.username == credentials[0]:
            # If there is a match between the usernames, the loop ceases
            # and sets the boolean representing whether or not a duplicate has been found to true
            duplicate = True
            break
    if duplicate:
        # Sends the user back to the sign up page telling them that their username is already in use
        return render_template('signUp.html', response='That Username is Already in Use')
    else:
        # If the user's username was not found to match anyone else's, their username and password
        # are added to the database, and tells the user that their sign up was a success
        newUser = userTable(username=credentials[0], password=credentials[1])
        db.session.add(newUser)
        db.session.commit()
        try:
            mkdir('static/media/' + credentials[0])
        except:
            return Response(status=500)
        return render_template('signUp.html', success='Your Sign Up was a Success!')


# Purpose: handles all options within the toolbox divider in HTML
@app.route('/toolBoxHandler', methods=['POST'])
def toolBoxHandler():
    try:
        option = request.form['submit']
        sideOfCard = request.form['sideOfCard']
    except:
        return Response(status=400)

    glob.cardSideChecker(sideOfCard)
    keyName = None
    # Adds the default background color to the userCardSettings database if there are no settings for
    # the background color
    # Following this, the color is set as the background color for the user's card
    if glob.sideOfCard == 'frontSideOfCard.html':
        color = glob.cardSettings['cardColor'][1]
    else:
        color = glob.cardSettings['cardColor'][0]

    if option == 'Borders':
        glob.visSettings['bord'] = 'block'
        keyName = 'bord'
    elif option == 'Icon':
        glob.visSettings['icon'] = 'block'
        keyName = 'icon'
    elif option == 'Title':
        glob.visSettings['text'] = 'block'
        keyName = 'text'
        glob.isDesc = False
    elif option == 'Card Description':
        glob.visSettings['text'] = 'block'
        keyName = 'text'
        glob.isDesc = True
    elif option == 'Card Type':
        glob.visSettings['cardT'] = 'block'
        keyName = 'cardT'
    elif option == 'Change to Front-Side of Card':
        glob.cardSideChecker('front')
        keyName = 'none'
    elif option == 'Change to Back-Side of Card':
        glob.cardSideChecker('back')
        keyName = 'none'
    else:
        return Response(status=400)

    # Closes all options except for the one currently opened by the user
    for visSet in glob.visSettings:
        if keyName != visSet:
            glob.visSettings[visSet] = 'none'
    return redirect('/pageUpdater')


# Purpose: Sets the background color of the user's card to the color input by the user
@app.route('/backgroundAdjust', methods=['POST'])
def backgroundAdjust():
    try:
        newBackColor = request.form['backgroundColor']
        sideOfCard = request.form['sideOfCard']
    except:
        return Response(status=400)

    # Checks the side of the card
    glob.cardSideChecker(sideOfCard)
    # Grabs the currently set colors
    newColor = userCardSettings.query.filter_by(user=glob.username).first()

    # Checks to see which side of the card the user is trying to change the background color for
    if glob.sideOfCard == 'frontSideOfCard.html':
        # Sets a variable that will be the color of the front of the card equal to the
        # color submitted by the user
        # sets the variable that represents the color of the back side of the card equal to the value already
        # in the database
        newColor.cardFrontColor = newBackColor
        glob.cardSettings['cardColor'][1] = newBackColor
    else:
        # does the inverse of the commands within the previous conditional
        newColor.cardBackColor = newBackColor
        glob.cardSettings['cardColor'][0] = newBackColor

    db.session.commit()

    return redirect('/pageUpdater')


# Purpose: Displays the user's text as the title on their card
@app.route('/userText', methods=['POST'])
def userText():
    try:
        userTextContent = request.form['textContent']
        cardSide = request.form['sideOfCard']
    except:
        return Response(status=400)

    glob.cardSideChecker(cardSide)
    settings = userCardSettings.query.filter_by(user=glob.username).first()

    # Checks if the text being edited is the description or title and assigns the user's values
    # to the correct settings as a result
    if not glob.isDesc:
        if glob.sideOfCard == 'frontSideOfCard.html':
            settings.cardFrontTitleText = userTextContent
            side = 1
        else:
            settings.cardBackTitleText = userTextContent
            side = 0
        glob.cardSettings['cardTitleText'][side] = userTextContent
    else:
        glob.cardSettings['cardDesc'][1] = userTextContent
        settings.cardDesc = userTextContent

    db.session.commit()
    return redirect('/pageUpdater')


# Purpose: Change the text of the user's title to their selected color
@app.route('/textColor', methods=['POST'])
def textColor():
    try:
        textColor = request.form['textColor']
        sideOfCard = request.form['sideOfCard']
    except:
        return Response(status=400)

    glob.cardSideChecker(sideOfCard)
    settings = userCardSettings.query.filter_by(user=glob.username).first()
    # Checks if the text being edited is the description or title and assigns the user's values
    # to the correct settings as a result
    if not glob.isDesc:
        if glob.sideOfCard == 'frontSideOfCard.html':
            settings.cardFrontTitleCol = textColor
            glob.cardSettings['cardTitleCol'][1] = textColor
        else:
            settings.cardBackTitleCol = textColor
            glob.cardSettings['cardTitleCol'][0] = textColor
    else:
        settings.cardDescCol = textColor
        glob.cardSettings['cardDescCol'][1] = textColor

    db.session.commit()
    return redirect('/pageUpdater')


@app.route('/fontChanger', methods=['POST'])
def fontChanger():
    try:
        userFont = request.form['fonts']
        cardSide = request.form['sideOfCard']
    except:
        return Response(status=400)
    glob.cardSideChecker(cardSide)
    settings = userCardSettings.query.filter_by(user=glob.username).first()
    # Checks if the text being edited is the description or title and assigns the user's values
    # to the correct settings as a result
    if not glob.isDesc:
        if glob.sideOfCard == 'frontSideOfCard.html':
            settings.cardFrontTitleFontFam = userFont
            glob.cardSettings['cardTitleFontFam'][1] = userFont
        else:
            settings.cardBackTitleFontFam = userFont
            glob.cardSettings['cardTitleFontFam'][0] = userFont
    else:
        settings.cardDescFontFam = userFont
        glob.cardSettings['cardDescFontFam'][1] = userFont

    db.session.commit()
    return redirect('/pageUpdater')


# Updates the card's icon
@app.route('/iconUpdater/<side>', methods=['POST'])
def iconUpdater(side=None):
    try:
        icon = request.files['userIcon']
    except:
        return Response(status=400)

    # Checks if the user's image is the correct file type (jpg or png)
    if icon.filename.upper().endswith('.JPG') or icon.filename.upper().endswith('.PNG'):
        # Uses the data in the side variable to define a class attribute called: sideOfCard
        glob.cardSideChecker(side)
        path = f'static/media/{glob.username}'
        try:
            # Deletes any previous icons for the side of the card that the current icon is being assigned to
            for file in listdir(path):
                if f'%${glob.sideOfCard}' in file:
                    remove(path + '/' + file)
        except:
            return Response(status=500)
        try:
            # Path includes %$ to delimit the side of the card that the icon is being assigned to
            path = f'static/media/{glob.username}/%${glob.sideOfCard}-{icon.filename}'
            icon.save(path)
        except:
            return Response(status=500)

        settings = userCardSettings.query.filter_by(user=glob.username).first()
        if glob.sideOfCard == 'frontSideOfCard.html':
            settings.cardFrontIconPath = path
            glob.cardFrontIconPath = path
        else:
            settings.cardBackIconPath = path
            glob.cardBackIconPath = path

        db.session.commit()

        return redirect('/pageUpdater')
    else:
        # Returns response code: 415 (the user submitted an unsupported file type in the case that the user submits
        return Response(status=415)


# Takes the user's input for the border style and updates the border style database columns corresponding with
# with the correct side
@app.route('/borderStyleUpdater', methods=['POST'])
def borderStyleUpdater():
    try:
        style = request.form['borderOptionsChose'].lower()
        side = request.form['sideOfCard']
    except:
        return Response(status=400)

    glob.cardSideChecker(side)
    settings = userCardSettings.query.filter_by(user=glob.username).first()
    if glob.sideOfCard == 'frontSideOfCard.html':
        glob.cardFrontBorderStyle = style
        settings.cardFrontBorderStyle = style
    else:
        glob.cardBackBorderStyle = style
        settings.cardBackBorderStyle = style

    db.session.commit()
    return redirect('/pageUpdater')


# Updates the color of the border for the side of the card that the user accessed the border settings for
@app.route('/borderColorUpdater', methods=['POST'])
def borderColorUpdater():
    try:
        side = request.form['sideOfCard']
        borderColor = request.form['borderColor']
    except:
        return Response(status=400)

    glob.cardSideChecker(side)
    settings = userCardSettings.query.filter_by(user=glob.username).first()

    if glob.sideOfCard == 'frontSideOfCard.html':
        glob.cardFrontBorderCol = borderColor
        settings.cardFrontBorderCol = borderColor
    else:
        glob.cardBackBorderCol = borderColor
        settings.cardBackBorderCol = borderColor

    db.session.commit()

    return redirect('/pageUpdater')


# Purpose: Takes which options is being closed as an argument, and sets the display of that
# option to none
@app.route('/optionsCloser/<toolBoxOpt>', methods=['POST'])
def optionsCloser(toolBoxOpt=None):
    if toolBoxOpt == 'text':
        glob.visSettings['text'] = 'none'
    elif toolBoxOpt == 'icon':
        glob.visSettings['icon'] = 'none'
    elif toolBoxOpt == 'bord':
        glob.visSettings['bord'] = 'none'
    elif toolBoxOpt == 'cardT':
        glob.visSettings['cardT'] = 'none'
    else:
        return Response(status=500)
    return redirect('/pageUpdater')


# Runs the app if the app's name is equal to __main__
if '__main__' == __name__:
    app.run(debug=False)