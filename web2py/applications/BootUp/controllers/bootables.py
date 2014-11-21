__author__='Y8191122'
# This controller is for bootable manipulation

def create():
    """
    Create bootables (the basic bootable information)
    :return: bootable creation form
    """
    #User must be logged in
    response.subtitle = 'Create new Bootable.'
    if session.user is None:
        redirect(response.loginURL)
    else:
        form = getBootableForm(request.post_vars)

        if form.accepts(request.post_vars, session, formname='bootableForm'):
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
            session.flash = 'Bootable successfully created'
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
    bootable = db(db.Bootables.id == request.args(0)).select().first()
    if bootable is None:
        #Can only edit existing bootables
        redirect(URL('default', 'index'))
    elif bootable.userID != session.user:
        #Can only edit if loged in as owning user
        redirect(loginURL)
    elif bootable.State == bootableStates[0]:
        #Cant create pledge for bootable that is not not available
        redirect(URL('dash'))

    response.subtitle = 'Create pledge for Bootable: ' + bootable.Title
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
        pledgeId = db.Pledges.insert(Name=request.post_vars.name,
                                     Value=request.post_vars.value,
                                     bootID=request.args(0)
                                     )

        for i in range(1, numRewards + 1):
            rewardId = db.Rewards.insert(Description=request.post_vars['description-' + str(i)])
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
            redirect(URL('dash'))
    elif form.errors:
        response.flash = 'There was a problem with what you entered.'
    else:
        response.flash = 'Please enter Pledge details'
    return dict(form=form)


def getBootableForm(values, includeImage=True, submitText='Add pledge values'):
    """
    Get the bootable creation/edit form
    :param values: pre population values
    :param includeImage: include image upload input (for editing bootable)
    :param submitText: The text of the submit button
    :return: A form for creating/editing bootables
    """
    #The basic bootable form
    formDiv = DIV(DIV(LEGEND('Bootable Info:')),
                  DIV(LABEL('Title:', _for='title')),
                  DIV(INPUT(_name='title', requires=db.Bootables.Title.requires,
                            _value=getFieldValue(values, 'title'))),
                  DIV(LABEL('Short Description:', _for='shortDesc')),
                  DIV(INPUT(_name='shortDesc', requires=db.Bootables.ShortDescription.requires,
                            _value=getFieldValue(values, 'shortDesc'),
                            _placeholder='Max length 120 characters', _maxlength=120)),
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
                               value=getFieldValue(values, 'story')))
                  )

    if includeImage:
        formDiv.append(getImageUploadDiv(values))

    formDiv.append(DIV(INPUT(_type='submit', _value=submitText)))

    form = FORM(formDiv, formname='bootableForm')

    return form

def getPledgeForm(values, numRewards, inheritPledges, inheritLabel='Get inheritable rewards from other pledges',
                  incNextPledge=True):
    """
    Get the form used for entering pledges into the database
    :param values: the values of the fields for repopulation
    :param numRewards: the number of reward input for the form to ahve
    :param inheritPledges: whether to include inheritance checkboxes
    :param inheritLabel: the label for the inheritance button
    :param incNextPledge: whether to unclude next pledge button (for editing)
    :return: the pledge creation / edit form
    """
    form = FORM(DIV(DIV(LEGEND('Pledge:')),
                    DIV(LABEL('Name:', _for='name')),
                    DIV(INPUT(_name='name', requires=db.Pledges.Name.requires,
                              _value=getFieldValue(values, 'name'))),
                    DIV(LABEL('Value:', _for='value')),
                    DIV(INPUT(_name='value', _tppe='number', _min='0', requires=db.Pledges.Value.requires,
                              _value=getFieldValue(values, 'value')))
                    ),
                _name='pledgeForm')

    form.append(DIV(LEGEND('Rewards')))
    for i in range(1, int(numRewards)+1):
        form.append(getRewardDiv(values, str(i)))

    form.append(INPUT(_name='numRewards', _value=numRewards, _hidden=True, _type='hidden'))

    if inheritPledges:
        form.append(INPUT(_name='inheritRewards', _value='True', _hidden=True, _type='hidden'))
        form.append(getPledgeInheritDiv(values, values.value or 0, int(request.args(0))))
        inheritLabel = 'Refresh inheritable rewards'

    form.append(INPUT(_name='inheritPledges', _type='submit', _value=inheritLabel, _id='inheritPledges'))

    buttonDiv = DIV(DIV(INPUT(_name='delReward', _type='submit', _value='Delete last reward')),
                    DIV(INPUT(_name='addReward', _type='submit', _value='Add another reward')))

    if incNextPledge:
        buttonDiv.append(DIV(INPUT(_name='nextPledge', _type='submit', _value='Add another pledge', _id='nextPledge')))

    buttonDiv.append(DIV(INPUT(_name='done', _type='submit', _value='Done', _id='doneSubmit')))
    form.append(buttonDiv)

    #Must set formkey in all paths
    form.accepts(dict(), session, 'pledgeForm')
    return form


