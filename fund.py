#!/usr/bin/python 
# -*- coding:utf-8 -*-

import urllib 
import urllib2
import time
import os
import sys
import json
import logging
import logging.config
import ConfigParser
import optparse
import re

# API_URL
fund_api_url = "https://fundmobapi.eastmoney.com/FundMApi/FundVarietieValuationDetail.ashx"
stock_api_url = "http://hq.sinajs.cn/list=s_{0}"

# 控制字符
CLEAR_SCREEN = "\x1B[2J\x1B[3J\x1B[H"
RED = "\x1B[31m"
GREEN = "\x1B[32m"
RESET = "\x1B[0m"
MAGENTA = "\x1B[35m"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"

def get(url, data):
    var_list = []
    for k in data.keys():
        var_list.append(k + "=" + str(data[k]))
    url += "?" + "&".join(var_list)
    response = urllib2.urlopen(url)
    return response.read()

def get_fund(fund_id):
    data = {
        "FCODE" : fund_id,
        "deviceid" : "wap",
        "plat" : "Wap",
        "product" : "EFund",
        "version" : "2.0.0"
    }
    return get(fund_api_url, data)

def get_stock(stock_id):
    response = urllib2.urlopen(stock_api_url.format(stock_id))
    return response.read()

def get_all_fund_data(fund_list):
    fund_data_list = []
    for fund_id in fund_list:
        fund_data_list.append(get_fund(fund_id))
    return fund_data_list

def process_all_fund_data(fund_data_list):
    fund_dict_list = []
    desc_dict = {
        "name" : u"基金名称".encode('gb18030'),
        "dwjz" : u"单位价值".encode('gb18030'),
        "gz" : u"估值".encode('gb18030'),
        "gszzl" : u"估算涨幅".encode('gb18030'),
        "gztime" : u"更新时间".encode('gb18030')
    }

    fund_dict_list.append(desc_dict)

    for fund_data in fund_data_list:
        fund_data = json.loads(fund_data)

        fund_dict = {}
        fund_dict["name"] = fund_data["Expansion"]["SHORTNAME"].encode('gb18030')
        fund_dict["gz"] = fund_data["Expansion"]["GZ"].encode('gb18030')
        fund_dict["dwjz"] = fund_data["Expansion"]["DWJZ"].encode('gb18030')
        fund_dict["gszzl"] = fund_data["Expansion"]["GSZZL"].encode('gb18030')
        fund_dict["gztime"] = fund_data["Expansion"]["GZTIME"].encode('gb18030')

        fund_dict_list.append(fund_dict)
    return fund_dict_list

def print_all_fund_data(fund_dict_list):
    name_max_len = max([len(f["name"]) for f in fund_dict_list])
    gz_max_len = max([len(f["gz"]) for f in fund_dict_list])
    dwjz_max_len = max([len(f["dwjz"]) for f in fund_dict_list])
    gszzl_max_len = max([len(f["gszzl"]) for f in fund_dict_list])
    gztime_max_len = max([len(f["gztime"]) for f in fund_dict_list])

    print("_" * (name_max_len + gz_max_len + dwjz_max_len + gszzl_max_len + gztime_max_len + 15))

    for fund_dict in fund_dict_list:
        line = b"|" + fund_dict["name"].ljust(name_max_len) + \
        b" | " + fund_dict["dwjz"].ljust(dwjz_max_len) + \
        b" | " + fund_dict["gz"].ljust(gz_max_len) + b" | "
        
        if fund_dict["gszzl"].decode('gb18030') != u"估算涨幅":
            if float(fund_dict["gszzl"]) > 0:
                line += RED + fund_dict["gszzl"].ljust(gszzl_max_len) + RESET
            elif float(fund_dict["gszzl"]) < 0:
                line += GREEN + fund_dict["gszzl"].ljust(gszzl_max_len) + RESET
            else:
                line += fund_dict["gszzl"].ljust(gszzl_max_len)
        else:
            line += fund_dict["gszzl"].ljust(gszzl_max_len)

        line += b" | " + fund_dict["gztime"].ljust(gztime_max_len) + b" | "

        print line.decode('gb18030')

def get_all_stock_data(stock_id_list):
    stock_data_list = []
    for stock_id in stock_id_list:
        stock_data_list.append(get_stock(stock_id).decode("gbk"))
    return stock_data_list

def process_all_stock_data(stock_data_list):
    stock_dict_list = []
    desc_dict = {
        "name" : u"指数名称".encode('gb18030'),
        "index" : u"指数".encode('gb18030'),
        "change" : u"涨跌额".encode('gb18030'),
        "rate" : u"涨跌幅".encode('gb18030')
    }
    stock_dict_list.append(desc_dict)

    for stock_data in stock_data_list:
        stock_list = re.search(r"=\"(\S*)\"", stock_data).group(1).split(",")

        stock_dict = {}
        stock_dict["name"] = stock_list[0].encode('gb18030')
        stock_dict["index"] = stock_list[1].encode('gb18030')
        stock_dict["change"] = stock_list[2].encode('gb18030')
        stock_dict["rate"] = stock_list[3].encode('gb18030')
        stock_dict_list.append(stock_dict)
    return stock_dict_list

def print_all_stock_data(stock_dict_list):
    name_max_len = max([len(f["name"]) for f in stock_dict_list])
    index_max_len = max([len(f["index"]) for f in stock_dict_list])
    change_max_len = max([len(f["change"]) for f in stock_dict_list])
    rate_max_len = max([len(f["rate"]) for f in stock_dict_list])

    print("_" * (name_max_len + index_max_len + change_max_len + rate_max_len + 21))

    for stock_dict in stock_dict_list:
        line = b"|" + stock_dict["name"].ljust(name_max_len) + \
        b" | " + stock_dict["index"].ljust(index_max_len) + \
        b" | " + stock_dict["change"].ljust(change_max_len) + b" | "

        if stock_dict["rate"].decode('gb18030') != u"涨跌幅":
            if float(stock_dict["rate"]) > 0:
                line += RED + stock_dict["rate"].ljust(rate_max_len) + RESET
            elif float(stock_dict["rate"]) < 0:
                line += GREEN + stock_dict["rate"].ljust(rate_max_len) + RESET
            else:
                line += stock_dict["rate"].ljust(rate_max_len)
        else:
            line += stock_dict["rate"].ljust(rate_max_len)

        line += b" | " + stock_dict["rate"].ljust(rate_max_len) + b" |"
        print line.decode('gb18030')

def main():
    parser = optparse.OptionParser()
    parser.add_option("-d", "--delay", dest="delay", default=60)
    (options, args) = parser.parse_args()

    cf = ConfigParser.ConfigParser()
    cf.read("./fund.conf")
    fund_id_list = cf.options("fund")
    stock_id_list = cf.options("stock")

    print HIDE_CURSOR,
    last_tick_time = 0

    while 1:
        now = time.time()
        if now> last_tick_time + int(options.delay):
            stock_data_list = get_all_stock_data(stock_id_list)
            stock_dict_list = process_all_stock_data(stock_data_list)

            fund_data_list = get_all_fund_data(fund_id_list)
            fund_dict_list = process_all_fund_data(fund_data_list)

            rows, columns = os.popen('stty size', 'r').read().split()

            print CLEAR_SCREEN,
            print(MAGENTA + time.strftime("%Y-%m-%d %H:%M:%S").center(int(columns)) + RESET)
            print_all_stock_data(stock_dict_list)
            print
            print_all_fund_data(fund_dict_list)

            last_tick_time = now
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except:
        print SHOW_CURSOR
