#!/usr/bin/python3

from bs4 import BeautifulSoup as Soup
from time import strftime
import sys
import urllib.request
import re
import os
import json

sysLog = ''

def sysMsg (msg):
    global sysLog
    msg = strftime("[%H:%M:%S] ") + msg
    print(msg, file=sys.stderr)
    sysLog += msg + "\n"

def request (url, data = None):
    sysMsg('Request to ' + url);
    if data is not None:
        data = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        }
    )
    with urllib.request.urlopen(req) as url:
        html = url.read()
    return html

def crawlBlog(id, backup_dir):
    blog = {}
    blog['url'] = 'https://' + id + '.tian.yam.com/posts'
    blog['time_crawl'] = strftime("%Y-%m-%d %H:%M:%S %Z")
    
    sysMsg("Backup account = " + id)
    sysMsg("Start at " + blog['time_crawl'])
    html = request(blog['url'])
    soup = Soup(html, 'html.parser')
    
    os.makedirs(backup_dir + '/blog')
    
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    
    blog['name'] = soup.select('div.txt-des')[0].get_text().strip()
    blog['description'] = soup.select('h1.blog-headline')[0].get_text().strip()
    
    sysMsg('Fetching article list')
    
    page = 1
    blog['articles'] = []
    
    while True:
        articles = soup.select('div.post-content-block.block-edit')
        for article in articles:
            if article['data-id'] is not None:
                blog['articles'].append({
                    'id': article['data-id'],
                    'summary': str(article),
                    's_title': str(article.select('.post-title h3 a')[0].get_text().strip())
                })
        sysMsg('Collected ' + str(len(blog['articles'])) + ' article(s)')
        if len(soup.select('.pagination a[aria-label|=Next]')) > 0:
            page += 1
            html = request(blog['url'] + '?page=' + str(page))
            soup = Soup(html, 'html.parser')
        else:
            break
    
    blog_img_pattern = re.compile(' src="(http://([^"]+)/(\w+\.\w\w\w))"')
    
    for i,article in enumerate(blog['articles']):
        sysMsg('Fetching article (' + str(i) + '/' + str(len(blog['articles'])) + ') ' + article['id'] + ' ' + article['s_title'])
        os.makedirs(backup_dir + '/blog/' + article['id'] + '/images')
        html = request(blog['url'] + '/' + article['id'])
        soup = Soup(html, 'html.parser')
    
        content = None
        while content is None:
            article_title = soup.select('div.post-title h1')
            if len(article_title) > 0:
                blog['articles'][i]['title'] = soup.select('div.post-title h1')[0].get_text().strip()
                content = str(soup.select('div.post-content')[0])
            elif len(soup.select('input#mask-passwd')) > 0:
                sysMsg('This article is protected by password')
                passwd = input('Password for ' + article['s_title'] + ' ' + blog['url'] + '/' + article['id'] + ' : ')
                html = request(blog['url'] + '/' + article['id'], {'passwd' : passwd})
                soup = Soup(html, 'html.parser')
            else:
                sysMsg('fail to backup blog article ' + blog['url'] + '/' + article['id'])
                die()
    
        content = article['summary'] + '<hr>' + content
    
        blog['articles'][i]['images'] = []
        for match in blog_img_pattern.findall(content):
            sysMsg('Download ' + match[0])
            imgError = None
            try:
                urllib.request.urlretrieve(match[0], backup_dir + '/blog/' + article['id'] + '/images/' + match[2])
            except urllib.error.HTTPError as err:
                sysMsg(str(err))
                imgError = str(err)
                None
            if imgError is not None:
                content = content.replace(match[0], match[0] + '" crawler-comment="error: ' + imgError)
            else:
                content = content.replace(match[0], 'images/' + match[2])
            blog['articles'][i]['images'].append([match[0], match[2], imgError])
        blog['articles'][i]['content'] = content
        human_file = open(backup_dir + '/blog/' + article['id'] + '/index.html', 'x')
        human_file.write('<!DOCTYPE html><html><head><meta charset="utf-8"><title>' + blog['articles'][i]['title'] + '</title></head><body>')
        human_file.write('<h1>' + blog['articles'][i]['title'] + '</h1>')
        human_file.write('<div>Backup from: <a href="' + blog['url'] + '/' + article['id'] + '">' + blog['url'] + '/' + article['id'] + '</a> at ' + blog['time_crawl'] + '</div><hr>');
        human_file.write(content)
        human_file.write('</body></html>')
        human_file.close()
        try:
            human_file = open(backup_dir + '/blog/' + article['id'] + '/' + article['title'], 'x')
            human_file.close()
        except:
            None
    
    machine_file = open(backup_dir + '/blog/data.json', 'x')
    machine_file.write(json.dumps(blog))
    machine_file.close()

