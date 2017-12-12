import urllib.request;
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import subprocess

Result = 'The word not found: \n'
def notFound(word):
    print('*****{}: not found*****'.format(word))
    global Result
    Result += word
def lookUp(word):
    word = word.replace(' ', '-')
    url="http://dictionary.cambridge.org/dictionary/english-chinese-traditional/{}".format(word)
    try:
        content = urllib.request.urlopen(url).read()
    except urllib.error.URLError as e:
        print(e.reason)
        return
    except urllib.error.HTTPError as e:
        print(e.reason, e.code, e.headers, sep='\n')
        return
    soup = BeautifulSoup(content, 'lxml', \
                         parse_only = SoupStrainer('div', \
                         class_= 'entry-body__el clrd js-share-holder'))
    entry_body = soup.find_all('div', class_='entry-body__el clrd js-share-holder')

    if len(entry_body) == 0 : 
        notFound(word)
    else:
        for entry in entry_body:
            #單字
            headword = entry.select('.pos-header .headword')
            if len(headword) == 0:
                notFound(word)
                continue
            else:
                headword = headword[0].get_text()
                print('headword={}'.format(headword))
                file.write(headword + ';')

            #音標  0 為 UK
            posgram = entry.select('.pron-info .uk .pron')
            if len(posgram) > 1:
                posgram = posgram[1].get_text()
            elif len(posgram) == 1:
                posgram = posgram[0].get_text()
            print('posgram={}'.format(posgram))
            file.write(posgram + ';')
            #詞性
            ipa = entry.select('.posgram')
            if len(ipa) != 0:
                ipa = ipa[0].get_text()
            else:
                ipa = ''
            print('ipa={}'.format(ipa))
            file.write(ipa + ';')

            sense_bodys = entry.find_all('div', class_='sense-body')

            file.write('<ol type="I">')
            for sense_body in sense_bodys:
                for index, child in enumerate(sense_body.children):
                    try:
                        if isinstance(child['class'].index('def-block'), int):
                            #意思
                            trans = child.select('.def-body .trans')
                            trans = trans[0].get_text("", strip=True)
                            print('trans={}'.format(trans))
                            file.write("<li>" + trans + "</li>")
                    except (ValueError,TypeError) as e:
                        pass
            file.write('</ol>;')

            for sense_body in sense_bodys:
                for index, child in enumerate(sense_body.children):
                    try:
                        if isinstance(child['class'].index('def-block'), int):
                            #例句
                            example = child.select('.examp')
                            if len(example) != 0:
                                file.write("<div class='def-block'>")
                                file.write("<div class='trans'>" + child.select('.def-body .trans')[0].get_text("", strip=True) + "</div>")
                                for i in example:
                                    examp_eg = ''
                                    examp_trans = ''
                                    if len(i.select('.eg')) != 0:
                                        examp_eg = i.select('.eg')[0].get_text()
                                    if len(i.select('.trans')) != 0 :
                                        examp_trans = i.select('.trans')[0].get_text("", strip=True)
                                    print('example={}'.format(examp_eg))
                                    print('example_trans={}'.format(examp_trans))
                                    file.write("<div class='examp'>")
                                    file.write("<span>" + examp_eg + "</span>")
                                    file.write("<span>" + examp_trans + "</span>")
                                    file.write("</div>")
                                file.write("</div>")
                    except (ValueError,TypeError) as e:
                        pass
            file.write(';')

            #mp3檔案
            file.write('[sound:' + headword + '.mp3]\n')
            soundsURL = entry.select('.pron-info .us .sound')
            if len(soundsURL) != 0:
                dlmp3 = urllib.request.urlopen(soundsURL[0]['data-src-mp3'])
                with open( './result/mp3/' + headword + '.mp3', 'wb') as mp3File:
                    mp3File.write(dlmp3.read())

            # 額外的片語卡片
            phrase_blocks = entry.find_all('div', class_='phrase-block')
            for phrase_block in phrase_blocks:
                phrase_title = phrase_block.select('.phrase-head .phrase-title .phrase')
                phrase_title = phrase_title[0].get_text()
                print('phrase_title={}'.format(phrase_title))
                file.write(phrase_title + ';;;')

                phrase_trans = phrase_block.select('.phrase-body .def-block .def-body .trans')
                phrase_trans = phrase_trans[0].get_text("", strip=True)
                print('phrase_trans={}'.format(phrase_trans))
                file.write(phrase_trans + ';')

                phrase_example = phrase_block.select('.phrase-body .def-block .def-body .examp')
                if len(phrase_example) != 0:
                    file.write("<div class='def-block'>")
                    for i in phrase_example:
                        examp_eg = ''
                        examp_trans = ''
                        if len(i.select('.eg')) != 0:
                            examp_eg = i.select('.eg')[0].get_text()
                        if len(i.select('.trans')) != 0 :
                            examp_trans = i.select('.trans')[0].get_text("", strip=True)
                        print('phrase_example={}'.format(examp_eg))
                        print('phrase_exampleZh={}'.format(examp_trans))
                        file.write("<div class='examp'>")
                        file.write("<span>" + examp_eg + "</span>")
                        file.write("<span>" + examp_trans + "</span>")
                        file.write("</div>")
                    file.write('</div>')
                file.write(';[sound:' + headword + '.mp3]\n')



with open("./input", "r") as inputFile:
    file = open('./result/anki.txt', 'w')
    for word in inputFile:
        lookUp(word)
    file.close()
    print('{}'.format(Result))