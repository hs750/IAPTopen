__author__='Y8191122'

def index():
    return dict()


def create():
    """
    Create bootables (the basic bootable information
    :return: bootable creation form
    """
    #User must be logged in
    if session.user is None:
        redirect(URL('default', 'user', args=['login']))
    else:
        form = getBootableForm(request.post_vars)

        if form.accepts(request.post_vars, session):
            image = db.Bootables.Image.store(request.post_vars.image.file, request.post_vars.image.filename)
            bootableID = db.Bootables.insert(Title=request.post_vars.title,
                                             ShortDescription=request.post_vars.shortDesc,
                                             FundingGoal=request.post_vars.fundGoal,
                                             Category=request.post_vars.cat,
                                             Image=image,
                                             LongDescription=request.post_vars.longDesc,
                                             PersonalStory=request.post_vars.story,
                                             State=bootableStates[0],
                                             userID=session.user
                                             )
            response.flash = 'Bootable successfully created'
            #After bootable created proceed to edit it (add pledges and rewards)
            redirect(URL('bootables', 'createPledges', args=[bootableID]))
        elif form.errors:
            response.flash = 'There was a problem with your entry'
        else:
            response.flash = 'Please enter your Bootable details'
    return dict(form=form)


def createPledges():
    """
    Create pledges to go with a bootable
    request.args(0) contains the bootID of the bootables these pledges are associated with
    :return: pledge creation form
    """
    session.resubmit = ''
    #Number of rewards a pledge has
    numRewards = request.post_vars.numRewards
    if numRewards is None:
        numRewards = 1
    else:
        numRewards = int(numRewards)
        if numRewards < 1:
            numRewards = 0

    #Whether the pledge is inheriting rewards from lesser valued pledges
    inheritRewards = request.post_vars.inheritRewards
    if inheritRewards is None:
        inheritRewards = False

    form = getPledgeForm(request.post_vars, numRewards, inheritRewards)

    if (request.post_vars.addReward is not None) & (request.post_vars.addReward != ''):
        #Add a reward to the form
        numRewards += 1
        form = getPledgeForm(request.post_vars, numRewards, inheritRewards)
    elif (request.post_vars.delReward is not None) & (request.post_vars.delReward != ''):
        #if user added too many rewards can remove the lase one
        numRewards -= 1
        form = getPledgeForm(request.post_vars, numRewards, inheritRewards)
    elif (request.post_vars.inheritPledges is not None) & (request.post_vars.inheritPledges != ''):
        #Get rewards eligible for inheritance
        if (request.post_vars.value is None) or (request.post_vars.value == ''):
            form.errors.value = 'Must enter a value to inherit pledge rewards'
            response.flash = 'Unable to inherit rewards'
            form = getPledgeForm(request.post_vars, numRewards, False)
        else:
            form = getPledgeForm(request.post_vars, numRewards, True)
    elif form.accepts(request.post_vars, session, formname='pledgeForm'):
        print('accepted')
        pledgeId = db.Pledges.insert(Name=request.post_vars.name,
                                     Value=request.post_vars.value,
                                     bootID=request.args(0)
                                     )

        for i in range(1, numRewards + 1):
            rewardId = db.Rewards.insert(description=request.post_vars['description-' + str(i)])
            db.PledgeRewards.insert(pledgeID=pledgeId,
                                    rewardID=rewardId,
                                    Inherited=False)

        inheritCount = request.post_vars.inheritCount
        if inheritCount is not None:
            inheritCount = int(inheritCount)
            for i in range(1, inheritCount + 1):
                rewardId = request.post_vars['rewardID-' + str(i)]
                if (request.post_vars['reward-' + str(rewardId)] is not None) and \
                        (request.post_vars['reward-'+str(rewardId)] == 'on'):
                    db.PledgeRewards.insert(pledgeID=pledgeId,
                                            rewardID=rewardId,
                                            Inherited=True)

        session.flash = 'Pledge ' + request.post_vars.name + ' saved'
        response.flash = session.flash
        #Continue to the next pledge
        if (request.post_vars.nextPledge is not None) & (request.post_vars.nextPledge != ''):
            redirect(URL(args=request.args))
        else:
            redirect(URL('default', 'index'))
            #TODO redirect to bootable edit page
    elif form.errors:
        response.flash = 'There was a problem with what you entered.'
    else:
        if request.post_vars.name is not None:
            if (request.post_vars.nextPledge is not None) & (request.post_vars.nextPledge != ''):
                session.resubmit = 'nextPledge'
            else:
                session.resubmit = 'doneSubmit'
            #For some reason when the inheritance check boxes are in the form, the form wont be accepted the first time
            #But will also not populate the errors variable so there is no way to know what is wrong.
            #So as a temporary measure added this message so the user has some feedback/forward on what to do.
            #Some javascript resubmits the form so this message is only needed if javascript is not enabled
            response.flash = 'Please submit the form again.'
        else:
            response.flash = 'Please enter Pledge details'
    return dict(form=form)


