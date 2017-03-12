#!/bin/env python 
#encoding=utf-8

from django.shortcuts import render,render_to_response
from django.http import HttpResponse,JsonResponse
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from wechatpy import parse_message, create_reply
from django.views.decorators.csrf import csrf_exempt
from wechatpy import parse_message
from wechatpy.replies import TextReply
from wechatpy.replies import ImageReply
import urllib
import sys
import os
import cv
import time
import commands
import json

path='/root/home'

TOKEN = 'douban_book'
appID='wx9771152873650093'
appsecret='637423ac0b9d7cdc50acda53c7bc8e4e'


# Create your views here.

@csrf_exempt
def home(request):
	if request.method=='GET':
		signature = request.GET.get('signature')
		timestamp = request.GET.get('timestamp')
		nonce = request.GET.get('nonce', None)
		echo_str = request.GET.get('echostr')
		print(signature,"   ",timestamp,"    ",nonce)
		try:
			check_signature(TOKEN, signature, timestamp, nonce)
		except InvalidSignatureException:
			return HttpResponse("hello world")
		return HttpResponse(echo_str,content_type="text/plain")
	msg = parse_message(request.body)
	print(msg.type)
	if(msg.type=='text'):
		reply = TextReply(content="you say:%s"%msg.content, message=msg)
		xml=reply.render()
		return HttpResponse(xml)
	elif(msg.type=='image'):
		url=msg.image
		f=open(path+"/aaa.jpg",'wb')
		str1=urllib.urlopen(url).read()
		f.write(str1)
		f.close()
		image = cv.LoadImage(path+"/aaa.jpg",1)
		size = (image.width,image.height)
		iUD = cv.CreateImage(size,image.depth,image.nChannels)
		h = image.height
		w = image.width
		for i in range(h):
			for j in range(w):
				iUD[i,w-j-1] = image[i,j]
		cv.WaitKey(0)
		cv.SaveImage(path+"/bbb.jpg",iUD)
		json_str=urllib.urlopen("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s"%(appID,appsecret)).read().decode("utf-8")
		access_token=json.loads(json_str)['access_token']
		json_str=commands.getoutput("curl -F media=@%s/bbb.jpg 'https://api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=image'"%(path,access_token))
		print(json_str)
		media_id=json_str.split(',')[1].split(':')[1].replace('"','')
		print(type(media_id))
		print(media_id)
		print(dir(media_id))
		xml ="""<xml>
			<ToUserName><![CDATA[%s]]></ToUserName>
			<FromUserName><![CDATA[%s]]></FromUserName>
			<CreateTime>%s</CreateTime>
			<MsgType><![CDATA[image]]></MsgType>
			<Image>
			<MediaId><![CDATA[%s]]></MediaId>
			</Image>
			</xml>
			"""%(msg.source,msg.target,time.time()+1,media_id)
		return HttpResponse(xml)







def index(request):
	return HttpResponse("hello index")
