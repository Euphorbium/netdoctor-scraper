import unicodecsv
import re
import time
import random
from lxml import html


f = open('netdoctor.csv', 'w')
w = unicodecsv.writer(f, encoding='utf-8', lineterminator='\n')
w.writerow(['uniqueID', 'qid', 'localID', 'title', 'poster', 'date', 'replyTo', 'content', 'infered_replies', 'tag' ],)

for i in range(1, 101):
    time.sleep(50 + random.random() * 10)
    print 'processing page', i
    page = html.parse('http://forums.netdoctor.co.uk/discussions/p'+str(i))
    for heading in page.xpath('//*[contains(@class, "ItemContent Discussion")]/*/a'):
        title = heading.text
        url = heading.attrib['href']
        tag = heading.xpath('./../..//*[contains(@class, "Category")]')[0].text_content()
        qid = re.findall(r'netdoctor.co.uk/discussion/(\d*)', url)[0]
        while True:
            try:
                thread = html.parse(url)
            except IOError:
                print 'stopped on', url
                time.sleep(30)
            break
        posters = set()
        try:
            pagers = thread.xpath('//*[contains(@class, "PagerWrap")]//a[contains(@class, "Next")]/preceding-sibling::a/text()')[-1]
        except IndexError:
            pagers = 1
        pager = 1
        while pager <= int(pagers):
            if pager == 1:
                pass
            else:
                while True:
                    try:
                        thread = html.parse(url+'/p'+str(pager))
                    except IOError:
                        print 'stopped on', url
                        time.sleep(30)
                    break
            time.sleep(5+random.random())
            for j, message in enumerate(thread.xpath('//*[@class="Message"]')):
                inferred_replies = set()
                localID = j-1+(pager-1)*30
                content = message.text_content().strip()
                poster = message.xpath('./../../..//a/text()')[0]
                date = message.xpath('./../../..//time/@datetime')[0]
                uniqueID = qid + '_' + str(localID) if localID > -1 else qid + '_top'
                replyTo = qid + '_top' if localID > -1 else " "
                for p in posters:
                    if p in content and not content.endswith(p):
                        inferred_replies.add(p)
                posters.add(poster)
                w.writerow([uniqueID, qid, localID, title, poster, date, replyTo, content, " ".join(inferred_replies), tag])
                f.flush()
            pager += 1

f.close()