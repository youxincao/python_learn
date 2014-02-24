# -*- coding: utf-8 -*-
import urllib
import urllib2
import cookielib
import re
from test.test_iterlen import len
# 登录地址
tbLoginUrl = "https://login.taobao.com/member/login.jhtml"
shoppingurl = "http://item.taobao.com/item.htm?id=37373807880&spm=a310v.4.88.1"
checkCodeUrl = ''
# post请求头部
headers = {
    'x-requestted-with': 'XMLHttpRequest',
    'Accept-Language': 'zh-cn',
    'Accept-Encoding': 'gzip, deflate',
    'ContentType': 'application/x-www-form-urlencoded; chartset=UTF-8',
    'Host':    'login.taobao.com',
    'DNT': 1,
    'Cache-Control': 'no-cache',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1',
    'Referer' : 'https://login.taobao.com/member/login.jhtml?redirectURL=http%3A%2F%2Fwww.taobao.com%2F',
    'Connection' : 'Keep-Alive'
}
# 用户名，密码
username = "you_xin_cao"
password = raw_input("Please input your password of taobao: ")
# 请求数据包
postData = {   
    'TPL_username':username,
    'TPL_password':password,
    "need_check_code" : "false",
    "loginsite": 0,
    "newlogin":1,
    'TPL_redirect_url':'',
    'from':'tbTop',
    'fc':"default",
    'style':'default',
    'css_style':'',
    'tid':'',
    'support':'000001',
    'CtrlVersion':'1,0,0,7',
    'loginType':3,
    'minititle':'',
    'minipara' :'',
    "umto":"NAN",
    'pstrong':2,
    'llnick':'',
    'sign':'',
    'need_sign':'',
    "isIgnore":'',
    "full_redirect":'',
    'popid':'',
    'callback':'1',
    'guf':'',
    'not_duplite_str':'',
    'need_user_id':'',
    'poy':'',
    'gvfdcname':10,
    'from_encoding':'',
    "sub":'',
    "allp":'',
    'action':'Authenticator',
    'event_submit_do_login':'anything',
    'longLogin':0               
}

buy_now_data = {
    'tb_token' : '' ,
    'item_url_refer' : '' ,
    'item_id' : '' ,
    'item_id_num' : '' ,
    'auction_type' : '' ,
    'from' : '' ,
    'frm'  : '' ,
    'current_price' : '' ,
    'activity' : '' ,
    'auto_post1' : '' ,
    'quantity' : '' ,
    'skuId' : '',
    'skuInfo' : '' ,
    'buyer_from' : '' ,
    'chargeTypeId' : '' 
};
# 登录主函数
def loginToTaobao():
    # cookie 自动处理器
    global checkCodeUrl
    cookiejar = cookielib.LWPCookieJar()  # LWPCookieJar提供可读写操作的cookie文件,存储cookie对象
    cookieSupport = urllib2.HTTPCookieProcessor(cookiejar)
    opener = urllib2.build_opener(cookieSupport, urllib2.HTTPHandler)
    urllib2.install_opener(opener)
    # 打开登陆页面
    taobao = urllib2.urlopen(tbLoginUrl)
    resp = taobao.read().decode("gbk")
    # 提取验证码地址
    pattern = r'img id="J_StandardCode_m" src="https://s.tbcdn.cn/apps/login/static/img/blank.gif" data-src="(\S*)"'
    checkCodeUrlList = re.findall(pattern, resp)
    checkCodeUrl = checkCodeUrlList[0]
    print "checkCodeUrl:", checkCodeUrl
    # 此时直接发送post数据包登录
    sendPostData(tbLoginUrl, postData, headers)
    if checkCodeUrl != "":
        getCheckCode(checkCodeUrl)
    sendPostData(tbLoginUrl, postData, headers)
     
def sendPostData(url, data, header):
    print "+"*20 + "sendPostData" + "+"*20
    data = urllib.urlencode(data)      
    request = urllib2.Request(url, data, header)
    response = urllib2.urlopen(request)
    # url = response.geturl()
    text = response.read().decode("gbk")
    info = response.info()
    status = response.getcode()
    response.close()
    print status
    print info
    print "Response:", text
    result = handleResponseText(text)
    if result["state"]:
        print "successfully login in!"
    else:
        print "failed to login in, error message: ", result["message"]
 
def handleResponseText(text):
    """处理登录返回结果"""
    global checkCodeUrl
     
    print "+"*20 + "handleResponseText" + "+"*20  
    text = text.replace(',', ' ')   
    responseData = {"state": False,
                    "message" : "",
                    "code" : ""}
     
    m1 = re.match(r'\{?"state":(\w*)\ ', text)
    if m1 is not None:
        s = m1.group(1)
        if s == "true":
            responseData["state"] = True
        else:
            m2 = re.search(r'"message":"(\S*)"( |})', text)
            if m2 is not None:
                msg = m2.group(1)
                responseData["message"] = msg.decode("utf-8")   
            else:
                print "failed to get the error message"
            m3 = re.match(r'.+\"code":(\w*)\ ', text)
            if m3 is not None:
                code = m3.group(1)
                responseData["code"] = code
#                 if code == "1000":                 
#                     getCheckCode(checkCodeUrl)
            else:
                print "failed to get the error code"
    return responseData
 
