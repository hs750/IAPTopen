__author__ = "Y8191122"


def index():
    return dict()


def user():
    """
    The user page, depending on the request.args it will display different forms relating to users
    :return: a dict containing: the form for the required operation
    """
    if request.args(0) == 'register':
        #Display the registration form with or without a separate billing address depending on users preferences
        if (request.post_vars.ccAddress is not None) & (request.post_vars.ccAddress != ''):
            form = registrationForm(True, request.post_vars)
        else:
            form = registrationForm(False, dict(request.post_vars))
        if form.accepts(request.post_vars, session):
            adrsID = db.Addresses.insert(StreetAddress=request.post_vars.sAddress,
                                            City=request.post_vars.city,
                                            Country=request.post_vars.country,
                                            PostCode=request.post_vars.postCode)
            ccAddressID = adrsID
            if (request.post_vars.ccAddress is not None) & (request.post_vars.ccAddress != ''):
                ccAddressID = db.Addresses.insert(StreetAddress=request.post_vars.ccAddress,
                                                  City=request.post_vars.ccCity,
                                                  Country=request.post_vars.ccCountry,
                                                  PostCode=request.post_vars.ccPostCode)

            ccID = db.CreditCards.insert(CardNumber=request.post_vars.cardNumber,
                                         ExpiryDate=request.post_vars.expDate,
                                         IDCode=request.post_vars.cardID,
                                         addressID=ccAddressID)
            db.Users.insert(FirstName=request.post_vars.fName,
                            LastName=request.post_vars.lName,
                            Email=request.post_vars.email,
                            Username=request.post_vars.username,
                            Password=request.post_vars.password,
                            DateOfBirth=request.post_vars.dob,
                            addressID=adrsID,
                            cardID=ccID)
            response.flash = 'Successfully Registered'
        elif form.errors:
            response.flash = 'There was a problem with something you entered'
        else:
            response.flash = 'Please enter your details bellow:'
    elif request.args(0) == 'login':
        #Display the login form
        form = getLoginForm()
        if form.accepts(request.post_vars, session):
            print(request.post_vars.username)
            userLogin = db(db.Users.Username == request.post_vars.username).select(db.Users.id, db.Users.Password)
            print(userLogin)
            userLogin = userLogin[0]
            print(userLogin)
            if userLogin is not None:
                if userLogin.Password == request.post_vars.password:
                    #When logged in store user ID and redirect to home page
                    session.user = userLogin.id
                    redirect(URL('default', 'index'))
                else:
                    response.flash = 'Incorrect Password'
            else:
                response.flash = 'User Not Found!'
        elif form.errors:
            response.flash = 'Username or Password incorrectly entered'
        else:
            response.flash = 'Please enter your username and password'
    elif request.args(0) == 'logout':
        #Log the user out and redirect home
        session.user = None
        redirect(URL('default', 'index'))
        form=FORM()
    else:
        form=FORM()
    return dict(form=form)


