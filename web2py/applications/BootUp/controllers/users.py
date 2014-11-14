__author__ = 'Y8191122'


def user():
    if request.args(0) == 'register':
        #Display the registration form with or without a separate billing address depending on users preferences
        if (request.post_vars.ccAddress is not None) & (request.post_vars.ccAddress != ''):
            form = registrationForm(True, request.post_vars)
        else:
            form = registrationForm(False, dict(request.post_vars))
    else:
        form=auth()
    return dict(form=form)


def registrationForm(ccAddress, values):
    """Returns a form for user registration"""
    #The requirements of the inputs are taken from the requirements of the database fields as
    #as they should be the same in most cases and there is no need for duplication.

    #A registration form consists of 4 parts 3 manditory and 1 optional
    #   General details (name, email, username, password)
    #   Address
    #   Credit Card
    #   Then optionally the address of the credit card (if different from the main address)
    form = FORM(DIV(DIV(H3('General Details:')),
                    DIV(LABEL('First Name:', _for='fName')),
                    DIV(INPUT(_name='fName', requires=db.auth_user.first_name.requires,
                              _value=getFieldValue(values, 'fName'))),
                    DIV(LABEL('Last Name:', _for='lName')),
                    DIV(INPUT(_name='lName', reqires=db.auth_user.last_name.requires,
                              _value=getFieldValue(values, 'lName'))),
                    DIV(LABEL('Email:', _for='email')),
                    DIV(INPUT(_name='email', _type='email', reqires=db.auth_user.email.requires,
                              _value=getFieldValue(values, 'email'))),
                    DIV(LABEL('Date of Birth:', _for='dob')),
                    DIV(INPUT(_name='dob', _type='date', reqires=db.auth_user.DateOfBirth.requires,
                              _value=getFieldValue(values, 'dob'))),
                    DIV(LABEL('Username:', _for='username')),
                    DIV(INPUT(_name='username', reqires=db.auth_user.username.requires,
                              _value=getFieldValue(values, 'username'))),
                    DIV(LABEL('Password:', _for='password')),
                    DIV(INPUT(_name='password', _type='password', reqires=db.auth_user.password.requires,
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
                              _value=getFieldValue(values, 'postCode'))),
                    _class='regForm',
                    _id='regForm2'),

                DIV(DIV(H3('Credit Card Details:')),
                    DIV(LABEL('Card Number:', _for='cardNumber')),
                    DIV(INPUT(_name='cardNumber', requires=db.CreditCards.CardNumber.requires,
                              _value=getFieldValue(values, 'cardNumber'))),
                    DIV(LABEL('Expiry Date:', _for='expDate')),
                    DIV(INPUT(_name='expDate', _type='date', requires=db.CreditCards.ExpiryDate.requires,
                              _value=getFieldValue(values, 'expDate'))),
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
    form.keepvalues = True
    return form

def getFieldValue(vars, key):
    if key in vars:
        return vars[key]
    return ''

