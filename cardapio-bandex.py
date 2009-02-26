#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2009, Raphael Kubo da Costa <kubito@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

try:
  from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
except ImportError:
  import sys
  sys.stderr.write("This program needs BeautifulSoup to run.\n")
  sys.exit(1)

from xml.sax.saxutils import unescape
import urllib2
import re

class Menu(object):
  def __init__(self, values):
    self.fromDict(values)

  data      = property(lambda self: self.values['data'])
  principal = property(lambda self: self.values['principal'])
  salada    = property(lambda self: self.values['salada'])
  sobremesa = property(lambda self: self.values['sobremesa'])
  suco      = property(lambda self: self.values['suco'])

  def fromDict(self, values):
    """
    Validates and loads a dict with the menu values
    """
    if not isinstance(values, dict):
      raise TypeError, "A dict object must be passed to Menu"

    if set(values.keys()) != set(['data', 'principal', 'sobremesa', 'salada',
                                  'suco']):
      raise ValueError, "Malformed dictionary passed to Menu"

    self.values = values

  def printMenu(self):
    """
    Prints the menu in the usual, multi-line way.
    """
    for key in ('data', 'principal', 'salada', 'sobremesa', 'suco'):
      print '%s: %s' % (key, self.values[key])

  def printSMSMenu(self):
    """
    Prints the menu in a format suitable for SMS messages.
    """
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
    """
    Returns the HTML source which will be parsed.
    """
    return urllib2.urlopen(MenuParser.SOURCE_URL).read()

  def getTagText(self, tag):
    """
    Receives a Tag object and returns its stripped text.
    """
    return ''.join(tag.findAll(text=True)).replace(unichr(160), ' ')

  def parseMenu(self):
    """
    Parses an HTML source.
    """
    soup = BeautifulSoup(self.sourceText,
                         markupMassage = MenuParser.SOURCE_FIXES,
                         convertEntities = BeautifulStoneSoup.HTML_ENTITIES)

    menu = {}

    # The code here is not very smart or efficient, but we are trying
    # to be as much error-proof as possible.
    # Using the main meal and reading the other entries using it as a
    # reference point seems to be the best take.
    mainMeal = soup.find(text = re.compile(r"prato\s+principal", re.IGNORECASE)).parent.parent
    menu['principal'] = self.getTagText(mainMeal)

    # The date is usually the entry right before the main meal
    mealDate = mainMeal.findPreviousSibling('p')
    menu['data'] = self.getTagText(mealDate)

    # The three remaining entries (dessert, salad and juice) are the 3 next siblings
    for item in mainMeal.findNextSiblings('p', limit=3):
      match = re.match(r'([\w\s]+):\s*(.+)', self.getTagText(item))

      if match:
        menu[match.group(1).lower()] = match.group(2)

    # In the end, we shall have a dictionary with the following keys:
    # 'data', 'principal', 'salada', 'sobremesa', 'suco'
    if len(menu) != 5:
      raise ValueError, "The menu in the site has an invalid format"

    return Menu(menu)

if __name__ == "__main__":
  app = MenuParser()

  menu = app.parseMenu()
  menu.printMenu()
  menu.printSMSMenu()
