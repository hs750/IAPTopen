__author__ = 'Y8191122'
import operator
from decimal import *

db = DAL('sqlite://bootUpDB.db')

"""
    All tables and fields are defined using a standard naming convention.
    Tables and Fields use Camel Case. All fields except those which are foreign keys start capitalised.
    All tables start capitalised.

    The default web2py primary key ID is used in all tabled except where explicitly stated (which has type Long)
"""

bootableCategories = ['Art', 'Comics', 'Crafts', 'Fashion', 'Film', 'Games', 'Music', 'Photography', 'Technology']
bootableStates = ['Not Available', 'Open for Pledges', 'Funded', 'Not Funded']

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
                Field('FundingGoal', 'decimal(11,2)', requires=[IS_NOT_EMPTY(), IS_DECIMAL_IN_RANGE(0, 1e9)]),
                Field('Category', 'string',
                      requires=IS_IN_SET(bootableCategories)),
                Field('Image', 'upload', requires=[IS_IMAGE(), IS_NOT_EMPTY()]),
                Field('LongDescription', 'text', requires=IS_NOT_EMPTY()),
                Field('PersonalStory', 'text', requires=IS_NOT_EMPTY()),
                Field('State', 'string',
                      requires=IS_IN_SET(bootableStates)),
                Field('userID', db.Users, requires=IS_NOT_EMPTY())
                )

pledge_value_type = 'decimal(11,2)'  # maximum value of 999,999,999.99
db.define_table('Pledges',
                Field('Name', 'string', requires=IS_NOT_EMPTY()),
                Field('Value', pledge_value_type, requires=[IS_NOT_EMPTY(), IS_DECIMAL_IN_RANGE(0, 1e9)]),
                Field('bootID', db.Bootables, requires=IS_NOT_EMPTY())
                )

db.define_table('Rewards',
                Field('description', 'text', requires=IS_NOT_EMPTY())
                )

#Cant use composite keys as DAL has shaky support for them
#It is possible to add records but not possible to update / delete them
#Therefore must use the default id primary key
#Set what would normally be the composite key fields to notnull=True to give them some constraint
db.define_table('PledgeRewards',
                Field('pledgeID', db.Pledges, requires=IS_NOT_EMPTY(), notnull=True),
                Field('rewardID', db.Rewards, requires=IS_NOT_EMPTY(), notnull=True)
                )

db.define_table('UserPledges',
                Field('userID', db.Users, requires=IS_NOT_EMPTY(), notnull=True),
                Field('bootID', db.Bootables, requires=IS_NOT_EMPTY(), notnull=True),
                Field('Value', pledge_value_type, requires=IS_IN_DB(db, 'Pledges.Value'))
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

def getCompletionPercentage(bootID):
    pledges = db(db.UserPledges.bootID == bootID).select('UserPledges.Value', 'Bootables.FundingGoal')
    total = Decimal(0)
    for item in pledges:
        total += item.UserPledges.Value
    print(total)
    percentageComplete = 0
    if pledges.first() is not None:
        percentageComplete = total / pledges.first().Bootables.FundingGoal

    return percentageComplete

def getTop5():
    pledges = db(db.UserPledges.bootID == db.Bootables.id).select('Bootables.id',
                                                                  'UserPledges.Value', 'Bootables.FundingGoal')

    totals = dict()
    goals = dict()
    #Get total of pledges for each bootable
    for pledge in pledges:
        total = totals.get(pledge.Bootables.id, Decimal(0))
        total += pledge.UserPledges.Value
        totals[pledge.Bootables.id] = total
        goals[pledge.Bootables.id] = pledge.Bootables.FundingGoal

    percent = dict()
    #Calculate the percent for each bootable
    for totalID in totals.keys():
        percent[totalID] = totals[totalID] / goals[totalID]

    #list of bootID, percent complete pairs in order, most complete first
    sortedPercent = sorted(percent.items(), key=operator.itemgetter(1), reverse=True)
    sortedKeys = []

    #pick out the bootIDs of the top 5 bootables
    for i in range(0, min(len(sortedPercent), 5)):
        sortedKeys += [sortedPercent[i][0]]

    query = (db.Bootables.id == sortedKeys[0])
    for i in range(1, len(sortedKeys)):
        query |= (db.Bootables.id == sortedKeys[i])
    top5 = db(query).select(db.Bootables.ALL)
    print top5
    #Add the percentage to the return
    for item in top5:
        item['percent'] = percent[item.id]

    return top5

