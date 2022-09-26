from __future__ import unicode_literals
from operator import index
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import configparser
import random

state = False #狀態

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))


# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)    
    try:
        #print(body, signature)
        handler.handle(body, signature)        
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def pretty_echo(event):
    global state

    def Input():
        return event.message.text

    def Chose():
        A,B,N = map(int,Input().split())
        lst = []
        for i in range(A, B+1):
            lst.append(i)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str(random.choices(lst, k=N))))

    Help = 'U1無聊做的，有bug為常態\n\n功能\n!!!打的數字一律用空白隔開!!!\n1."抽",輸入座號幾到幾，抽幾個人\n(1 22 3)1~22抽三個\n2."分"輸入全班人數,女生第一位座號,沒來的座號,全到請打0\n(22 10 1 20)全班22人，女生第一位為10號，1、22號沒來\n(22 10 0)全班22人，女生第一位為10號，全到'
    def Team():
        lst = list(map(int,Input().split()))
        person = []
        for i in range(1, lst[0] + 1):
            person.append(i)
        del lst[0]
        G = lst.pop(0)
        for i in lst:
            if(i in person):
                person.remove(i)
        while(G not in person): #怕分界沒來
            G += 1
        p = person.index(G)
        Blst,Glst = person[:p],person[p:]
        random.shuffle(Blst)
        random.shuffle(Glst)
        Bp = len(Blst)// 2
        Gp = len(Glst)// 2
        team1 = sorted(Blst[:Bp] + Glst[Gp:])
        team2 = sorted(Blst[Bp:] + Glst[:Gp])
        output = '[team1]\n' + str(team1) + '\n' + '[team2]\n' + str(team2)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=output))

    print(state)    
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef": 
        if(state == False):#沒指令
            if(Input() == '抽'):
                state = '抽'
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='幾到幾,幾個(X X X)'))
                return     
            elif(Input() == '分'):
                state = '分'
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='全班共幾人,女生第一號,沒來的座號(X X X)'))
                return
            elif(Input() == '?'):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=Help))
                return
            else:
                pretty_note = '♫♪♬'
                pretty_text = ''
                for i in Input:
                    pretty_text += i
                    pretty_text += random.choice(pretty_note)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=pretty_text))
                return
        else:
            if(state == '抽'):
                Chose()
            elif(state == '分'):
                Team()
            state = False
    print(state)

if __name__ == "__main__":
    app.run()
