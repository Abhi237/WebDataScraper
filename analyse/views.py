from django.shortcuts import render
from celery import task
from django.template.loader import render_to_string
from . import Scrapedata
from django.shortcuts import render_to_response
from django.http import HttpResponse,JsonResponse
import pdb
import json


def home(request):
   
    return render(request,'analyse/home.html')
    
def result(request):
    
    asin=request.POST.get('asin',None)
    if not asin:
        asin=""
    context=Scrapedata.Getdata(asin)
    return render(request,'analyse/result.html',context)


def sentiment(request):  
    if 'reviewdata' in request.POST:
        data=request.POST['reviewdata']
        obj=json.loads(data)
        sentimentdata=Scrapedata.sentimentanalyser(obj)
        return HttpResponse(json.dumps(sentimentdata))
    else:
        return HttpResponse(json.dumps('[{Data error":"not found"}]'))


def reviews(request):
    asin=request.POST['asin']
    datalist=Scrapedata.ParseReviews(asin)
    #pdb.set_trace()
    return HttpResponse(json.dumps(datalist))
    