def getBootableForm(values, includeImage=True, submitText='Add pledge values'):
    #The basic bootable form
    formDiv = DIV(DIV(H3('Bootable Info:')),
                  DIV(LABEL('Title:', _for='title')),
                  DIV(INPUT(_name='title', requires=db.Bootables.Title.requires,
                            _value=getFieldValue(values, 'title'))),
                  DIV(LABEL('Short Description:', _for='shortDesc')),
                  DIV(INPUT(_name='shortDesc', requires=db.Bootables.ShortDescription.requires,
                            _value=getFieldValue(values, 'shortDesc'),
                            _placeholder='Max length 120 characters')),
                  DIV(LABEL('Funding Goal:', _for='fundGoal')),
                  DIV(INPUT(_name='fundGoal', _type='number', _min='1', requires=db.Bootables.FundingGoal.requires,
                            _value=getFieldValue(values, 'fundGoal'))),
                  DIV(LABEL('Category:', _for='cat')),
                  DIV(SELECT(bootableCategories, _name='cat', requires=db.Bootables.Category.requires,
                            _value=getFieldValue(values, 'cat'))),
                  DIV(LABEL('Long Description:', _for='longDesc')),
                  DIV(TEXTAREA(_name='longDesc', requires=db.Bootables.LongDescription.requires,
                               value=getFieldValue(values, 'longDesc'))),
                  DIV(LABEL('Personal Story:', _for='story')),
                  DIV(TEXTAREA(_name='story', requires=db.Bootables.PersonalStory.requires,
                               value=getFieldValue(values, 'story'))),
                  DIV(INPUT(_type='submit', _value=submitText))
                  )

    if includeImage:
        formDiv.append(DIV(LABEL('Image:', _for='image')))
        formDiv.append(DIV(INPUT(_name='image', _type='file', requires=db.Bootables.Image.requires,
                                 _value=getFieldValue(values, 'image'))))

    form = FORM(formDiv)

    return form

def getPledgeForm(values, numRewards, inheritPledges, inheritLabel='Get inheritable rewards from other pledges',
                  incNextPledge=True):
    """
    Get the form used for entering pledges into the database
    :param values: the post_vars from the last submission (used for repopulating){
    :param numRewards: the number of reward slots to have in the form
    :return: The pledge entry form
    """

    form = FORM(DIV(DIV(H3('Pledge:')),
                    DIV(LABEL('Name:', _for='name')),
                    DIV(INPUT(_name='name', requires=db.Pledges.Name.requires,
                              _value=getFieldValue(values, 'name'))),
                    DIV(LABEL('Value:', _for='value')),
                    DIV(INPUT(_name='value', _tppe='number', _min='0', requires=db.Pledges.Value.requires,
                              _value=getFieldValue(values, 'value')))
                    ),
                _name='pledgeForm')

    for i in range(1, int(numRewards)+1):
        form.append(getRewardDiv(values, str(i)))

    form.append(INPUT(_name='numRewards', _value=numRewards, _hidden=True, _type='hidden'))

    if inheritPledges:
        form.append(INPUT(_name='inheritRewards', _value='True', _hidden=True, _type='hidden'))
        form.append(getPledgeInheritDiv(values, values.value or 0))
        inheritLabel = 'Refresh inheritable rewards'

    form.append(INPUT(_name='inheritPledges', _type='submit', _value=inheritLabel, _id='inheritPledges'))

    buttonDiv = DIV(DIV(INPUT(_name='delReward', _type='submit', _value='Delete last reward')),
                    DIV(INPUT(_name='addReward', _type='submit', _value='Add another reward')))

    if incNextPledge:
        buttonDiv.append(DIV(INPUT(_name='nextPledge', _type='submit', _value='Add another pledge', _id='nextPledge')))

    buttonDiv.append(DIV(INPUT(_name='done', _type='submit', _value='Done', _id='doneSubmit')))
    form.append(buttonDiv)
    return form


def getRewardDiv(values, num):
    form = DIV(DIV(H4('Reward ' + num + ':')),
               DIV(LABEL('Description:', _for='description-'+num)),
               DIV(TEXTAREA(_name='description-'+num, requires=db.Rewards.description.requires,
                            value=getFieldValue(values, 'description-'+num)))
               )
    return form


