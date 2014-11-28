__author__ = 'Y8191122'
from gluon import XML

def paragraphise(text):
    """
    Takes text and replaces newlines in it with <br> so that paragraphs get displayed correctly
    :param text: input text
    :return: xml of input text
    """
    text = text.replace('\n', '<br>')
    return XML(text)