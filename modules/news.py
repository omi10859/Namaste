from newsapi import NewsApiClient



def newsbyname(country,search=None, category=None):

    newsapi = NewsApiClient(api_key='1e8aa2017af046b08f8db306b7c7ad70')


    top_headlines = newsapi.get_top_headlines(q=search,
                                            category=category,
                                            language='en',
                                            country=country)

    return top_headlines


