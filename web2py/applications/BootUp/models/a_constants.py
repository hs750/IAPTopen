__author__ = 'Y8191122'
# a_ because models are loaded in alphabetical order

#These variables are intended as global constants
bootableCategories = ['Art', 'Comics', 'Crafts', 'Fashion', 'Film', 'Games', 'Music', 'Photography', 'Technology']
bootableStates = ['Not Available', 'Open for Pledges', 'Funded', 'Not Funded']


#This is intended to be a method available anywhere
def paragraphise(text):
    """
    Takes text and replaces newlines in it with <br> so that paragraphs get displayed correctly
    :param text: input text
    :return: xml of input text
    """
    text = text.replace('\n', '<br>')
    return XML(text)