def getRewardDiv(values, num):
    """
    Get a div containing reward input fields for a form
    :param values: pre population values
    :param num: the number of reward inputs
    :return: div containing reward input fields
    """
    form = DIV(DIV(H4('Reward ' + num + ':')),
               DIV(LABEL('Description:', _for='description-'+num)),
               DIV(TEXTAREA(_name='description-'+num, requires=db.Rewards.Description.requires,
                            value=getFieldValue(values, 'description-'+num)))
               )
    return form


def getPledgeInheritDiv(values, pledgeValue, bootID):
    """
    A Div containing pledge inheritance inputs
    :param values: pre population values
    :param pledgeValue: the value of the pledge (only inherit from lower valued pledges)
    :param bootID: the id of the bootable these pledges are for
    :return: div containing inheritance inputs
    """
    #Add checkboxes for reward inheritance
    otherRewards = db((db.Pledges.bootID == bootID) &
                      (db.Pledges.Value < pledgeValue) &
                      (db.Pledges.id == db.PledgeRewards.pledgeID) &
                      (db.PledgeRewards.rewardID == db.Rewards.id)
    ).select('Rewards.id', 'Rewards.Description', distinct=True)

    count = 0
    rewardInheritanceDiv = DIV(DIV(LEGEND('Inherit Rewards:')))
    for reward in otherRewards:
        count+=1
        rewardInheritanceDiv.append(DIV(INPUT(_name='reward-' + str(reward.id),
                                              _type='checkbox', value=getFieldValue(values, 'reward-'+str(reward.id)),
                                              _class='checkbox-inline'),
                                        LABEL(reward.Description, _for='reward-' + str(reward.id)),
                                        INPUT(_name='rewardID-'+str(count), _value=reward.id, _hidden=True, _type='hidden'),
                                        _class='checkbox'))
    rewardInheritanceDiv.append(INPUT(_name='inheritCount', _value=count, _hidden=True, _type='hidden'))
    return rewardInheritanceDiv


def dash():
    """
    The bootable dashboard for a user
    :return: a set of bootables owned by the user,
            a set of pledges and their rewards for each bootable owned by the user,
            a dict of percentages complete for each bootable indexed by bootID,
            a dict of total pledge values for each bootable index by bootID,
            a dict of forms, one for each bootable, for selecting the bootables state,
            a dict of images one for each bootable

    """
    response.subtitle = 'Bootable Dashboard'
    userID = session.user
    if userID is None:
        redirect(response.loginURL)

    bootables = db(db.Bootables.userID == userID).select()
    pledges = db((db.Bootables.userID == userID) &
                 (db.Pledges.bootID == db.Bootables.id) &
                 (db.Pledges.id == db.PledgeRewards.pledgeID) &
                 (db.Rewards.id == db.PledgeRewards.rewardID)).select('Bootables.id',
                                                                      'Pledges.id',
                                                                      'Pledges.Name',
                                                                      'Pledges.Value',
                                                                      'Rewards.Description',
                                                                      orderby=db.Pledges.Value)
    totalPledged = dict()
    percentComplete = dict()
    forms = dict()
    images = dict()
    count = 0
    #Build the list of totals, percentages, state forms and images for each bootable owned by user
    for bootable in bootables:
        totalPledged[bootable.id] = getTotalPledged(bootable.id)
        percentComplete[bootable.id] = getCompletionPercentage(bootable.id)
        formname = 'stateForm-' + str(bootable.id)
        bootStateForm = FORM(SELECT(bootableStates, _name='state-'+str(bootable.id), value=bootable.State),
                             INPUT(_name='bootID-' + str(count), _value=bootable.id, _hidden=True, _type='hidden'),
                             INPUT(_name='submit-'+str(bootable.id), _type='submit'),
                             formname=formname,
                             _class='form-inline')
        count += 1
        forms[bootable.id] = bootStateForm
        images[bootable.id] = IMG(_src=URL('default', 'bootableImage', args=[bootable.Image]),
                                  _alt='bootable image')

        if bootStateForm.accepts(request.post_vars, session, formname):
            newState = request.post_vars['state-' + str(bootable.id)]
            bootable.State = newState
            bootable.update_record()
            session.flash = 'Updated ' + bootable.Title + ' to ' + newState
            redirect(URL())

    return dict(bootables=bootables,
                pledges=pledges,
                totals=totalPledged,
                percents=percentComplete,
                stateForms=forms,
                images=images)


def edit():
    """
    A page for editing bootables
    :return: a form for editing bootable, a list of pledges for the bootable
    """
    response.subtitle = 'Edit Bootable'
    bootID = request.args(0)
    bootable = db(db.Bootables.id == bootID).select().first()

    #Only the owner of a bootable can edit it.
    if (session.user is None) or (session.user != bootable.userID):
        redirect(URL('default', 'index'))
    elif bootable.State == bootableStates[1]:
        #Cannot edit if open
        session.flash = 'Bootable Open so cannot edit'
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
                                                                      'Rewards.Description')

    form = getBootableForm(vars, False, 'Save Changes')
    if form.accepts(request.post_vars, session, formname='bootableForm'):
        session.flash = 'Updated Bootable successfully'
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
        response.flash = 'Edit your Bootable'
    return dict(form=form, pledges=pledges)


