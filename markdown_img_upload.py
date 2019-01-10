#coding=utf-8

import requests
import sys
import os
import re
import time

def img_upload(img_path,url='https://sm.ms/api/upload'):
    '''
    to upload an img to sm.ms
    :param img_path: should be absolute path
    :param url: the api of sm.ms
    :return: the link of sm.ms
    '''
    global img_count

    files={'smfile':open(img_path,'rb')}
    r=requests.post(url,files=files)
    img_count+=1
    data1=eval(r.text.encode('utf-8'))
    if data1['code']=='error':
        print(data1['msg'])
        return None
    url1=data1['data']['url']
    print(url1)
    if img_count%10==0 and img_count:
        print('Sleep...')
        time.sleep(5)
    return url1

def markdown_processing(markdown_path):
    texts=[]
    with open(markdown_path,mode='r',encoding='utf-8') as c:
        texts=c.readlines()
        new_texts=[]
        pattern=re.compile(r'!\[.*\]\(.*\)')
        for i,text in enumerate(texts):
            begin=0
            while(True):
                m=pattern.match(text,begin)
                if not m:
                    break
                place=re.search(r'\(.*\)',m.group())
                #中文路径与斜杠问题
                img_path=re.sub(r'\\','/',place.group()[1:-1])
                #解决非本地路径问题
                if re.match(r'http',img_path):
                    begin=m.end()
                    continue
                # print(type(img_path))
                # a=open(img_path,'rb')
                # t=a.read()
                img_path=rename_chinese_path(img_path)
                img_url=img_upload(img_path)

                if not img_url:
                    print('maybe you are blocked or the link of your path not right!')
                    begin=m.end()
                    continue

                new_code=re.sub(r'\(.*\)','('+img_url+')',m.group(),1)
                text=text[:m.span()[0]]+new_code+text[m.span()[1]:]
                begin=m.span()[0]+len(new_code)
            new_texts.append(text)
    with open(markdown_path,mode='w',encoding='utf-8') as c:
        c.writelines(new_texts)
    print('replace img path as link succeed!')

def rename_chinese_path(img_path):
    name=int(round(time.time()*1000)).__str__()+'.'
    temp_path=img_path.split('/')[0]+'/'
    for part in img_path.split('/')[1:-1]:
        temp_path=os.path.join(temp_path,part)
    try:
        new_name=os.path.join(temp_path,name+img_path.split('\\')[-1].split('.')[-1])
        os.rename(img_path,new_name)
        print(new_name)
        return new_name
    except FileNotFoundError:
        print('the path of {} not exist, please modify it'.format(img_path))
        exit(-1)


def main():
    if len(sys.argv)<2:
        print('!!!! please enter the path of markdown !!!!')
        exit(-1)
    else:
        markdown_processing(sys.argv[1])

if __name__=='__main__':
    img_count=0
    main()

