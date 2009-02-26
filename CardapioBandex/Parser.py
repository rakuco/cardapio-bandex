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

import urllib2
import re
import Menu

class Parser(object):
  SOURCE_FIXES = [
    # <td background-color: "#ededed;"> becomes <td>
    (re.compile(r'\s*[-\w]+:\s*"[a-zA-Z0-9#;]+"'), lambda s: ''),
  ]
  SOURCE_URL = "http://www.prefeitura.unicamp.br/servicos.php?servID=119"

  def __init__(self, source = None):
    if source is None:
      self.sourceText = self.getSource().read()
    else:
      self.sourceText = source.read()

  def __getTagText(self, tag):
    """
    Receives a Tag object and returns its stripped text.
    """
    return ''.join(tag.findAll(text=True)).replace(unichr(160), ' ')

  def getSource(self):
    """
    Returns the HTML file that should be parsed.
    """
    return urllib2.urlopen(Parser.SOURCE_URL)

  def parseMenu(self):
    """
    Parses an HTML source.
    """
    soup = BeautifulSoup(self.sourceText,
                         markupMassage = Parser.SOURCE_FIXES,
                         convertEntities = BeautifulStoneSoup.HTML_ENTITIES)

    menu = {}

    # The code here is not very smart or efficient, but we are trying
    # to be as much error-proof as possible.
    # Using the main meal and reading the other entries using it as a
    # reference point seems to be the best take.
    mainMeal = soup.find(text = re.compile(r"prato\s+principal", re.IGNORECASE)).parent.parent
    menu['principal'] = self.__getTagText(mainMeal)

    # The date is usually the entry right before the main meal
    mealDate = mainMeal.findPreviousSibling('p')
    menu['data'] = self.__getTagText(mealDate)

    # The three remaining entries (dessert, salad and juice) are the 3 next siblings
    for item in mainMeal.findNextSiblings('p', limit=3):
      match = re.match(r'([\w\s]+):\s*(.+)', self.__getTagText(item))

      if match:
        menu[match.group(1).lower()] = match.group(2)

    # In the end, we shall have a dictionary with the following keys:
    # 'data', 'principal', 'salada', 'sobremesa', 'suco'
    if len(menu) != 5:
      raise ValueError, "The menu in the site has an invalid format"

    return Menu.Menu(menu)
