#!/usr/bin/env python

from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from xml.sax.saxutils import unescape
import urllib
import re

SOURCE_FIXES = [
  # <td background-color: "#ededed;"> becomes <td>
  (re.compile(r'\s*[-\w]+:\s*"[a-zA-Z0-9#;]+"'), lambda s: ''),
]
SOURCE_URL = "http://www.prefeitura.unicamp.br/servicos.php?servID=119"

def main():
  soup = BeautifulSoup(urllib.urlopen(SOURCE_URL),
                       markupMassage = SOURCE_FIXES,
                       convertEntities = BeautifulStoneSoup.HTML_ENTITIES)

  menuBlock  = soup.findAll('p', style="text-align: left")
  menuKeys   = ('data', 'principal', 'sobremesa', 'salada', 'suco')
  menuValues = []

  for line in menuBlock:
    strLine = ''.join(line.findAll(text=True)).replace(unichr(160), ' ')
    match   = re.match(r'[\w\s]+:\s*(.+)', strLine)

    if match:
      menuValues.append(match.group(1))

  if len(menuValues) != 5:
    raise ValueError, "There are not 5 items in the menu!"

  menu = dict(zip(menuKeys, menuValues))
  print menu

if __name__ == "__main__":
  main()
