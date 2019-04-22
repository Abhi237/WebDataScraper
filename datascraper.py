# Made For Course5 by Abhishek Thakur

from lxml import html
from json import dump,loads
from requests import get
import json
from re import sub
from dateutil import parser as dateparser
from time import sleep
from pymongo import MongoClient
#import string


def Parsedata(asin):
    amazon_url  = 'https://www.amazon.in/dp/'+asin
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    response = get(amazon_url, headers = headers, verify=False, timeout=30)
    if response.status_code == 404:
        return {"url": amazon_url, "error": "page not found"}
    cleaned_response = response.text.replace('\x00', '')
    parser = html.fromstring(cleaned_response)
    techdet_dict = {}
    ratings_dict = {}
    descriptiontext=''
    XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
    XPATH_PRODUCT_NAME = '//h1//span[@id="productTitle"]//text()'
    XPATH_PRODUCT_PRICE = '//span[@id="priceblock_dealprice"]/text()'
    XPATH_PRICE_EX='//div[@id="maxBuyBackDiscountSection"]//span//span//text()'
    XPATH_PRICE_NOEX='//span[@id="priceblock_ourprice"]//text()'
    XPATH_REVIEWCOUNT_TEXT='//span[@id="acrCustomerReviewText"]//text()'
    XPATH_COLOR_TEXT='//span[@id="variation_color_name"]//text()'
    #XPATH_TECHDETAIL='//span/text()="Technical Details"/parent::div/following-sibling:div//div//div//table'
    XPATH_IMGSRC='//div[@id="ivlargeimage"]/img/@src'
    XPATH_DESCRIPTION='//div[@id="feature-bullets"]//ul'
    
    raw_product_price = parser.xpath(XPATH_PRODUCT_PRICE)
    raw_product_name = parser.xpath(XPATH_PRODUCT_NAME)
    raw_total_reviews  = parser.xpath(XPATH_REVIEWCOUNT_TEXT)
    total_ratings  = parser.xpath(XPATH_AGGREGATE_RATING)
    noex_price=parser.xpath(XPATH_PRICE_NOEX)
    ex_price=parser.xpath(XPATH_PRICE_EX)
    color=parser.xpath(XPATH_COLOR_TEXT)
    #desctable =parser.xpath(XPATH_TECHDETAIL)
    descriplist = parser.xpath(XPATH_DESCRIPTION)
    
    for ratings in total_ratings:
        extracted_rating = ratings.xpath('./td//a//text()')
        if extracted_rating:
            rating_key = extracted_rating[0] 
            raw_raing_value = extracted_rating[1]
            rating_value = raw_raing_value
            if rating_key:
                ratings_dict.update({rating_key: rating_value})
##    for row in desctable:
##        rowdata=row.xpath('./td//text()')
##        if rowdata:
##            datakey = rowdata[0]
##            datavalue = rowvalue[1]
##            if datakey:
##                techdet_dict.update({datakey : datavalue})
    for descrow in descriplist:
        descdata=descrow.xpath('.//li//span//text()')
        if descdata:
            descriptiontext+=descdata[0]
    product_exprice = ''.join(ex_price).replace(',', '')
    product_price = ''.join(noex_price).replace(',', '')
    product_name = ''.join(raw_product_name).strip()          


                        
    exprice =''.join(filter(lambda x: x.isdigit(), product_exprice))
    total_reviews=raw_total_reviews
    data ={
            'Product Name': product_name,
            'Price without exchange': product_price,
            'Price with exchange': exprice,
            'Product Color': color,
            'Total Reviews':str(total_reviews),
            'Description':descdata,
            'Ratings':ratings_dict,
            #'Technical Details':techdet_dict
            
          }

    
    #saving fullsize image
    #URl = http://ecx.images-amazon.com/images/I/41qJGxrMW0L._SL500_AA300_.jpg
    #urllib.urlretrieve(URL, "000001.jpg")
    id=collec.insert_one(data)
    print("Success: "+str(id))


    
def ParseReviews(asin):  
    review_url_p1= 'https://www.amazon.in/product-reviews/'+asin+'/ref=cm_cr_getr_d_paging_btm_next_'
    review_url_p2= '?ie=UTF8&reviewerType=all_reviews&pageNumber='
    pagenumber=10
    extracted_data = []
    collec=db["test2"]
    #f = open('data.json', 'w')
    # Adding some recent user agent 
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}

    for j in range(pagenumber):
        amazonurl=review_url_p1+str(j)+review_url_p2+str(j)
        response = get(amazonurl, headers = headers, verify=False, timeout=30)
        if response.status_code == 404:
            return {"url": amazon_url, "error": "page not found"}
        if response.status_code != 200:
            continue
        for i in range(10):
            # Removing the null bytes from the response.
            cleaned_response = response.text.replace('\x00', '')
            '''
            parser = html.fromstring(cleaned_response)
            XPATH_AGGREGATE = '//span[@id="acrCustomerReviewText"]'
            XPATH_REVIEW_SECTION_1 = '//div[contains(@id,"reviews-summary")]'
            XPATH_REVIEW_SECTION_2 = '//div[@data-hook="review"]'
)
            reviews = parser.xpath(XPATH_REVIEW_SECTION_1)

            product_price = ''.join(raw_product_price).replace(',', '')
            product_name = ''.join(raw_product_name).strip()          '''


            parser = html.fromstring(cleaned_response)
            #XPATH_AGGREGATE = '//span[@id="acrCustomerReviewText"]'
            XPATH_REVIEW_SECTION_1 = '//div[contains(@id,"reviews-summary")]'
            XPATH_REVIEW_SECTION_2 = '//div[@data-hook="review"]'
            XPATH_AGGREGATE_RATING = '//table[@id="histogramTable"]//tr'