def crawlAlbum(id, backup_dir):
    sysMsg('Start working on album')

    ab = {}
    ab['url'] = 'https://' + id + '.tian.yam.com/albums'
    ab['url_ajax'] = 'https://' + id + '.tian.yam.com/ajax/album/fetch'
    ab['url_base'] = 'https://' + id + '.tian.yam.com/album/'
    
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)

    sysMsg('Fetching album list')

    html = request(ab['url'])
    soup = Soup(html, 'html.parser')
    ab['albums'] = []
    page = 1

    while True:
        albums = soup.select('div.album-block')
        for album in albums:
            if album['data-id'] is not None:
                photos = album.select('.img-wrap img')
                if len(photos) > 0:
                    photos = [{'url': photos[0]['src'], 'id': 'COVER', 'name': 'COVER'}]
                else:
                    photos = []
                ab['albums'].append({
                    'id': album['data-id'],
                    's_title': album.select('h5.album-title')[0].get_text().strip(),
                    'photos': photos,
                    'url': ab['url_base'] + album['data-id']
                })
        sysMsg('Collected ' + str(len(ab['albums'])) + ' album(s)')
        if len(soup.select('.pagination a[aria-label|=Next]')) > 0:
            page += 1
            html = request(ab['url'] + '?page=' + str(page))
            soup = Soup(html, 'html.parser')
        else:
            break

    for album in ab['albums']:
        genHtml = '<!DOCTYPE html><html><head><meta charset="utf-8"><title>' + album['s_title'] + '</title></head><body>'
        genHtml += '<h1>' + album['s_title'] + '</h1>'
        genHtml += '<a href="' + album['url'] + '">' + album['url'] + '</a>'
        sysMsg('Process ' + album['url'] + ' ' + album['s_title'])
        os.makedirs(backup_dir + '/albums/' + album['id'] + '/images')
        page = 1
        while True:
            html = request(ab['url_ajax'] + '?albumId=' + album['id'] + '&page=' + str(page), {'albumId' : album['id'], 'page' : str(page)})
            res = json.JSONDecoder().decode(str(html)[2:-1].replace("\n",'').replace('\\','\\\\'))
            page += 1
            for p in res['photos']:
                album['photos'].append(p)
            if res['lastPage']:
                break
        for photo in album['photos']:
            imgError = None
            try:
                urllib.request.urlretrieve(photo['url'], backup_dir + '/albums/' + album['id'] + '/images/' + photo['id'] + photo['url'][-4:])
            except urllib.error.HTTPError as err:
                sysMsg(str(err))
                imgError = str(err)
                None
            if imgError is not None:
                photo['has_error'] = imgError
            genHtml += '<div class="photo"><h2>' + photo['name'] + '</h2><a href="' + photo['url'] + '">' + photo['url'] + '</a><img src="images/' + photo['id'] + photo['url'][-4:] + '"></div>'
        human_file = open(backup_dir + '/albums/' + album['id'] + '/index.html', 'x')
        human_file.write(genHtml + '</body></html>');
        human_file.close()
        try:
            human_file = open(backup_dir + '/albums/' + album['id'] + '/n_' + album['s_title'], 'x')
            human_file.close()
        except:
            None
    machine_file = open(backup_dir + '/albums/data.json', 'x')
    machine_file.write(json.dumps(ab))
    machine_file.close()


id = sys.argv[1]
task = sys.argv[2]
    
backup_dir = 'bak_' + id + '_' + strftime("%Y%m%d%H%M%S")
os.makedirs(backup_dir)

if task == "all" or task == "blog":
    crawlBlog(id, backup_dir)
if task == "all" or task == "album":
    crawlAlbum(id, backup_dir)


sysMsg('Done')

machine_file = open(backup_dir + '/log.txt', 'x')
machine_file.write(sysLog)
machine_file.close()
