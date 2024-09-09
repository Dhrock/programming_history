#-*- coding:utf-8 -*-
from requests_oauthlib import OAuth1Session
import json
import datetime, time, sys
from abc import ABCMeta, abstractmethod

CK = 'O7uICA58cM5sKZO8jgKfISbZg'   # API key
CS = 'Th3o0Fq9BtA7Yuh5YXFF0jQcvZYbDdy5jmjQcJlBLi5YH7iLL8'   # API secret
AT = '1359366834764484610-aKfNal7XCFMVfkTm2aQsZbAj1YKrpL'
AS = 'XKRqgsnfDRGzvj3bo5pzYMB01EeiFmVFjiyw4PuJy6qMJ'

class TweetsGetter(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.session = OAuth1Session(CK,CS,AT,AS)
    
    @abstractmethod
    def specifyUrlAndParams(self,keyword):
        '''
        呼び出し先 URL, パラメータを返す
        '''
    @abstractmethod
    def pickupTweet(self,res_text):
        '''
        res_text からツイートを取り出し、配列にセットして返却
        '''
    @abstractmethod
    def getLimitContext(self,res_text):
        '''
        回数制限の情報を取得　(起動時)
        '''
    def collect(self,total = -1,onlyText = False,includeRetweet = False):
        '''
        ツイート取得を開始
        '''
        self.checkLimit()

        url,params = self.specifyUrlAndParams()
        params['include_rts'] = str(includeRetweet).lower()


        cnt = 0
        unavailableCnt = 0
        while True:
            res = self.session.get(url,params = params)
            if res.status_code == 503:
                #503 : Service Unavailable
                if unavailableCnt > 10:
                    raise Exception('Twitter API error %d' % res.status_code)

                unavailableCnt += 1
                print('Service Unavailable 503')
                self.waitUntilReset(time.mktime(datetime.datetime.now().timetuple()) + 30)
                continue

            unavailableCnt = 0

            if res.status_code != 200:
                raise Exception('Twitter API error %d' % res.status_code)

            tweets = self.pickupTweet(json.loads(res.text))
            if len(tweets) == 0:
                break

            for tweet in tweets:
                if(('retweeted_status' in tweet) and (includeRetweet is False)):
                    pass
                else:
                    if onlyText is True:
                        yield tweet['text']
                    else:
                        yield tweet
                    
                    cnt += 1
                    if cnt % 100 == 0:
                        print('%d件' % cnt)

                    if total > 0 and cnt >= total:
                        return

            params['max_id'] = tweet['id'] -1
            
            #ヘッダ確認　（回数制限）
            
            if('X-Rate-Limit-Remaining' in res.headers and 'X-Rate-Limit-Reset' in res.headers):
                if(int(res.headers['X-Rate-Limit-Remaining']) == 0):
                    self.waitUntilReset(int(res.headers['X-Rate-Limit-Reset']))
                    self.checkLimit()
            else:
                print('not found  -  X-Rate-Limit-Remaining or X-Rate-Limit-Reset')
                self.checkLimit()
            
    def checkLimit(self):
        '''
        回数制限を問い合わせ、アクセス可能になるまでwaitする
        '''
        unavailableCnt = 0
        while True:
            url = "https://api.twitter.com/1.1/application/rate_limit_status.json"
            res = self.session.get(url)

            if res.status_code == 503:
                if unavailableCnt > 10:
                    raise Exception('Twitter API error %d' % res.status_code)

                unavailableCnt += 1
                print('Service Unavailable 503')
                self.waitUntilReset(time.mktime(datetime.datetime.now().timetuple()) + 30)
                continue

            unavailableCnt = 0

            if res.status_code != 200:
                raise Exception('Twitter API error %d' % res.status_code)

            remaining, reset = self.getLimitContext(json.loads(res.text))
            if(remaining == 0):
                self.waitUntilReset(reset)
            else:
                break
    def waitUntilReset(self,reset):
        '''
        reset時刻までsleep
        '''
        seconds = reset - time.mktime(datetime.datetime.now().timetuple())
        seconds = max(seconds, 0)
        print('\n     =====================')
        print ('     == waiting %d sec ==' % seconds)
        print ('     =====================')
        sys.stdout.flush()
        time.sleep(seconds + 10)

    @staticmethod
    def bySearch(keyword):
        return TweetsGetterBySearch(keyword)

class TweetsGetterBySearch(TweetsGetter):
    '''
    キーワードでツイート検索
    '''
    def __init__(self, keyword):
        super(TweetsGetterBySearch, self).__init__()
        self.keyword = keyword

    def specifyUrlAndParams(self):
        '''
        呼び出し先URL、パラメータを返す
        '''
        url = 'https://api.twitter.com/1.1/search/tweets.json'
        params = {'q':self.keyword, 'count':100}
        return url,params

    def pickupTweet(self,res_text):
        '''
        res_textからツイートを取り出し、配列にセットして返却
        '''
        results = []
        for tweet in res_text['statuses']:
            results.append(tweet)

        return results

    def getLimitContext(self,res_text):
        '''
        回数制限の情報を取得（起動時）
        '''
        remaining = res_text['resources']['search']['/search/tweets']['remaining']
        reset = res_text['resources']['search']['/search/tweets']['reset']

        return int(remaining), int(reset)
if __name__ == '__main__':
    getter = TweetsGetter.bySearch(u'コロナ　-filter:retweets -filter:replies -http:// -https:// -filter:links -#コロナ')

    cnt = 0
    for tweet in getter.collect(total = 100):
        cnt += 1
        print('--------%d' % cnt)
        print(tweet['text'])