def getPledgeInheritDiv(values, pledgeValue):
    #Add checkboxes for reward inheritance
    otherRewards = db((db.Pledges.bootID == int(request.args(0))) &
                      (db.Pledges.Value <= pledgeValue) &
                      (db.Pledges.id == db.PledgeRewards.pledgeID) &
                      (db.PledgeRewards.rewardID == db.Rewards.id)
    ).select('Rewards.id', 'Rewards.description', distinct=True)

    count = 0
    rewardInheritanceDiv = DIV(DIV(H4('Inherit Rewards:')))
    for reward in otherRewards:
        count+=1
        rewardInheritanceDiv.append(DIV(INPUT(_name='reward-' + str(reward.id),
                                              _type='checkbox', value=getFieldValue(values, 'reward-'+str(reward.id)),
                                              _class='checkbox-inline'),
                                        LABEL(reward.description, _for='reward-' + str(reward.id)),
                                        INPUT(_name='rewardID-'+str(count), _value=reward.id, _hidden=True, _type='hidden'),
                                        _class='checkbox'))
    rewardInheritanceDiv.append(INPUT(_name='inheritCount', _value=count, _hidden=True, _type='hidden'))
    return rewardInheritanceDiv


def dash():
    userID = session.user
    if userID is None:
        redirect(URL('default', 'user', args=['login']))

    bootables = db(db.Bootables.userID == userID).select()
    pledges = db((db.Bootables.userID == userID) &
                 (db.Pledges.bootID == db.Bootables.id) &
                 (db.Pledges.id == db.PledgeRewards.pledgeID) &
                 (db.Rewards.id == db.PledgeRewards.rewardID)).select('Bootables.id',
                                                                      'Pledges.Name',
                                                                      'Pledges.Value',
                                                                      'Rewards.description')
    totalPledged = dict()
    percentComplete = dict()
    forms = dict()
    for bootable in bootables:
        totalPledged[bootable.id] = getTotalPledged(bootable.id)
        percentComplete[bootable.id] = getCompletionPercentage(bootable.id)
        bootStateForm = FORM(SELECT(bootableStates, _name='state-'+str(bootable.id), _value=bootable.State),
                             INPUT(_name='bootID', _value=bootable.id, _hidden=True, _type='hidden'),
                             INPUT(_name='submit-'+str(bootable.id), _type='submit'))
        forms[bootable.id] = bootStateForm
    return dict(bootables=bootables, pledges=pledges, total=totalPledged, percent=percentComplete, stateForms=forms)


def view():
    """
    View a particular bootable,
    which bootable is determined by request.args(0) which is the bootID
    :return: booable information, the percentage complete and the users who pledged with their pledge amount
    """
    bootID = request.args(0)
    bootable = db(db.Bootables.id == bootID).select()

    total = getTotalPledged(bootID)
    completion = getCompletionPercentage(bootID)

    pledgeValues = db(db.Pledges.bootID == bootID).select('Value')
    values = []
    for item in pledgeValues:
        values += [item.Value]

    print(values)
    pledgeForm = FORM(SELECT(values, _name='pledgeValue'),
                      INPUT(_type='submit', _name='pledgeSubmit', _value='Pledge!'),
                      _name='pledgeForm',
                      _class='form-inline')

    if session.user is not None:
        #Only do anything with the form if user logged in
        if pledgeForm.accepts(request.post_vars, session):
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

    return dict(bootable=bootable, total=total, percent=completion, users=usersPledged, pledgeForm=pledgeForm)


def edit():
    bootID = request.args(0)
    bootable = db(db.Bootables.id == bootID).select().first()
    #Only the owner of a bootable can edit it.
    if (session.user is None) or (session.user != bootable.userID):
        redirect(URL('default', 'index'))
    elif bootable.State == bootableStates[1]:
        #Cannot edit if open
        redirect(URL('bootables', 'dash'))
    vars = dict()
    vars['title'] = bootable.Title;
    vars['shortDesc'] = bootable.ShortDescription
    vars['fundGoal'] = bootable.FundingGoal
    vars['cat'] = bootable.Category
    vars['longDesc'] = bootable.LongDescription
    vars['story'] = bootable.PersonalStory

    pledges = db((db.Bootables.userID == session.user) &
                 (db.Pledges.bootID == bootID) &
                 (db.Pledges.id == db.PledgeRewards.pledgeID) &
                 (db.Rewards.id == db.PledgeRewards.rewardID)).select('Bootables.id',
                                                                      'Pledges.Name',
                                                                      'Pledges.Value',
                                                                      'Rewards.description')

    form = getBootableForm(vars, False, 'Save Changes')
    if form.accepts(request.post_vars, session):
        session.flash = 'Updated bootable successfully'
        bootable.Title = request.post_vars.title
        bootable.ShortDescription = request.post_vars.shortDesc
        bootable.FundingGoal = request.post_vars.fundGoal
        bootable.Category = request.post_vars.cat
        bootable.LongDescription = request.post_vars.longDesc
        bootable.PersonalStory = request.post_vars.story
        bootable.update_record()
        redirect(URL('bootables', 'dash'))
    elif form.errors:
        response.flash = 'There was a problem with something you entered.'
    else:
        response.flash = 'Edit your bootable'
    return dict(form=form, pledges=pledges)


