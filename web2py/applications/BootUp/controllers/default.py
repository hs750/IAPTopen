__author__ = "Y8191122"
# This default is for general site functionality, not requiring user login for the most part

def index():
    """
    The home page of BootUP
    :return: the 5 newest bootables and the top5 closest to completion,
            the bootables total pledged and percentage complete
    """
    response.subtitle = 'Home'
    #The newest bootables assumes higher id = newer, bootable cant be not available
    newest = db((db.Bootables.id>0) &
                (db.Bootables.State != bootableStates[0])).select(orderby=~db.Bootables.id, limitby=(0, 5))
    top5 = getTop5()

    totals = dict()
    percentages = dict()
    for item in newest:
        totals[item.id] = getTotalPledged(item.id)
        percentages[item.id] = getCompletionPercentage(item.id)

    for item in top5:
        totals[item.id] = getTotalPledged(item.id)
        percentages[item.id] = getCompletionPercentage(item.id)

    return dict(newest=newest, top=top5, totals=totals, percent=percentages)


def view():
    """
    View a particular bootable,
    which bootable is determined by request.args(0) which is the bootID
    :return: booable information,
            the percentage complete,
            to total pledged,
            the users who pledged with their pledge amount,
            the form allowing users to pledge,
            and the image of the bootable,
            the rewards for this bootable,
            the username of the bootble owner,
            the rewards for each user,
            whether the current logged in user has pledged to this bootble
    """
    bootID = request.args(0)
    bootable = db(db.Bootables.id == bootID).select().first()
    #Cant view if not available, owning user can see for 'preview'

    if (bootable is None) or ((bootable.State == bootableStates[0]) & (bootable.userID != session.user)):
        redirect(URL('index'))
    response.subtitle = bootable.Title
    owner = db(db.Users.id == bootable.userID).select('FirstName', 'LastName').first()


    #The bootable image
    image = IMG(_src=URL('bootableImage', args=[bootable.Image]))

    total = getTotalPledged(bootID)
    completion = getCompletionPercentage(bootID)

    rewardQuery = (db.Pledges.bootID == bootID) & \
                    (db.Pledges.id == db.PledgeRewards.pledgeID) & \
                    (db.Rewards.id == db.PledgeRewards.rewardID)
    rewards = db(rewardQuery).select('Pledges.id',
                                      'Pledges.Name',
                                      'Pledges.Value',
                                      'Rewards.Description',
                                      orderby=db.Pledges.Value)

    usersPledgedQuery = (db.Bootables.id == bootID) & \
                        (db.Bootables.id == db.UserPledges.bootID) & \
                        (db.UserPledges.userID == db.Users.id)

    #Collect the values of pledges available for this bootable
    pledgeValues = db(db.Pledges.bootID == bootID).select('Value')
    values = []
    for item in pledgeValues:
        values += [item.Value]

    pledgeForm = FORM(SELECT(values, _name='pledgeValue'),
                      INPUT(_type='submit', _name='pledgeSubmit', _value='Pledge!', _class='btn btn-success'),
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

            #If the pledge tipped bootable over the edge of its funding goal
            #Move bootable to funded state
            percentageComplete = getCompletionPercentage(bootID)
            if percentageComplete >= 100:
                bootable.State = bootableStates[2]
                bootable.update_record()
            response.flash = 'You have successfully pledged!'
        elif pledgeForm.errors:
            response.flash = 'There was a problem with your pledge'

    userRewards = db((db.UserPledges.Value == db.Pledges.Value) &
                     usersPledgedQuery &
                     rewardQuery).select('Users.id', 'Rewards.Description')

    #Get this after submition of form so that screen updated on refresh
    usersPledged = db(usersPledgedQuery).select('Users.id', 'Users.Username',
                                                            'UserPledges.Value',
                                                            'Users.FirstName',
                                                            'Users.LastName')

    currentUserPledged = False
    for up in usersPledged:
        currentUserPledged = currentUserPledged or (up.Users.id == session.user)

    return dict(bootable=bootable,
                total=total,
                percent=completion,
                users=usersPledged,
                pledgeForm=pledgeForm,
                image=image,
                rewards=rewards,
                owner=owner,
                userRewards=userRewards,
                currentUserPledged=currentUserPledged)


def search():
    """
    The search page for BootUP
    :return: the search results, the total pledges and percentages for each item
    """
    search = request.vars.search
    cat = request.vars.cat
    response.subtitle = 'Search Results: ' + search + ' in ' + cat
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
    totals = dict()
    percentages = dict()
    for item in searchResults:
        totals[item.id] = getTotalPledged(item.id)
        percentages[item.id] = getCompletionPercentage(item.id)

    return dict(searchResults=searchResults, totals=totals, percent=percentages)

def bootableImage():
    """
    Get the image of a bootable. Which bootable to get is stored in request.
    This method should only be called as part of a URL for displaying a bootable image on the page
    :return: the bootable image
    """
    return response.download(request, db)


def getTop5():
    """
    Get the top 5 bootable closest to completion, in the order of most complete first
    :return: the top 5 bootables
    """
    # Get the pledges for each bootable, but only the bootables that are not not open
    pledges = db((db.UserPledges.bootID == db.Bootables.id) &
                 (db.Bootables.State != bootableStates[0])).select('Bootables.id',
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
    sortedPercentTemp = sorted(percent.items(), key=operator.itemgetter(1), reverse=True)
    sortedPercent = []

    #Dont show funded projects in top 5 (otherwise top5 will only end up being the completed projects
    for item in sortedPercentTemp:
        if item[1] < 1:
            sortedPercent += [item]

    sortedKeys = []

    #pick out the bootIDs of the top 5 bootables
    for i in range(0, min(len(sortedPercent), 5)):
        sortedKeys += [sortedPercent[i][0]]

    #If there are no bootables with pledges do a query which will return noting
    query = (db.Bootables.State == 'No State')
    if len(sortedKeys) > 0:
        query = (db.Bootables.id == sortedKeys[0])
        for i in range(1, len(sortedKeys)):
            query |= (db.Bootables.id == sortedKeys[i])

    top5 = db(query).select(db.Bootables.ALL)

    #Add the percentage to the return
    for item in top5:
        item['percent'] = percent.get(item.id, 0)

    return top5