def registrationForm(ccAddress, values):
    """Returns a form for user registration

    :param ccAddress: Include a seperate address as billing address
    :param values: input values taken from form (for re-population)
    :return: The form to be displayed
    """

    #The requirements of the inputs are taken from the requirements of the database fields as
    #as they should be the same in most cases and there is no need for duplication.

    #A registration form consists of 4 parts 3 manditory and 1 optional
    #   General details (name, email, username, password)
    #   Address
    #   Credit Card
    #   Then optionally the address of the credit card (if different from the main address)
    form = FORM(DIV(DIV(H3('General Details:')),
                    DIV(LABEL('First Name:', _for='fName')),
                    DIV(INPUT(_name='fName', requires=db.Users.FirstName.requires,
                              _value=getFieldValue(values, 'fName'))),
                    DIV(LABEL('Last Name:', _for='lName')),
                    DIV(INPUT(_name='lName', reqires=db.Users.LastName.requires,
                              _value=getFieldValue(values, 'lName'))),
                    DIV(LABEL('Email:', _for='email')),
                    DIV(INPUT(_name='email', _type='email', reqires=db.Users.Email.requires,
                              _value=getFieldValue(values, 'email'))),
                    DIV(LABEL('Date of Birth:', _for='dob')),
                    DIV(INPUT(_name='dob', _type='date', reqires=db.Users.DateOfBirth.requires,
                              _value=getFieldValue(values, 'dob', 'DD-MM-YYY'))),
                    DIV(LABEL('Username:', _for='username')),
                    DIV(INPUT(_name='username', reqires=db.Users.Username.requires,
                              _value=getFieldValue(values, 'username'))),
                    DIV(LABEL('Password:', _for='password')),
                    DIV(INPUT(_name='password', _type='password', reqires=db.Users.Password.requires,
                              _value=getFieldValue(values, 'fName'))),
                    DIV(LABEL('Confirm Password:', _for='password_two')),
                    DIV(INPUT(_name="password_two", _type="password",
                              requires=IS_EXPR('value==%s' % repr(request.vars.password),
                                               error_message='Passwords do not match'),
                              _value=getFieldValue(values, 'password_two'))),
                    _class='regForm',
                    _id='regForm1'),
                DIV(DIV(H3('Address:')),
                    DIV(LABEL('Street Address:', _for='sAddress')),
                    DIV(TEXTAREA(_name='sAddress', requires=db.Addresses.StreetAddress.requires,
                                 _value=getFieldValue(values, 'sAddress'))),
                    DIV(LABEL('City:', _for='city')),
                    DIV(INPUT(_name='city', requires=db.Addresses.City.requires,
                              _value=getFieldValue(values, 'city'))),
                    DIV(LABEL('Country:', _for='country')),
                    DIV(INPUT(_name='country', requires=db.Addresses.Country.requires,
                              _value=getFieldValue(values, 'country'))),
                    DIV(LABEL('Post Code:', _for='postCode')),
                    DIV(INPUT(_name='postCode', requires=db.Addresses.PostCode.requires,
                              _value=getFieldValue(values, 'postCode', 'AB01 2CD'))),
                    _class='regForm',
                    _id='regForm2'),

                DIV(DIV(H3('Credit Card Details:')),
                    DIV(LABEL('Card Number:', _for='cardNumber')),
                    DIV(INPUT(_name='cardNumber', requires=db.CreditCards.CardNumber.requires,
                              _value=getFieldValue(values, 'cardNumber'))),
                    DIV(LABEL('Expiry Date:', _for='expDate')),
                    DIV(INPUT(_name='expDate', _type='date', requires=db.CreditCards.ExpiryDate.requires,
                              _value=getFieldValue(values, 'expDate', 'DD-MM-YYYY'))),
                    DIV(LABEL('Card ID Code:', _for='cardID')),
                    DIV(INPUT(_name='cardID', requires=db.CreditCards.IDCode.requires,
                              _value=getFieldValue(values, 'cardID'))),
                    _class='regForm',
                    _id='regForm3')
                )

    if not ccAddress:
        form.append(INPUT(_name='ccAddress', _type='submit', _value='Use Separate Billing Address'))
    else:
        form.append(DIV(DIV(H3('Billing Address')),
                        DIV(LABEL('Street Address:', _for='ccAddress')),
                        DIV(TEXTAREA(_name='ccAddress', requires=db.Addresses.StreetAddress.requires,
                                     _value=getFieldValue(values, 'ccAddress'))),
                        DIV(LABEL('City:', _for='ccCity')),
                        DIV(INPUT(_name='ccCity', requires=db.Addresses.City.requires,
                                  _value=getFieldValue(values, 'ccCity'))),
                        DIV(LABEL('Country:', _for='ccCountry')),
                        DIV(INPUT(_name='ccCountry', requires=db.Addresses.Country.requires,
                                  _value=getFieldValue(values, 'ccCountry'))),
                        DIV(LABEL('Post Code:', _for='ccPostCode')),
                        DIV(INPUT(_name='ccPostCode', requires=db.Addresses.PostCode.requires,
                                  _value=getFieldValue(values, 'ccPostCode'))),
                        _class='regForm',
                        _id='regForm4'
                        ))
        form.append(INPUT(_name='ccCancel', _type='submit', _value='Cancel billing address'))

    form.append(INPUT(_name='submit', _type='submit'))
    return form


def getFieldValue(vars, key, default=''):
    """ Get the value of a field from a dictionary.
    :param vars: a dictionary of field names to their input values
    :param key: the key you are looking for in vars
    :param default: the default to use if not found (default default is ''
    :return: the value from vars pointed to by key or default
    """
    if key in vars:
        return vars[key]
    return default


def getLoginForm():
    form = FORM(DIV(H3('Login:')),
                DIV(LABEL('Username:', _for='username')),
                DIV(INPUT(_name='username', requires=IS_NOT_EMPTY())),
                DIV(LABEL('Password:', _for='password')),
                DIV(INPUT(_name='password', _type='password', requires=IS_NOT_EMPTY())),
                DIV(INPUT(_name='login', _type='submit'))
                )
    return form


