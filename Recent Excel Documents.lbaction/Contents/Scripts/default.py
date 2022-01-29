#!/usr/bin/env python3

import json, operator
import mruservice, mruuserdata

APP_NAME = 'Excel'
APP_BUNDLE_ID = 'com.microsoft.Excel'
APP_URL_PREFIX = 'ms-excel:ofe|u|'
EXTENSION_TO_ICON_NAME = dict(
    slk='XLS8', dif='XLS8', ods='ODS', xls='XLS8', xlsx='XLSX', xltx='XLTX', xlsm='XLSM',
    xltm='XLTM', xlsb='XLSB', xlam='XLAM', xlw='XLW8', xla='XLA8', xlb='XLB8', xlt='XLT',
    xld='XLD5', xlm='XLM4', xll='XLL', csv='CSV', txt='TEXT', xml='XMLS', tlb='OTLB', _='TEXT')

items = mruuserdata.items_for_app(APP_NAME)
items += mruservice.items_for_app(APP_NAME, APP_BUNDLE_ID, APP_URL_PREFIX, EXTENSION_TO_ICON_NAME)

items.sort(key=operator.itemgetter('Timestamp'), reverse=True)

print(json.dumps(items))
