__author__ = 'Y8191122'


def profile():
    userID = session.user
    #If user manually types url and is not loged in redirect to login
    if userID is None:
        redirect(URL('default', 'user', args=['login']))

    user = db((db.Users.cardID == db.CreditCards.id) &
              (db.CreditCards.addressID == db.Addresses.id) &
              (db.Users.id == userID)).select().first()

    cardAddress = db(db.Addresses.id == user.CreditCards.addressID).select().first()

    pledges = db((db.Users.id == db.UserPledges.userID) &
                 (db.Bootables.id == db.UserPledges.bootID) &
                 (db.Bootables.id == db.Pledges.bootID) &
                 (db.Pledges.id == db.PledgeRewards.pledgeID) &
                 (db.Pledges.Value == db.UserPledges.Value) &
                 (db.Rewards.id == db.PledgeRewards.rewardID) &
                 (db.Users.id == userID)).select('Bootables.Title',
                                                 'Pledges.Name',
                                                 'Pledges.Value',
                                                 'Rewards.description',

                                                 distinct=True)

    return dict(user=user, cardAddress=cardAddress, pledges=pledges)

def editProfile():
    userID = session.user
    #If user manually types url and is not loged in redirect to login
    if userID is None:
        redirect(URL('default', 'user', args=['login']))
    return dict()