def editPledge():
    session.resubmit = ''
    pledgeID = request.args(0)
    pledge = db((db.Pledges.id == pledgeID) &
                (db.Pledges.id == db.PledgeRewards.pledgeID) &
                (db.Rewards.id == db.PledgeRewards.rewardID)).select()

    #Dont allow users to edit pledges that dont belong to them
    bootable = db(db.Bootables.id == pledge.first().Pledges.bootID).select('userID').first()
    if bootable.userID != session.user:
        redirect(URL('default', 'index'))

    values = dict()
    values['name'] = pledge.first().Pledges.Name
    values['value'] = pledge.first().Pledges.Value

    #After the initial loading of the form user may have edited fields,
    # so use the values from post_vars overriding those from db
    for item in request.post_vars:
        values[item] = request.post_vars[item]

    count=1
    rewardIDs = dict()
    for reward in pledge:
        if not reward.PledgeRewards.Inherited:
            values['description-' + str(count)] = reward.Rewards.description
            rewardIDs[count] = reward.Rewards.id
            count += 1
    count -= 1

    numRewards = count
    if request.post_vars.numRewards is not None:
        numRewards = int(request.post_vars.numRewards)

    inheritLabel = 'Save and continue to inherit pledges'
    form = getPledgeForm(values, numRewards, False, inheritLabel, False)

    if (request.post_vars.addReward is not None) & (request.post_vars.addReward != ''):
        #Add a reward to the form
        numRewards += 1
        form = getPledgeForm(request.post_vars, numRewards, False, inheritLabel, False)
    elif (request.post_vars.delReward is not None) & (request.post_vars.delReward != ''):
        #if user added too many rewards can remove the lase one
        numRewards -= 1
        form = getPledgeForm(request.post_vars, numRewards, False, inheritLabel, False)
    elif form.accepts(request.post_vars, session, formname='pledgeForm'):
        db(db.Pledges.id == pledgeID).update(Name=request.post_vars.name)
        valueChanged = False
        if pledge.first().Pledges.Value != request.post_vars.value:
            valueChanged = True
            db(db.Pledges.id == pledgeID).update(Value=request.post_vars.value)

        print 'count' + str(count)
        rewardDiff = 0
        if numRewards < count:
            rewardDiff = count - numRewards
            count = numRewards

            #Delete rewards which are no longer wanted
            for i in range(numRewards + 1, numRewards + rewardDiff + 1):
                db(db.Rewards.id == rewardIDs[i]).delete()

        #update the existing records
        for i in range(1, count+1):
            db(db.Rewards.id == rewardIDs[i]).update(description=request.post_vars['description-' + str(i)])

        for i in range(count + 1, numRewards + 1):
            rewardID = db.Rewards.insert(description=request.post_vars['description-' + str(i)])
            db.PledgeRewards.insert(pledgeID=pledgeID,
                                    rewardID=rewardID,
                                    Inherited=False)

        if (request.post_vars.inheritPledges is not None) & (request.post_vars.inheritPledges != ''):
            redirect(URL('selectInheritedRewards', args=[pledgeID]))
        else:
            redirect(URL('dash'))

    elif form.errors:
        response.flash = 'There was a problem with the form'
    else:
        if request.post_vars.name is not None:
            if (request.post_vars.inheritPledges is not None) & (request.post_vars.inheritPledges != ''):
                session.resubmit = 'inheritPledges'
            else:
                session.resubmit = 'doneSubmit'
            #Need to use the submit hack again
            response.flash = 'Please submit the form again'
        else:
            response.flash = 'Edit the pledge, ' \
                             'changing the value will require changing the reward inheritance on the next page'


    return dict(form=form)