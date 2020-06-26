import requests
import argparse
import os
import threading
from collections import deque
import colorama
from termcolor import colored
from bs4 import BeautifulSoup
import time

colorama.init()

parser = argparse.ArgumentParser()
parser.add_argument("url", metavar="url", type=str, help="url. Must have form https://upload.2ch.hk/*")
parser.add_argument("-o", type=str, action="store", dest="dir", default="./data/", help="Output directory. ./data/ by default.")
parser.add_argument("-a", action="store_true", dest="archive", help="Create archive in output directory")
parser.add_argument("-t", type=int, action="store", dest="threads", default=1, help="Num of threads. (future)")
args = parser.parse_args()

if not os.path.isabs(args.dir):
    args.dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.dir)

if not os.path.isdir(args.dir):
    os.makedirs(args.dir)

# TODO threads check 

queue = deque()

try:
    page = requests.get(args.url)
    if page.status_code != 200:
        print(colored("[ERROR] site return code {page.status_code}", "red"))
        exit()
    print(colored("[OK] {0} is avalible".format(args.url), "green"))
except:
    print(colored("[ERROR] site can not be reacheble", "red"))
    exit()

soup = BeautifulSoup(page.text.encode("utf-8"), "html.parser")
fileboxes = soup.findAll("div", {"class": "filesbox"})
print("[INFO] founded {0} files".format(len(fileboxes)))

for link in fileboxes:
    a = link.find("a", href = True)
    queue.append(a["href"])

def Download(link):
    img = requests.get("https://upload.2ch.hk" + link)
    name = os.path.basename(link)
    with open(os.path.join(args.dir, name), "wb") as file:
        file.write(img.content)
        file.close()
    print(colored("[OK] image {0} downloaded".format(name), "green"))

def GetNext():
    _next = queue.pop() if len(queue) > 0 else None
    if _next == None:
        return
    t = threading.Thread(target=Download, args=[_next])
    t.start()
    t.join()
    GetNext()

for t in range(args.threads):
    GetNext()

if args.archive:
    print("[INFO] creating archive")
    aname = os.path.basename(args.dir)
    archive = os.path.join(args.dir, aname + ".rar")
    os.system('rar a -ep1 -idq -r -y "{0}" "{1}"'.format(archive, args.dir))
    print(colored("[OK] archive {0} was created".format(archive), "green"))