##            XPATH_PRODUCT_NAME = '//h1//span[@id="productTitle"]//text()'
##            XPATH_PRODUCT_PRICE = '//span[@id="priceblock_dealprice"]/text()'

##            raw_product_price = parser.xpath(XPATH_PRODUCT_PRICE)
##            raw_product_name = parser.xpath(XPATH_PRODUCT_NAME)
            total_ratings  = parser.xpath(XPATH_AGGREGATE_RATING)
            reviews = parser.xpath(XPATH_REVIEW_SECTION_1)

            
           
            if not reviews:
                reviews = parser.xpath(XPATH_REVIEW_SECTION_2)
            ratings_dict = {}
            reviews_list = []

            #Grabing the rating  section in product page
            for ratings in total_ratings:
                extracted_rating = ratings.xpath('./td//a//text()')
                if extracted_rating:
                    rating_key = extracted_rating[0] 
                    raw_raing_value = extracted_rating[1]
                    rating_value = raw_raing_value
                    if rating_key:
                        ratings_dict.update({rating_key: rating_value})
            
            # Parsing individual reviews
            for review in reviews:
                XPATH_RATING  = './/i[@data-hook="review-star-rating"]//text()'
                XPATH_REVIEW_HEADER = './/a[@data-hook="review-title"]//text()'
                XPATH_REVIEW_POSTED_DATE = './/span[@data-hook="review-date"]//text()'
                XPATH_REVIEW_TEXT_1 = './/div[@data-hook="review-collapsed"]//text()'
                XPATH_REVIEW_TEXT_2 = './/div//span[@data-action="columnbalancing-showfullreview"]/@data-columnbalancing-showfullreview'
                XPATH_REVIEW_COMMENTS = './/span[@data-hook="review-comment"]//text()'
                XPATH_AUTHOR = './/span[contains(@class,"profile-name")]//text()'
                XPATH_REVIEW_TEXT_3 = './/div[contains(@id,"dpReviews")]/div/text()'
                XPATH_REVIEW_TEXT_4 = './/span[@data-hook="review-body"]//text()'
                
                
                raw_review_author = review.xpath(XPATH_AUTHOR)
                raw_review_rating = review.xpath(XPATH_RATING)
                raw_review_header = review.xpath(XPATH_REVIEW_HEADER)
                raw_review_posted_date = review.xpath(XPATH_REVIEW_POSTED_DATE)
                raw_review_text1 = review.xpath(XPATH_REVIEW_TEXT_1)
                raw_review_text2 = review.xpath(XPATH_REVIEW_TEXT_2)
                raw_review_text3 = review.xpath(XPATH_REVIEW_TEXT_3)
                raw_review_text4 = review.xpath(XPATH_REVIEW_TEXT_4)

                # Cleaning data
                author = ' '.join(' '.join(raw_review_author).split())
                review_rating = ''.join(raw_review_rating).replace('out of 5 stars', '')
                review_header = ' '.join(' '.join(raw_review_header).split())

                try:
                    review_posted_date = dateparser.parse(''.join(raw_review_posted_date)).strftime('%d %b %Y')
                except:
                    review_posted_date = None
                review_text = ' '.join(' '.join(raw_review_text1).split())

                # Grabbing hidden comments if present
                if raw_review_text2:
                    json_loaded_review_data = loads(raw_review_text2[0])
                    json_loaded_review_data_text = json_loaded_review_data['rest']
                    cleaned_json_loaded_review_data_text = re.sub('<.*?>', '', json_loaded_review_data_text)
                    full_review_text = review_text+cleaned_json_loaded_review_data_text
                else:
                    full_review_text = review_text
                if not raw_review_text1:
                    full_review_text = ' '.join(' '.join(raw_review_text4).split())

                raw_review_comments = review.xpath(XPATH_REVIEW_COMMENTS)
                review_comments = ''.join(raw_review_comments)
                review_comments = sub('[A-Za-z]', '', review_comments).strip()
                review_dict = {
                                    
                                    'review_text': full_review_text,
                                    'review_posted_date': review_posted_date,
                                    'review_header': review_header,
                                    'review_rating': review_rating,
                                    'review_author': author

                                }
                #reviews_list.append(review_dict)

                data = {
                        
                        'reviews': review_dict,
                                           
                        }
                id=collec.insert_one(data)
                print("Success: "+str(id))
            
            #return data
            #extracted_data.append(data)
            #dump(extracted_data, f, indent=4)
            
        #return {"error": "failed to process the page", "url": amazon_url}
    #f.close()
            

def ReadAsin():
    # Add your own ASINs here
    AsinList = ['B07DJHY82F']
    extracted_data = []
    
    for asin in AsinList:
        print("Downloading and processing page http://www.amazon.com/dp/" + asin)
        Parsedata(asin)
        ParseReviews(asin)
        
        sleep(5)
##        f = open('data.json', 'w')
##        dump(extracted_data, f, indent=4)
##        f.close()

if __name__ == '__main__':
    client = MongoClient('localhost:27017')
##    dblist = Client.list_database_names()
##    if "webscraperdb" not in dblist:
        #database doesnt exist
    db=client["webscraperdb"];
##    collist = db.list_collection_names()
##    if "test1" not in collist:
        #collection doesnt exist
    collec=db["test1"]
        

        
    
    ReadAsin()