def editPledge():
    """
    A page for editing pledges
    :return: a form
    """
    response.subtitle = 'Edit Pledge'
    session.resubmit = ''
    pledgeID = request.args(0)
    pledge = getPledge(pledgeID)

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
            values['description-' + str(count)] = reward.Rewards.Description
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
            db(db.Rewards.id == rewardIDs[i]).update(Description=request.post_vars['description-' + str(i)])

        for i in range(count + 1, numRewards + 1):
            rewardID = db.Rewards.insert(Description=request.post_vars['description-' + str(i)])
            db.PledgeRewards.insert(pledgeID=pledgeID,
                                    rewardID=rewardID,
                                    Inherited=False)

        session.flash = 'Pledge successfully saved'
        if (request.post_vars.inheritPledges is not None) & (request.post_vars.inheritPledges != ''):
            redirect(URL('selectInheritedRewards', args=[pledgeID]))
        else:
            redirect(URL('dash'))

    elif form.errors:
        response.flash = 'There was a problem with the form'
    else:
        response.flash = 'Edit the pledge, ' \
                         'changing the value will require changing the reward inheritance on the next page'


    return dict(form=form)

def selectInheritedRewards():
    """
    Select the reward inheritance of a pledge page
    :return: form for selecting pledges, the pledge that you are editing
    """
    response.subtitle = 'Select Inherited Rewards'
    pledgeID = request.args(0)
    pledge = getPledge(pledgeID)

    values = dict()
    rewardIDs = dict()
    for reward in pledge:
        if reward.PledgeRewards.Inherited:
            values['reward-' + str(reward.Rewards.id)] = 'on'

    form = FORM(formname='inheritForm')

    form.append(getPledgeInheritDiv(values, pledge.first().Pledges.Value, pledge.first().Pledges.bootID))
    form.append(DIV(INPUT(_name='submit', _type='submit')))

    if form.accepts(request.post_vars, session, formname='inheritForm'):
        inheritCount = int(request.post_vars.inheritCount)

        for i in range(1, inheritCount + 1):
            rewardId = request.post_vars['rewardID-' + str(i)]

            if (values.get('reward-' + str(rewardId), 'off') == 'on') & \
                    (request.post_vars['reward-' + str(rewardId)] != 'on'):
                #If gone from checked to not checked, delete relationship from db
                db((db.PledgeRewards.rewardID == rewardId) &
                   (db.PledgeRewards.pledgeID == pledgeID)).delete()

            elif request.post_vars['reward-'+str(rewardId)] == 'on':
                #if gone from off to on insert into db
                db.PledgeRewards.insert(pledgeID=pledgeID,
                                        rewardID=rewardId,
                                        Inherited=True)
            #Otherwise there was no change so do nothing
        session.flash = 'Successfully updated pledge inheritance!'
        redirect(URL('dash'))
    elif form.errors:
        response.flash = 'Something went wrong! Please try again'
    else:
        response.flash = 'Select rewards you wish this pledge to inherit from other pledges'

    return dict(form=form, pledge=pledge)


def getPledge(pledgeID):
    """
    Get a pledge
    :param pledgeID: the id of the pledge to get
    :return: the pledge with all its rewards
    """
    pledge = db((db.Pledges.id == pledgeID) &
                (db.Pledges.id == db.PledgeRewards.pledgeID) &
                (db.Rewards.id == db.PledgeRewards.rewardID)).select()

    #Dont allow users to edit pledges that dont belong to them
    bootable = db(db.Bootables.id == pledge.first().Pledges.bootID).select('userID').first()
    if bootable.userID != session.user:
        redirect(URL('default', 'index'))
    return pledge

def upload():
    """
    Page for uploading a new bootable image
    :return: the form for uploading an image, the current image
    """
    response.subtitle = 'Upload new Bootable image'
    bootID = request.args(0)
    bootable = db(db.Bootables.id == bootID).select().first()
    if bootable.userID != session.user:
        redirect(loginURL)

    #Current image
    image = DIV(LEGEND('Current Image'),
                IMG(_src=URL('default', 'bootableImage', args=[bootable.Image]), _alt='Current Image'))

    form = FORM(LEGEND('New Image'),
                getImageUploadDiv(),
                INPUT(_name='submit', _type='submit'),
                formname='imageForm')

    if form.accepts(request.post_vars, session, 'imageForm'):
        image = db.Bootables.Image.store(request.post_vars.image.file, request.post_vars.image.filename)
        bootable.Image = image
        bootable.update_record()
        session.flash = 'Image updated'
        redirect(URL('dash'))
    elif form.errors:
        response.flash = 'There was something wrong with your selection'
    else:
        response.flash = 'Upload your new image below'

    return dict(form=form, currentImage=image)


def getImageUploadDiv(values=dict()):
    """
    Get a Div with input for uploading image
    :return: the div
    """
    div = DIV(DIV(LABEL('Image:', _for='image')),
              DIV(INPUT(_name='image', _type='file', requires=db.Bootables.Image.requires),
                  _value=getFieldValue(values, 'image')))
    return div
