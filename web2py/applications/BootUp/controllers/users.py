__author__ = 'Y8191122'


def user():
    if request.args(0) == 'register':
        if (request.post_vars.ccAddress is not None) & (request.post_vars.ccAddress != ''):
            form = registrationForm(True)
        elif request.post_vars.ccCancel is not None:
            form = registrationForm(False)
        else:
            form = registrationForm(False)
    else:
        form=auth()
    return dict(form=form)


def registrationForm(ccAddress):
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
                    DIV(INPUT(_name='fName', requires=db.auth_user.first_name.requires)),
                    DIV(LABEL('Last Name:', _for='lName')),
                    DIV(INPUT(_name='lName', reqires=db.auth_user.last_name.requires)),
                    DIV(LABEL('Email:', _for='email')),
                    DIV(INPUT(_name='email', _type='email', reqires=db.auth_user.email.requires)),
                    DIV(LABEL('Date of Birth:', _for='dob')),
                    DIV(INPUT(_name='dob', _type='date', reqires=db.auth_user.DateOfBirth.requires)),
                    DIV(LABEL('Username:', _for='username')),
                    DIV(INPUT(_name='username', reqires=db.auth_user.username.requires)),
                    DIV(LABEL('Password:', _for='password')),
                    DIV(INPUT(_name='password', _type='password', reqires=db.auth_user.password.requires)),
                    DIV(LABEL('Confirm Password:', _for='password_two')),
                    DIV(INPUT(_name="password_two", _type="password",
                              requires=IS_EXPR('value==%s' % repr(request.vars.password),
                                               error_message='Passwords do not match'))),
                    _class='regForm',
                    _id='regForm1'),
                DIV(DIV(H3('Address:')),
                    DIV(LABEL('Street Address:', _for='sAddress')),
                    DIV(TEXTAREA(_name='sAddress', requires=db.Addresses.StreetAddress.requires)),
                    DIV(LABEL('City:', _for='city')),
                    DIV(INPUT(_name='city', requires=db.Addresses.City.requires)),
                    DIV(LABEL('Country:', _for='country')),
                    DIV(INPUT(_name='country', requires=db.Addresses.Country.requires)),
                    DIV(LABEL('Post Code:', _for='postCode')),
                    DIV(INPUT(_name='postCode', requires=db.Addresses.PostCode.requires)),
                    _class='regForm',
                    _id='regForm2'),

                DIV(DIV(H3('Credit Card Details:')),
                    DIV(LABEL('Card Number:', _for='cardNumber')),
                    DIV(INPUT(_name='cardNumber', requires=db.CreditCards.CardNumber.requires)),
                    DIV(LABEL('Expiry Date:', _for='expDate')),
                    DIV(INPUT(_name='expDate', _type='date', requires=db.CreditCards.ExpiryDate.requires)),
                    DIV(LABEL('Card ID Code:', _for='cardID')),
                    DIV(INPUT(_name='cardID', requires=db.CreditCards.IDCode.requires)),
                    _class='regForm',
                    _id='regForm3')
                )

    if not ccAddress:
        form.append(INPUT(_name='ccAddress', _type='submit', _value='Use Separate Billing Address'))
    else:
        form.append(DIV(DIV(H3('Billing Address')),
                        DIV(LABEL('Street Address:', _for='ccAddress')),
                        DIV(TEXTAREA(_name='ccAddress', requires=db.Addresses.StreetAddress.requires)),
                        DIV(LABEL('City:', _for='ccCity')),
                        DIV(INPUT(_name='ccCity', requires=db.Addresses.City.requires)),
                        DIV(LABEL('Country:', _for='ccCountry')),
                        DIV(INPUT(_name='ccCountry', requires=db.Addresses.Country.requires)),
                        DIV(LABEL('Post Code:', _for='ccPostCode')),
                        DIV(INPUT(_name='ccPostCode', requires=db.Addresses.PostCode.requires)),
                        _class='regForm',
                        _id='regForm4'
                        ))
        form.append(INPUT(_name='ccCancel', _type='submit', _value='Cancel billing address'))

    form.append(INPUT(_name='submit', _type='submit'))
    form.keepvalues = True
    return form
