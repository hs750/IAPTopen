__author__ = 'Y8191122'

db = DAL('sqlite://bootUpDB.db')

"""
    All tables and fields are defined using a standard naming convention.
    Tables and Fields use Camel Case. All fields except those which are foreign keys start capitalised.
    All tables start capitalised.

    The default web2py primary key ID is used in all tabled except where explicitly stated (which has type Long)
"""

db.define_table('Addresses',
                Field('StreetAddress', 'text', requires=IS_NOT_EMPTY()),
                Field('City', 'string', requires=IS_NOT_EMPTY()),
                Field('Country', 'string', requires=IS_NOT_EMPTY()),
                Field('PostCode', 'string', requires=[IS_NOT_EMPTY(), IS_MATCH('[A-Z]{2}[0-9]{2} [0-9][A-Z]{2}',
                                                                               error_message='Not a valid Post Code')],
                      comment='Must match the form AB01 2CD')
                )

db.define_table('CreditCards',
                Field('CardNumber', 'string', length=20, requires=[IS_NOT_EMPTY(), IS_MATCH('[0-9]{12}')]),
                Field('ExpiryDate', 'date',
                      requires=[IS_NOT_EMPTY(), IS_DATE()]),
                Field('IDCode', 'string', length=3, requires=[IS_NOT_EMPTY(), IS_MATCH('[0-9]{3}')]),
                Field('addressID', db.Addresses, requires=IS_NOT_EMPTY())
                )

db.define_table('Users',
                Field('FirstName', 'string', requires=IS_NOT_EMPTY()),
                Field('LastName', 'string', requires=IS_NOT_EMPTY()),
                Field('Email', 'string', requires=IS_EMAIL()),
                Field('Username', 'string', unique=True),
                Field('Password', 'string', requires=IS_NOT_EMPTY()),
                Field('DateOfBirth', 'date',
                      requires=[IS_NOT_EMPTY(), IS_DATE()]),
                Field('addressID', db.Addresses, requires=IS_NOT_EMPTY()),
                Field('cardID', db.CreditCards, requires=IS_NOT_EMPTY()))
db.Users.Username.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.Users.Username, 'Username already taken')]

db.define_table('Bootables',
                Field('Title', 'string', requires=IS_NOT_EMPTY()),
                Field('ShortDescription', 'string', length=120, comment='120 characters or less',
                      requires=IS_NOT_EMPTY()),
                #The maximum value a bootable can have as its goal is 999,999,999.99
                Field('FundingGoal', 'decimal(11,2)', requires=[IS_NOT_EMPTY(), IS_DECIMAL_IN_RANGE(0, 1e100)]),
                Field('Category', 'string',
                      requires=IS_IN_SET(['Art', 'Comics', 'Crafts', 'Fashion', 'Film',
                                          'Games', 'Music', 'Photography', 'Technology'])),
                Field('Image', 'upload', requires=[IS_IMAGE(), IS_NOT_EMPTY()]),
                Field('LongDescription', 'text', requires=IS_NOT_EMPTY()),
                Field('PersonalStory', 'text', requires=IS_NOT_EMPTY()),
                Field('State', 'string',
                      requires=IS_IN_SET(['Not Available', 'Open for Pledges', 'Funded', 'Not Funded'])),
                Field('userID', db.Users, requires=IS_NOT_EMPTY())
                )

pledge_value_type = 'decimal(8,2)'  # maximum value of 999,999.99
db.define_table('Pledges',
                Field('Name', 'string', requires=IS_NOT_EMPTY()),
                Field('Value', pledge_value_type, requires=IS_NOT_EMPTY()),
                Field('bootID', db.Bootables, requires=IS_NOT_EMPTY())
                )

db.define_table('Rewards',
                Field('description', 'text', requires=IS_NOT_EMPTY())
                )

db.define_table('PledgeRewards',
                Field('pledgeID', db.Pledges, requires=IS_NOT_EMPTY()),
                Field('rewardID', db.Rewards, requires=IS_NOT_EMPTY()),
                primarykey=['pledgeID', 'rewardID']
                )

db.define_table('UserPledges',
                Field('userID', db.Users, requires=IS_NOT_EMPTY()),
                Field('bootID', db.Bootables, requires=IS_NOT_EMPTY()),
                Field('Value', pledge_value_type, requires=IS_IN_DB(db, 'Pledges.Value', '%(Value)s')),
                primarykey=['userID', 'bootID']
                )


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