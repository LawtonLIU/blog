#todo: ping_google被弃用，需要替换

import requests
from django.conf import settings
# from django.contrib.sitemaps import ping_google



class SpiderNotify():
    @staticmethod
    def baidu_notify(urls):
        try:
            data = '\n'.join(urls)
            result = requests.post(settings.BAIDU_NOTIFY_URL, data=data)
        except Exception as e:
            print(e)

    # @staticmethod
    # def __google_notify():
    #     try:
    #         ping_google('/sitemap.xml')
    #     except Exception as e:

    @staticmethod
    def notify(url):

        SpiderNotify.baidu_notify(url)
        # SpiderNotify.__google_notify()
