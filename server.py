
import time
import BaseHTTPServer
import urllib
import urllib2
from urlparse import urlparse, parse_qs
import json
from bs4 import BeautifulSoup
import re
from random import randrange

HOST_NAME = 'localhost'
PORT_NUMBER = 9000 
names = []
query = ""
diff = {}
def read_by_line(filename):
    return [line for line in open(filename, 'r')]

def get_soup(url,header):
    return BeautifulSoup(urllib2.urlopen(urllib2.Request(url,headers=header)),'html.parser')

def get_names(filename):
    url="http://www.biographyonline.net/people/famous-100.html"
    header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
    soup = get_soup(url, header)
    i=0
    position=soup.find('div', {"class":"page"})
    out = open(filename, 'w')
    for row in position.findAllNext('li', limit=100):
        out.write(re.split(re.escape(' ('), row.get_text().encode('utf-8'))[0] + "\n")
    out.close()
    
def get_images(query):
    url="https://www.google.co.in/search?q="+query+"&source=lnms&tbm=isch"
    print url
    header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
    soup = get_soup(url,header)
    images=[]
    for a in soup.find_all("div",{"class":"rg_meta"}):
        link=json.loads(a.text)["ou"].encode('ascii')
        images.append(link)
        if (len(images) > 29):
            break
    return images

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        if s.path == '/favicon.ico':
            return
        global names
        global query
        global diff
        key="low"
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        query_components = parse_qs(urlparse(s.path).query)
        try:
            get_diff = query_components["diff"]
            val = diff[get_diff[0]]
        except:
            print "get_diff is empty"
            val = diff["low"]
        index = randrange(0, val)
        image_index = randrange(0, 30)
        query = names[index].replace("\n", "").replace(" ", "") 
        s.wfile.write("<html><head><title>Title goes here.</title></head>")
        s.wfile.write("<body><p>This is a test.</p>")
        s.wfile.write("<img src="+get_images(query)[image_index]+">")
        s.wfile.write('<form method="post">')
        s.wfile.write('<input type="text" name="person">')
        s.wfile.write('<input type="submit" value="Ok">')
        s.wfile.write("</form>")
        s.wfile.write('<br>')
        s.wfile.write('<form method="get">')
        s.wfile.write('<p><b>Choose your level</b></p>')
        s.wfile.write('<p><input name="diff" type="radio" value="low" checked> low</p>')
        s.wfile.write('<p><input name="diff" type="radio" value="mid"> mid</p>')
        s.wfile.write('<p><input name="diff" type="radio" value="hard"> hard</p>')
        s.wfile.write('<p><input type="submit" value="OK"></p>')
        s.wfile.write("</form>")
        s.wfile.write("</body></html>")
    def do_POST(s):
        global query
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write("<html><head><title>Result</title></head>")
        s.wfile.write("<body><p>Result</p>")
        length = int(s.headers.getheader('content-length'))
        field_data = s.rfile.read(length)
        fields = urlparse(field_data)
        answer = str(fields[2]).replace("person=","").lower().replace(" ", "").replace("+", "")
        if (answer == query.lower()):
            s.wfile.write("<body><p>You are right</p>")
        else:
            s.wfile.write("<body><p>You are wrong</p>")
        s.wfile.write('<form method="get">')
        s.wfile.write('<p><b>Choose your level</b></p>')
        s.wfile.write('<p><input name="diff" type="radio" value="low" checked> low</p>')
        s.wfile.write('<p><input name="diff" type="radio" value="mid"> mid</p>')
        s.wfile.write('<p><input name="diff" type="radio" value="hard"> hard</p>')
        s.wfile.write('<p><input type="submit" value="OK"></p>')
        s.wfile.write("</form>")    
        s.wfile.write("</body></html>")   

server_class = BaseHTTPServer.HTTPServer
httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
get_names("guess.txt")
names = read_by_line("guess.txt")
diff["low"] = 10
diff["mid"] = 50
diff["hard"] = 100
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
