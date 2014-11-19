__author__ = "Y8191122"


def index():
    newest = db(db.Bootables.id>0).select(orderby=~db.Bootables.id, limitby=(0, 5))
    top5 = getTop5()
    return dict(newest=newest, top=top5)



