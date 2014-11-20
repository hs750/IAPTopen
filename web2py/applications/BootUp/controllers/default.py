__author__ = "Y8191122"


def index():
    newest = db(db.Bootables.id>0).select(orderby=~db.Bootables.id, limitby=(0, 5))
    top5 = getTop5()
    return dict(newest=newest, top=top5)


def view():
    """
    View a particular bootable,
    which bootable is determined by request.args(0) which is the bootID
    :return: booable information, the percentage complete and the users who pledged with their pledge amount
    """
    bootID = request.args(0)
    bootable = db(db.Bootables.id == bootID).select()

    image = IMG(_src=URL('bootableImage', args=[bootable.first().Image]))

    total = getTotalPledged(bootID)
    completion = getCompletionPercentage(bootID)

    pledgeValues = db(db.Pledges.bootID == bootID).select('Value')
    values = []
    for item in pledgeValues:
        values += [item.Value]

    print(values)
    pledgeForm = FORM(SELECT(values, _name='pledgeValue'),
                      INPUT(_type='submit', _name='pledgeSubmit', _value='Pledge!'),
                      _name='userPledgeForm',
                      _class='form-inline')

    if session.user is not None:
        #Only do anything with the form if user logged in
        if pledgeForm.accepts(request.post_vars, session, formname='userPledgeForm'):
            db.UserPledges.insert(userID=session.user,
                                  bootID=bootID,
                                  Value=request.post_vars.pledgeValue)
            response.flash = 'You have successfully pledged!'
        elif pledgeForm.errors:
            response.flash = 'There was a problem with your pledge'
    else:
        #Should never get here as form shouldnt be displayed if no user signed in
        response.flash = 'Must be signed in to pledge!'

    #Get this after submition of form so that screen updated on refresh
    usersPledged = db((db.Bootables.id == bootID) &
                      (db.Bootables.id == db.UserPledges.bootID) &
                      (db.UserPledges.userID == db.Users.id)).select('Users.Username', 'UserPledges.Value')

    return dict(bootable=bootable,
                total=total,
                percent=completion,
                users=usersPledged,
                pledgeForm=pledgeForm,
                image=image)

def search():
    search = request.vars.search
    cat = request.vars.cat
    if cat == 'All':
        searchResults = db(((db.Bootables.Title.contains(search)) |
                            (db.Bootables.ShortDescription.contains(search))) &
                            #Cant be not available
                           (db.Bootables.State != bootableStates[0])).select()
    else:
        searchResults = db(((db.Bootables.Title.contains(search)) |
                            (db.Bootables.ShortDescription.contains(search))) &
                           (db.Bootables.State != bootableStates[0]) &
                            #Cant be not available
                           (db.Bootables.Category == cat)).select()
    return dict(searchResults=searchResults)

def bootableImage():
    return response.download(request, db)


