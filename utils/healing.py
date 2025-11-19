def select(goal):
    mapping = {
        'wealth': {
            'stones':[{'en':'Citrine','fa':'سیترین'}],
            'herbs':[{'en':'Bay Leaf','fa':'برگ بو'}]
        },
        'love': {
            'stones':[{'en':'Rose Quartz','fa':'کوارتز رز'}],
            'herbs':[{'en':'Rose','fa':'گل رز'}]
        },
        'health': {
            'stones':[{'en':'Amethyst','fa':'آمتیست'}],
            'herbs':[{'en':'Lavender','fa':'اسطوخودوس'}]
        },
        'career': {
            'stones':[{'en':'Hematite','fa':'هماتیت'}],
            'herbs':[{'en':'Cedar','fa':'سدر'}]
        }
    }
    return mapping.get(goal, mapping['wealth'])
