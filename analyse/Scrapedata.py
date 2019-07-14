# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 22:36:57 2019

@author: Abhishek
"""



from lxml import html
from json import dump,loads
from requests import get
import json
from re import sub
from dateutil import parser as dateparser
from time import sleep

import urllib.request
from textblob import TextBlob
import string
import re




def Getdata(asin='B07QT569GM'):
    amazon_url  = 'https://www.amazon.in/dp/'+asin
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    response = get(amazon_url, headers = headers, verify=False, timeout=30)
    if response.status_code == 404:
        return {"url": amazon_url, "error": "page not found"}
    cleaned_response = response.text.replace('\x00', '')
    parser = html.fromstring(cleaned_response)
    techdet_dict = {}
    ratings_dict = {}
    descriptiontext=''
    descdata=''
    

    
    XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
    XPATH_PRODUCT_NAME = '//h1//span[@id="productTitle"]//text()'
    XPATH_PRODUCT_PRICE = '//span[@id="priceblock_ourprice"]/text()'
    XPATH_PRODUCT_PRICE_ALT = '//*[@id="soldByThirdParty"]/span/text()'
    XPATH_PRICE_EX='//div[@id="maxBuyBackDiscountSection"]//span//span//text()'
    XPATH_PRICE_NOEX='//span[@id="priceblock_dealprice"]//text()'
    XPATH_REVIEWCOUNT_TEXT='//span[@id="acrCustomerReviewText"]//text()'
    XPATH_COLOR_TEXT='//span[@id="variation_color_name"]//text()'
    XPATH_TECHDETAIL='//div[@class="attrG"]//div[@class="pdTab"]//table//tbody//tr'
    XPATH_IMGSRC='//div[@id="imgTagWrapperId"]/img/@src | //div[@id="img-canvas"]/img/@src'
    
    XPATH_DESCRIPTION='//div[@id="feature-bullets"]//ul'
    
    raw_product_price = parser.xpath(XPATH_PRODUCT_PRICE)
    raw_product_name = parser.xpath(XPATH_PRODUCT_NAME)
    raw_total_reviews  = parser.xpath(XPATH_REVIEWCOUNT_TEXT)
    total_ratings  = parser.xpath(XPATH_AGGREGATE_RATING)
    noex_price=parser.xpath(XPATH_PRICE_NOEX)
    ex_price=parser.xpath(XPATH_PRICE_EX)
    color=parser.xpath(XPATH_COLOR_TEXT)
    desctable =parser.xpath(XPATH_TECHDETAIL)
    descriplist = parser.xpath(XPATH_DESCRIPTION)
    raw_product_price_alt=parser.xpath(XPATH_PRODUCT_PRICE_ALT)
    
    
    for ratings in total_ratings:
        extracted_rating = ratings.xpath('./td//a//text()')
        if extracted_rating:
            rating_key = str(extracted_rating[0]).replace(' ','')
            raw_raing_value = extracted_rating[1]
            rating_value = str(raw_raing_value).replace('%','')
            
            if rating_key:
                ratings_dict.update({rating_key: rating_value})
                
                
    for row in desctable:
        rowdata=row.xpath('./td//text()')
        if rowdata:
            datakey = rowdata[0].strip()
            datavalue = rowdata[1].strip()
            if datakey and datavalue:
                techdet_dict.update({datakey : datavalue})
    
    if not techdet_dict:
        techdet_dict.update({'N/A' : 'N/A'})
                

    listdesc=[]            
    for descrow in descriplist:
        descdata=descrow.xpath('.//li//span//text()')
        for dataline in descdata:
            dataline=dataline.strip()
            listdesc.append(dataline)
            
    if not listdesc:
        listdesc.append('No description available.')
            
   
    
    product_price = ''.join(raw_product_price).replace(',', '')
    product_price_alt = ''.join(raw_product_price_alt).replace(',', '')
    if(not bool(product_price)):
        product_price=product_price_alt
  
    product_name = ''.join(raw_product_name).strip()          


        
    
    



                
    #exprice =''.join(filter(lambda x: x.isdigit(), product_exprice))
    total_reviews=raw_total_reviews
    
    
    
    
    #post processing
    
    reviewcount=re.sub("[\[\]\'$]","",str(total_reviews)).strip()
    #image
    URL = parser.xpath(XPATH_IMGSRC)
    imgurl=''
    for urll in URL:
       
        imgurl+=urll.strip()
    
    
    
    #storage
    data ={
            'Product_Name': product_name.strip(),
            'Price': product_price,     
            'Total_Reviews':reviewcount,
            'Description':listdesc,
            'Ratings':ratings_dict,
            'Technical_Details':techdet_dict,
            'Imgurl':imgurl,
            'Asin':asin
            
          }
    
    
    return data


#def GetReview():




def ParseReviews(asin):  
    review_url_p1= 'https://www.amazon.in/product-reviews/'+asin+'/ref=cm_cr_arp_d_paging_btm_next_'
    review_url_p2= '?pageNumber='
    pagenumber=10
    extracted_data = []
    

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}

    for j in range(pagenumber):
        amazonurl=review_url_p1+str(j)+review_url_p2+str(j)
        response = get(amazonurl, headers = headers, verify=False, timeout=30)
        if response.status_code == 404:
            return {"url": amazon_url, "error": "page not found"}
        if response.status_code != 200:
            continue
        
        # Removing the null bytes from the response.
        cleaned_response = response.text.replace('\x00', '')
        


        parser = html.fromstring(cleaned_response)
        
        XPATH_REVIEW_SECTION_2 = '//div[@id="cm_cr-review_list"]//div[@data-hook="review"]'
        XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
        reviews = parser.xpath(XPATH_REVIEW_SECTION_2)

        
       

        ratings_dict = {}
        reviews_list = []

#        #Grabing the rating  section in product page
#        for ratings in total_ratings:
#            extracted_rating = ratings.xpath('./td//a//text()')
#            if extracted_rating:
#                rating_key = extracted_rating[0] 
#                raw_raing_value = extracted_rating[1]
#                rating_value = raw_raing_value
#                if rating_key:
#                    ratings_dict.update({rating_key: rating_value})
        
        # Parsing individual reviews
        for review in reviews:
            XPATH_RATING  = './/i[@data-hook="review-star-rating"]//text()'
            XPATH_REVIEW_HEADER = './/a[@data-hook="review-title"]//text()'
            XPATH_REVIEW_POSTED_DATE = './/span[@data-hook="review-date"]//text()'
 
            XPATH_AUTHOR = './/span[contains(@class,"profile-name")]//text()'

            XPATH_REVIEW_TEXT_4 = './/span[@data-hook="review-body"]//text()'
            
            
            raw_review_author = review.xpath(XPATH_AUTHOR)
            raw_review_rating = review.xpath(XPATH_RATING)
            raw_review_header = review.xpath(XPATH_REVIEW_HEADER)
            raw_review_posted_date = review.xpath(XPATH_REVIEW_POSTED_DATE)

            raw_review_text = review.xpath(XPATH_REVIEW_TEXT_4)

            # Cleaning data
            author = ' '.join(' '.join(raw_review_author).split())
            review_rating = ''.join(raw_review_rating).replace('out of 5 stars', '')
            review_header = ' '.join(' '.join(raw_review_header).split())

            try:
                review_posted_date = dateparser.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')
            except:
                review_posted_date = None
            review_text = ' '.join(' '.join(raw_review_text).split())
            review_text = review_text.replace("'","")

 
            data = {
                    

                    'review_header': review_header,
                    'review_text': review_text,
                    'review_author': author,             
                    'review_rating': review_rating,           
                    'review_posted_date': review_posted_date
                    
                                       
                    }

            
            
            extracted_data.append(data)
    return extracted_data
    

def get_review_sentiment(review): 
    ''' 
    Utility function to classify sentiment of passed review 
    using textblob's sentiment method 
    '''
    # create TextBlob object of passed review text 
    analysis = TextBlob(' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", review).split())) 
    # set sentiment 
    if analysis.sentiment.polarity > 0: 
        return 'positive'
    elif analysis.sentiment.polarity == 0: 
        return 'neutral'
    else: 
        return 'negative'
  
    

def sentimentanalyser(data):
    ''' 
    Main function to fetch reviews and parse them. 
    '''
    
        
    # empty list to store parsed reviews 
    reviews = [] 
    returndata=[]
    sentiment=''
     
    # data assignment 
    fetched_reviews = data 

    # parsing reviews one by one 
    for review in fetched_reviews: 
        # empty dictionary to store required params of a review 
        parsed_review = {} 

        # saving text of review 
        parsed_review['text'] = review["review_text"]
        # saving sentiment of review 
        analysis = TextBlob(' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", review["review_text"]).split())) 
        # set sentiment 
        if analysis.sentiment.polarity > 0: 
            sentiment='positive'
        elif analysis.sentiment.polarity == 0: 
            sentiment='neutral'
        else: 
            sentiment='negative'






        parsed_review['sentiment'] = sentiment 

        # appending parsed review to reviews list 

        reviews.append(parsed_review) 

                    
    
    
    previews=[]
    nreviews=[]
    

    for review in reviews:
        if review['sentiment'] == 'positive':
            previews.append(review)
    # percentage of positive reviews 
#    print("Positive reviews percentage: {} %".format(100*len(previews)/len(reviews))) 
    # picking negative reviews from reviews 
    
    for review in reviews: 
        if review['sentiment'] == 'negative':
            nreviews.append(review)
#    # percentage of negative reviews 
#    print("Negative reviews percentage: {} %".format(100*len(nreviews)/len(reviews))) 
#    # percentage of neutral reviews 
#    print("Neutral reviews percentage: {} %".format(100*(len(reviews) - len(nreviews) - len(previews))/len(reviews))) 
    
#    # printing first 5 positive reviews 
#    print("\n\nPositive reviews:") 
#    for review in previews[:10]: 
#        print(review['text']) 
#  
#    # printing first 5 negative reviews 
#    print("\n\nNegative reviews:") 
#    for review in nreviews[:10]: 
#        print(review['text']) 
    try:
        pos=(100*len(previews)/len(reviews))
        neg=(100*len(nreviews)/len(reviews))
        neu=(100*(len(reviews) - len(nreviews) - len(previews))/len(reviews))
   

   
    
        databack={
                'posperc':pos,
                'nperc':neg,
                'neuperc':neu,

                }
    except:
        databack={
                'posperc':len(previews),
                'nperc':len(nreviews),
                'neuperc':len(reviews),

                }
        
#    
#    if not data:
#        databack={
#            'posperc':33,
#            'nperc':33,
#            'neuperc':34,
#            
#            }
        
    returndata.append(databack)
    return returndata
    
    
    
    
    
    