def getCheckCode(url):
    print "+"*20 + "getCheckCode" + "+"*20
    response = urllib2.urlopen(url)
    status = response.getcode()
    picData = response.read()
     
    path = "D:\\checkcode.jpeg"
    if status == 200:
        localPic = open(path, "wb")
        localPic.write(picData)
        localPic.close() 
        print "请到%s,打开验证码图片" % path  
        checkCode = raw_input("请输入验证码：")
        print checkCode, type(checkCode)
        postData["TPL_checkcode"] = checkCode
        postData["need_check_code"] = "true"
    else:
        print "failed to get Check Code, status: ", status
        
def resetCheckCode():
    postData["need_check_code"] = "false"
    del postData["TPL_checkcode"]
    

# Get the shopping info from url 
def getShoppingInfo(url):
    content = urllib2.urlopen(url)
    shoppingMap = {}
    itemType = ''
    # print content 
    for line in content : 
        gbk_line = line.decode('gbk')
        m1 = re.match('.*<dt class="tb-property-type">(.*)</dt>', gbk_line) 
        if m1 :
            itemType = m1.group(1)
            shoppingMap[itemType] = {} 
        m1 = re.match('.*<li data-value=\"([0-9:]*)\".*', gbk_line)
        if m1 :
            # print  gbk_line 
            value = m1.group(1)
            title = ''
            if re.search("<a href=", gbk_line):
                match_title = re.match('.*<span>(.*)</span>.*', gbk_line)
                title = match_title.group(1) 
                shoppingMap[itemType][title] = value
            elif re.search("title=", gbk_line) :
                match_title = re.match('.*title=\"(.*)\" class=', gbk_line) 
                title = match_title.group(1)
                shoppingMap[itemType][title] = value
            else :
                return None
    for key in shoppingMap.keys() : 
        print "Type :" , key  
        for title in shoppingMap[key]:
            print "=== title  : " , title , " value : "  , shoppingMap[key][title] 
     
    return shoppingMap

def getSkuMap(url):
    content = urllib2.urlopen(url)
    
    token = "None"
    brace_level = 0 
    skuMap = [] 
    parseStock = False
    
    for line in content : 
        gbk_line = line.decode('gbk')
               
        m1 = re.search('"skuMap":', gbk_line)
        if m1 :
            token = "skuMap"
            brace_level = brace_level + 1 
            continue       
        if token == "skuMap" :
            # print brace_level , " " , gbk_line
            if brace_level == 2 : 
                m1 = re.match('.*";(.*);".*', gbk_line)
                if m1 :
                    #  We find a skumap 
                    # add a map to it 
                    skuMap.append({})
                    skuMap[len(skuMap) - 1]["index"] = m1.group(1)
                    # print len(skuMap) , " " , m1.group(1)
            
            if brace_level == 3 : 
                m1 = re.match('.*"skuId" : "([0-9]*)".*', gbk_line)
                if m1 :
                    skuMap[len(skuMap) - 1]["skuId"] = m1.group(1)
                    continue
                m1 = re.match('.*"price" : "([0-9\.]*)".*', gbk_line)
                if m1 :
                    skuMap[len(skuMap) - 1]["price"] = m1.group(1)
                    continue
                
                m1 = re.search('stock', gbk_line)
                if m1 : 
                    parseStock = True 
                    continue 
                
                if parseStock : 
                    m1 = re.match('.*"([0-9]*)".*', gbk_line)
                    if m1 :
                        skuMap[len(skuMap) - 1]["stock"] = m1.group(1)
                        parseStock = False             
                    
            if re.match(".*{.*" , gbk_line) : 
                brace_level = brace_level + 1
            if re.match(".*}.*" , gbk_line) : 
                brace_level = brace_level - 1 
            if brace_level == 0 : 
                token = "None"
    
    return skuMap

def inputValidNumber(msg , minVal , maxVal):
    number = -1
    
    # check the parameter 
    if minVal >= maxVal :
        return number
    while True :
        
        # first make sure we get a number 
        try :
            number = int(raw_input(msg))
        except ValueError : 
            print "The input is not a number "
            continue 
        
        # second make sure the number is valid 
        else :
            if number >= minVal and number < maxVal : 
                break 
        
    return number

def chooseShoppingItem(shoppingItems) :
    valuelist = [] 
    for key in shoppingItems.keys() : 
        print "Choose : " , key 
        for index , title in enumerate(shoppingItems[key].keys()):
            print index , " : " , title 
            
        # make sure a valid choice 
        index = inputValidNumber("Input the index : " , 0 , len(shoppingItems[key].keys()))  
        # get the title 
        if index != -1 :
            title = shoppingItems[key].keys()[index]
            print "You choose " , title 
            valuelist.append(shoppingItems[key][title])
    
    return valuelist 

def getChooseSku(valuelist , skuMap):  
    for sku in skuMap:
        found = True 
        for value in valuelist : 
            if not  re.search(value , sku["index"]) : 
                found = False 
                break 
        if found :
            return sku 
    return None 
          
if __name__ == "__main__":   
#     loginToTaobao()
#     resetCheckCode()
    shoppingItems = getShoppingInfo(shoppingurl)
    skumap = getSkuMap(shoppingurl)
    for item in skumap :
        print item 
    valueList = chooseShoppingItem(shoppingItems)
    for value in valueList :
        print value 
    
    chooseSkuItem = getChooseSku(valueList, skumap)
    print chooseSkuItem
