__author__='Y8191122'


def index():
    return dict()


def create():
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
            redirect(URL('bootables', 'createPledges', args=[bootableID, 1]))
        elif form.errors:
            response.flash = 'There was a problem with your entry'
        else:
            response.flash = 'Please enter your Bootable details'
    return dict(form=form)


def createPledges():
    numRewards = request.post_vars.numRewards
    if numRewards is None:
        numRewards = 1
    else:
        numRewards = int(numRewards)
        if numRewards < 1:
            numRewards = 0

    inheritRewards = request.post_vars.inheritRewards
    if inheritRewards is None:
        inheritRewards = False
    form = getPledgeForm(request.post_vars, numRewards, inheritRewards)

    if (request.post_vars.addReward is not None) & (request.post_vars.addReward != ''):
            numRewards += 1
            form = getPledgeForm(request.post_vars, numRewards, inheritRewards)
    elif (request.post_vars.delReward is not None) & (request.post_vars.delReward != ''):
            numRewards -= 1
            form = getPledgeForm(request.post_vars, numRewards, inheritRewards)
    elif (request.post_vars.inheritPledges is not None) & (request.post_vars.inheritPledges != ''):
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
                                    rewardID=rewardId)

        inheritCount = request.post_vars.inheritCount
        if inheritCount is not None:
            inheritCount = int(inheritCount)
            for i in range(1, inheritCount + 1):
                rewardId = request.post_vars['rewardID-' + str(i)]
                if (request.post_vars['reward-' + str(rewardId)] is not None) and \
                        (request.post_vars['reward-'+str(rewardId)] == 'on'):
                    db.PledgeRewards.insert(pledgeID=pledgeId,
                                            rewardID=rewardId)


        response.flash = 'Pledge ' + request.post_vars.name + ' saved'

        if (request.post_vars.nextPledge is not None) & (request.post_vars.nextPledge != ''):
            redirect(URL(args=request.args))
        else:
            redirect(URL('default', 'index'))
            #TODO redirect to bootable edit page
    elif form.errors:
        response.flash = 'There was a problem with what you entered.'
    else:
        if request.post_vars.name is not None:
            #TODO fix this
            #For some reason when the inheritance check boxes are in the form, the form wont be accepted the first time
            #But will also not populate the errors variable so there is no way to know what is wrong.
            #So as a temporary measure added this message so the user has some feedback/forward on what to do.
            response.flash = 'Please submit the form again.'
        else:
            response.flash = 'Please enter Pledge details'
    return dict(form=form)


def createRewards():
    form=FORM()
    return dict(form=form)


def getBootableForm(values):
    #The basic bootable form
    form = FORM(DIV(DIV(H3('Bootable Info:')),
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
                    DIV(LABEL('Image:', _for='image')),
                    DIV(INPUT(_name='image', _type='file', requires=db.Bootables.Image.requires,
                              _value=getFieldValue(values, 'image'))),
                    DIV(LABEL('Long Description:', _for='longDesc')),
                    DIV(TEXTAREA(_name='longDesc', requires=db.Bootables.LongDescription.requires,
                                 _value=getFieldValue(values, 'longDesc'))),
                    DIV(LABEL('Personal Story:', _for='story')),
                    DIV(TEXTAREA(_name='story', requires=db.Bootables.PersonalStory.requires,
                                 _value=getFieldValue(values, 'story'))),
                    DIV(INPUT(_type='submit', _value='Add pledge values'))

                    ))


    return form

def getPledgeForm(values, numRewards, inheritPledges):
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

    form.append(INPUT(_name='numRewards', _value=numRewards,_hidden=True))

    if inheritPledges:
        form.append(INPUT(_name='inheritRewards', _value='True', _hidden=True))
        form.append(getPledgeInheritDiv(values, values.value or 0))

    form.append(INPUT(_name='inheritPledges', _type='submit', _value='Refresh rewards from other pledges'))

    form.append(DIV(DIV(INPUT(_name='delReward', _type='submit', _value='Delete last reward')),
                    DIV(INPUT(_name='addReward', _type='submit', _value='Add another reward')),
                    DIV(INPUT(_name='nextPledge', _type='submit', _value='Add another pledge')),
                    DIV(INPUT(_name='done', _type='submit', _value='Done'))
                    ))
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
    otherRewards = db((db.Pledges.bootID == request.args(0) & (db.Pledges.Value <= pledgeValue)) &
                      ((db.Pledges.id == db.PledgeRewards.pledgeID) &
                      (db.PledgeRewards.rewardID == db.Rewards.id))).select('Rewards.id', 'Rewards.description',
                                                                            distinct=True)

    count = 0
    rewardInheritanceDiv = DIV(DIV(H4('Inherit Rewards:')))
    for reward in otherRewards:
        count+=1
        rewardInheritanceDiv.append(DIV(INPUT(_name='reward-' + str(reward.id),
                                              _type='checkbox', value=getFieldValue(values, 'reward-'+str(reward.id))),
                                        LABEL(reward.description, _for='reward-' + str(reward.id)),
                                        INPUT(_name='rewardID-'+str(count), _value=reward.id, _hidden=True)))
    rewardInheritanceDiv.append(INPUT(_name='inheritCount', _value=count, _hidden=True))
    return rewardInheritanceDiv



def dash():
    return dict()