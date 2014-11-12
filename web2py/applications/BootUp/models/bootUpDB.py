__author__ = 'Y8191122'

db = DAL('sqlite://bootUpDB.db')

"""
    All tables and fields are defined using a standard naming convention.
    Tables and Fields use Camel Case. All fields except those which are foreign keys start capitalised.
    All tables start capitalised.

    The default web2py primary key ID is used in all tabled except where explicitly stated (which has type Long)
"""

db.define_table('Bootables',
                Field('Title'),
                Field('ShortDescription'),
                Field('FundingGoal'),
                Field('Category'),
                Field('Image'),
                Field('LongDescription'),
                Field('PersonalStory'),
                Field('State'),
                Field('userID')
                )

db.define_table('CreditCards',
                Field('CardNumber'),
                Field('ExpiryDate'),
                Field('IDCode'),
                Field('addressID')
                )

db.define_table('Addresses',
                Field('StreetAddresses'),
                Field('City'),
                Field('Country'),
                Field('PostCode')
                )

db.define_table('Pledge',
                Field('Name'),
                Field('Value'),
                Field('bootID')
                )

db.define_table('Reward',
                Field('description')
                )

db.define_table('UserPledge',
                Field('bootID'),
                Field('Value')
                )

"""
    The Users table is not explicitly defined. Instead I use the authentication library built into web2py with
    some fields added.
"""

auth = Auth(db)
"""
    Custom fields added to the web2py authentication.
    Fields already provided by web2py authentication:
        username, email, name (split into first and last)
"""
auth.settings.extra_fields['auth_user'] = [
    Field('DateOfBirth'),
    Field('addressID'),
    Field('cardID')
]
auth.define_tables(username=True) #Allows login using username
