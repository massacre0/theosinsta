#!/bin/env python3

import requests
import random
import json
import sys
from local import *

resp_js = None
is_private = False
total_uploads = 12

def proxy_session():
	session = requests.session()
	session.proxies = {
		'http':  'socks5://127.0.0.1:9050',
		'https': 'socks5://127.0.0.1:9050'
	}
	return session

def get_page(usrname):
	global resp_js
	session = requests.session()
	session.headers = {'User-Agent': random.choice(useragent)}
	resp_js = session.get('https://www.instagram.com/'+usrname+'/?__a=1').text
	return resp_js

def exinfo():

	def xprint(xdict, text):
		if xdict != {}:
			print(f"{su} {re}en çok kullanılan %s :" % text)
			i = 0
			for key, val in xdict.items():
				if len(mail) == 1:
					if key in mail[0]:
						continue
				print(f"  {gr}%s : {wh}%s" % (key, val))
				i += 1
				if i > 4:
					break
			print()
		else:
			pass
	
	raw = find(resp_js)

	mail = raw['email']
	tags = sort_list(raw['tags'])
	ment = sort_list(raw['mention'])

	if mail != []:
		if len(mail) == 1:
			print(f"{su} {re}e-posta bulundu : \n{gr}  %s" % mail[0])
			print()
		else:
			print(f"{su} {re}e-posta bulundu : \n{gr}  ")
			for x in range(len(mail)):
				print(mail[x])
			print()

	xprint(tags, "etiketler")
	xprint(ment, "bahseden")
	
def user_info(usrname):

	global total_uploads, is_private
	
	resp_js = get_page(usrname)
	js = json.loads(resp_js)
	js = js['graphql']['user']
	
	if js['is_private'] != False:
		is_private = True
	
	if js['edge_owner_to_timeline_media']['count'] > 12:
		pass
	else:
		total_uploads = js['edge_owner_to_timeline_media']['count']

	usrinfo = {
		'Kullanıcı adı': js['username'],
		'Kullanıcı id': js['id'],
		'İsim': js['full_name'],
		'Takipçiler': js['edge_followed_by']['count'],
		'Takip ettiği': js['edge_follow']['count'],
		'Post fotoğrafları': js['edge_owner_to_timeline_media']['count'],
		'Post videoları': js['edge_felix_video_timeline']['count'],
		'Reels': js['highlight_reel_count'],
		'Biografi': js['biography'].replace('\n', ', '),
		'Harici url': js['external_url'],
		'Özel': js['is_private'],
		'Doğrulandı': js['is_verified'],
		'Profil fotoğrafı': urlshortner(js['profile_pic_url_hd']),
		'İş Hesabı': js['is_business_account'],
		#'connected to fb': js['connected_fb_page'],  -- requires login
		'Yenimi katıldı': js['is_joined_recently'],
		'İş kategorisi': js['business_category_name'],
		'Kategori': js['category_enum'],
		'kılavuzları var': js['has_guides'],
	}

	banner()

	print(f"{su}{re} Kullanıcı Bilgileri")
	for key, val in usrinfo.items():
		print(f"  {gr}%s : {wh}%s" % (key, val))

	print("")

	exinfo()

def highlight_post_info(i):

	postinfo = {}
	total_child = 0
	child_img_list = []

	x = json.loads(resp_js)
	js = x['graphql']['user']['edge_owner_to_timeline_media']['edges'][i]['node']

	# this info will be same on evry post
	info = {
		'yorum': js['edge_media_to_comment']['count'],
		'yorum devre dışı': js['comments_disabled'],
		'zaman damgası': js['taken_at_timestamp'],
		'beğeni': js['edge_liked_by']['count'],
		'konum': js['location'],
	}

	# if image dosen't have caption this key dosen't exist instead of null
	try:
		info['caption'] = js['edge_media_to_caption']['edges'][0]['node']['text']
	except IndexError:
		pass

	# if uploder has multiple images / vid in single post get info how much edges are
	if 'edge_sidecar_to_children' in js:
		total_child = len(js['edge_sidecar_to_children']['edges'])

		for child in range(total_child):
			js = x['graphql']['user']['edge_owner_to_timeline_media']['edges'][i]['node']['edge_sidecar_to_children']['edges'][child]['node']
			img_info = {
				'tür adı': js['__typename'],
				'id': js['id'],
				'kısa kod': js['shortcode'],
				'boyutlar': str(js['dimensions']['height'] + js['dimensions']['width']),
				'fotoğraf  url' : js['display_url'],
				'genel olarak doğruluk kontrolü': js['fact_check_overall_rating'],
				'doğruluk kontrolü': js['fact_check_information'],
				'geçiş bilgisi': js['gating_info'],
				'medya yer paylaşım bilgisi': js['media_overlay_info'],
				' video': js['is_video'],
				'ulaşılabilirlik': js['accessibility_caption']
			}

			child_img_list.append(img_info)

		postinfo['fotoğraflar'] = child_img_list
		postinfo['bilgi'] = info

	else:
		info = {
			'yorum': js['edge_media_to_comment']['count'],
			'yorum devre dışı': js['comments_disabled'],
			'zaman damgası': js['taken_at_timestamp'],
			'beğeniler': js['edge_liked_by']['count'],
			'konum': js['location'],
		}

		try:
			info['caption'] = js['edge_media_to_caption']['edges'][0]['node']['text']
		except IndexError:
			pass

		img_info = {
				'tür adı': js['__typename'],
				'id': js['id'],
				'kısa kod': js['shortcode'],
				'boyutlar': str(js['dimensions']['height'] + js['dimensions']['width']),
				'resim url' : js['display_url'],
				'genel olarak doğruluk kontrolü': js['fact_check_overall_rating'],
				'doğruluk kontrolü': js['fact_check_information'],
				'geçit bilgisi': js['gating_info'],
				'medya bindirme bilgisi': js['media_overlay_info'],
				'video': js['is_video'],
				'ulaşılabilirlik': js['accessibility_caption']
			}
		
		child_img_list.append(img_info)
		
		postinfo['fotoğraflar'] = child_img_list
		postinfo['bilgi'] = info

	return postinfo

def post_info():
	
	if is_private != False:
		print(f"{fa} {gr}-p özel hesaplar için kullanılamaz !\n")
		sys.exit(1)
	
	posts = []
	
	for x in range(total_uploads):
		posts.append(highlight_post_info(x))

	for x in range(len(posts)):
		# get 1 item from post list
		print(f"{su}{re} post %s :" % x)
		for key, val in posts[x].items():
			if key == 'fotoğraflar':
				# how many child imgs post has
				postlen = len(val)
				# loop over all child img
				print(f"{su}{re} içerir %s medya" % postlen) 
				for y in range(postlen):
					# print k,v of all child img in loop
					for xkey, xval in val[y].items():
						print(f"  {gr}%s : {wh}%s" % (xkey, xval))
			if key == 'bilgi':
				print(f"{su}{re} bilgi :")
				for key, val in val.items():
					print(f"  {gr}%s : {wh}%s" % (key, val))
				print("")	
