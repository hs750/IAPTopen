__author__ = "Y8191122"


def index():
    """
    The home page of BootUP
    :return: the 5 newest bootables and the top5 closest to completion
    """
    response.subtitle = 'Home'
    newest = db(db.Bootables.id>0).select(orderby=~db.Bootables.id, limitby=(0, 5))
    top5 = getTop5()
    return dict(newest=newest, top=top5)


def view():
    """
    View a particular bootable,
    which bootable is determined by request.args(0) which is the bootID
    :return: booable information,
            the percentage complete,
            to total pledged,
            the users who pledged with their pledge amount,
            the form allowing users to pledge,
            and the image of the bootable
    """
    bootID = request.args(0)
    bootable = db(db.Bootables.id == bootID).select().first()
    response.subtitle = bootable.Title

    #The bootable image
    image = IMG(_src=URL('bootableImage', args=[bootable.Image]))

    total = getTotalPledged(bootID)
    completion = getCompletionPercentage(bootID)

    #Collect the values of pledges available for this bootable
    pledgeValues = db(db.Pledges.bootID == bootID).select('Value')
    values = []
    for item in pledgeValues:
        values += [item.Value]

    pledgeForm = FORM(SELECT(values, _name='pledgeValue'),
                      INPUT(_type='submit', _name='pledgeSubmit', _value='Pledge!'),
                      _name='userPledgeForm',
                      _class='form-inline')
    #must to a form.accepts on every path though the code to make sure form.form key and session.formkey[formname]
    #match, otherwise the form will fail to submit
    pledgeForm.accepts(dict(), session, formname='userPledgeForm')
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
            response.flash = 'You can pledge to this Bootable below'
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
    """
    The search page for BootUP
    :return: the search results
    """
    response.subtitle = 'Search Results'
    search = request.vars.search
    cat = request.vars.cat
    #Search in all categories, or a specific one
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
    """
    Get the image of a bootable. Which bootable to get is stored in request.
    This method should only be called as part of a URL for displaying a bootable image on the page
    :return: the bootable image
    """
    return response.download(request, db)


