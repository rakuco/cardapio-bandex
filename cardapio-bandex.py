#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from xml.sax.saxutils import unescape
import urllib2
import re

class Menu(object):
  def __init__(self, values):
    self.fromDict(values)

  def fromDict(self, values):
    if not isinstance(values, dict):
      raise TypeError, "A dict object must be passed to Menu"

    if set(values.keys()) != set(['data', 'principal', 'sobremesa', 'salada',
                                  'suco']):
      raise ValueError, "Malformed dictionary passed to Menu"

    self.values = values

  def printMenu(self):
    for key in ('data', 'principal', 'salada', 'sobremesa', 'suco'):
      print '%s: %s' % (key, self.values[key])

  def printSMSMenu(self):
    ## Date
    data_re = re.match(r'(?:(.+) - )?([\d]{1,2}/[\d]{1,2})(?:\d{2,4})*',
                       self.values['data'])

    if not data_re:
      raise ValueError, "Invalid date format"

    if data_re.group(1) is not None:
      short_data = data_re.group(1)[:3] + ' ' + data_re.group(2)
    else:
      short_data = data_re.group(2)

    ## Principal
    short_principal = self.values['principal'].lower(). \
                                               replace(u'feijão', 'f'). \
                                               replace('arroz', 'a')

    ## Salada
    short_salada = self.values['salada'].lower()

    ## Sobremesa
    short_sobremesa = self.values['sobremesa'].lower()

    ## Suco
    short_suco = self.values['suco'].lower()

    ## Final message
    short_message = "%s - %s/Sl: %s/Sb: %s/Su: %s" % (short_data,
                                                      short_principal,
                                                      short_salada,
                                                      short_sobremesa,
                                                      short_suco)
    short_message = short_message.replace(', ', ',').replace('.', '')

    print len(short_message), short_message

class MenuParser(object):
  SOURCE_FIXES = [
    # <td background-color: "#ededed;"> becomes <td>
    (re.compile(r'\s*[-\w]+:\s*"[a-zA-Z0-9#;]+"'), lambda s: ''),
  ]
  SOURCE_URL = "http://www.prefeitura.unicamp.br/servicos.php?servID=119"

  def __init__(self):
    self.sourceText = self.getSource()

  def getSource(self):
    return urllib2.urlopen(MenuParser.SOURCE_URL).read()

  def getTagText(self, tag):
    """
    Receives a Tag object and returns its stripped text.
    """
    return ''.join(tag.findAll(text=True)).replace(unichr(160), ' ')

  def parseMenu(self):
    soup = BeautifulSoup(self.sourceText,
                         markupMassage = MenuParser.SOURCE_FIXES,
                         convertEntities = BeautifulStoneSoup.HTML_ENTITIES)

    menuKeys   = ('data', 'principal', 'sobremesa', 'salada', 'suco')

    # Add the entries which have the same format ('key: value')
    menuBlock  = soup.findAll('p', style="text-align: left")
    menuValues = []

    for line in menuBlock:
      strLine = self.getTagText(line)
      match   = re.match(r'[\w\s]+:\s*(.+)', strLine)

      if match:
        menuValues.append(match.group(1))

    # If there were only 4 entries in the usual format, probably date is missing
    if len(menuValues) == 4:
      # Add the date, whose format tends to vary.
      # Finding the main meal and simply retrieving the previous sibling
      # seems to be the most error-proof method.
      mainMeal = soup.find(text = re.compile(r"prato\s+principal", re.IGNORECASE)).parent.parent
      mealDate = mainMeal.findPreviousSibling('p')
      menuValues = [self.getTagText(mealDate)] + menuValues
    elif len(menuValues) != 4 and len(menuValues) != 5:
      raise ValueError, "The menu in the site has an invalid format"

    return Menu(dict(zip(menuKeys, menuValues)))

if __name__ == "__main__":
  app = MenuParser()

  menu = app.parseMenu()
  menu.printMenu()
  menu.printSMSMenu()
