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
    data_re = re.match(r'(?:(.+)\s*-\s*)?([\d]{1,2}/[\d]{1,2})(?:\d{2,4})*',
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
