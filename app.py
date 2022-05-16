from __future__ import unicode_literals

import time
from flask import Flask, request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import json
import configparser
import os
from urllib import parse
from linebot.models import (
  RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds,
  URIAction, PostbackAction
)

from datetime import datetime
# import pymysql
import sqlite3


app = Flask(__name__, static_url_path='/static')
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])


config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))
my_line_id = config.get('line-bot', 'my_line_id')
end_point = config.get('line-bot', 'end_point')
line_login_id = config.get('line-bot', 'line_login_id')
line_login_secret = config.get('line-bot', 'line_login_secret')
my_phone = config.get('line-bot', 'my_phone')
HEADER = {
    'Content-type': 'application/json',
    'Authorization': F'Bearer {config.get("line-bot", "channel_access_token")}'
}


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return 'ok'
    body = request.json
    events = body["events"]
    print(body)
    if "replyToken" in events[0]:
        payload = dict()
        replyToken = events[0]["replyToken"]
        payload["replyToken"] = replyToken
        if events[0]["type"] == "message":
            if events[0]["message"]["type"] == "text":
                text = events[0]["message"]["text"]

                if text == "尋找":
                    payload["messages"] = [region()]

                elif text == "GPS":
                    payload["messages"] = [{
                        "type": "template",
                        "altText": "打卡",
                        "template": {
                            "type": "buttons",
                            "text": "請選擇地點",
                            "actions": [
                                {
                                    "type": "location",
                                    "label": "Location"
                                }
                            ]
                        }
                    }]
                else:
                    p = []
                    if len(keyword_search(text)) > 0:
                        for i in keyword_search(text):
                            loc = {"type": "bubble", "body": {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                                {"type": "image", "url": "https://freedesignfile.com/upload/2019/07/ATM-vector.jpg"},
                                                {"type": "text", "text": f"{i[0]}"},
                                                {"type": "text", "text": f"{i[1]}", "adjustMode": "shrink-to-fit"},
                                                {"type": "separator", "color": "#000000"},
                                                {"type": "button", "action": {"type": "uri", "label": "帶我去", "uri": "https://www.google.com/maps/search/"+parse.quote_plus(f"{i[1]}")}, "style": "link", "color": "#00dd00"}
                                            ]
                                        }
                                   }

                            p.append(loc)

                        payload["messages"] = [{
                            "type": "flex",
                            "altText": "this is a flex message",
                            "contents": {
                                "type": "carousel",
                                "contents": p
                            }
                        }]
                    else:
                        payload["messages"] = [{
                            "type": "text",
                            "text": "查無資料"
                        }]

                replyMessage(payload)

            elif events[0]["message"]["type"] == "location":
                latitude = events[0]["message"]["latitude"]
                longitude = events[0]["message"]["longitude"]
                r = 0.0005

                for t in range(1, 10):
                    a = GPS_Search(latitude, longitude, r)
                    if len(a) > 0:
                        break
                    r = r * 2
                s = ""
                n = "\n"
                for l in a:
                    g = l[0]
                    s += g+n
                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{s}"
                                      }]
                replyMessage(payload)

        elif events[0]["type"] == "postback":
            if 'region' in events[0]["postback"]["data"]:
                if events[0]["postback"]["data"] == 'region=north':
                    payload["messages"] = [north()]
                    replyMessage(payload)
                elif events[0]["postback"]["data"] == 'region=central':
                    payload["messages"] = [central()]
                    replyMessage(payload)
                elif events[0]["postback"]["data"] == 'region=south':
                    payload["messages"] = [south()]
                    replyMessage(payload)
                elif events[0]["postback"]["data"] == 'region=east':
                    payload["messages"] = [east()]
                    replyMessage(payload)
                elif events[0]["postback"]["data"] == 'region=island':
                    payload["messages"] = [island()]
                    replyMessage(payload)
                    
            elif events[0]["postback"]["data"] == 'menu3':
                payload["messages"] = [region()]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '台北市':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '新北市':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '桃園市':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '新竹市':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '基隆市':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '宜蘭縣':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '新竹縣':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '苗栗縣':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '台中市':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '彰化縣':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '雲林縣':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '南投縣':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '嘉義縣':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '嘉義市':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '台南市':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '高雄市':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '屏東縣':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '花蓮縣':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '台東縣':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '連江縣':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '金門縣':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

            elif events[0]["postback"]["data"] == '澎湖縣':
                x = events[0]["postback"]["data"]
                a = AtmSearch(x)[0][0]

                payload["messages"] = [{
                                        "type": "text",
                                        "text": f"{a}"
                                      }]
                replyMessage(payload)

    return 'OK'


def getPlayStickerMessage():  # 標示打卡成功用的
    message = dict()
    message["type"] = "sticker"
    message["packageId"] = "6325"
    message["stickerId"] = "10979904"
    return message


def replyMessage(payload):
    response = requests.post("https://api.line.me/v2/bot/message/reply", headers=HEADER, data=json.dumps(payload))
    return 'OK'


def pushMessage(payload):
    response = requests.post("https://api.line.me/v2/bot/message/push", headers=HEADER, data=json.dumps(payload))
    return 'OK'


def region():
    message = {
        "type": "flex",
        "altText": "this is a flex message",
        "contents": {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "horizontal",
                "justifyContent": "center",
                "contents": [
                    {
                        "type": "text",
                        "text": "查詢",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#FFFFFFFF",
                        "align": "center",
                        "contents": []
                    },
                ]
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "backgroundColor": "#D6F2EDFF",
                "contents": [{
                    "type": "box",
                    "layout": "vertical",
                    "flex": 1,
                    "contents": [
                        {"type": "button",
                         "action": {
                             "type": "postback",
                             "label": "北區",
                             "data": "region=north"
                         }
                         },
                        {"type": "button",
                         "action": {
                             "type": "postback",
                             "label": "中區",
                             "data": "region=central"
                         }
                         }
                    ]
                },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "flex": 2,
                        "contents": [
                            {"type": "button",
                             "action": {
                                 "type": "postback",
                                 "label": "南區",
                                 "data": "region=south"
                             }
                             },
                            {"type": "button",
                             "action": {
                                 "type": "postback",
                                 "label": "東區",
                                 "data": "region=east"
                             }
                             },
                            {"type": "button",
                             "action": {
                                 "type": "postback",
                                 "label": "外島",
                                 "data": "region=island"
                             }
                             }
                        ]
                    }
                ]
            },
            "styles": {
                "header": {
                    "backgroundColor": "#67C9D4FF",
                }

            }
        }
    }
    return message


def north():
    message = {
                "type": "flex",
                "altText": "this is a flex message",
                "contents": {
                                "type": "bubble",
                                "header": {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "justifyContent": "center",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "查詢",
                                            "weight": "bold",
                                            "size": "xl",
                                            "color": "#FFFFFFFF",
                                            "align": "center",
                                            "contents": []
                                        },
                                    ]
                                },
                                "footer": {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "backgroundColor": "#D6F2EDFF",
                                    "contents": [{
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "flex": 1,
                                                    "contents": [
                                                                 {"type": "button",
                                                                  "action": {
                                                                             "type": "postback",
                                                                             "label": "台北市",
                                                                             "data": "台北市"
                                                                            }
                                                                 },
                                                                 {"type": "button",
                                                                  "action": {
                                                                             "type": "postback",
                                                                             "label": "新北市",
                                                                             "data": "新北市"
                                                                            }
                                                                  },
                                                                 {"type": "button",
                                                                  "action": {
                                                                             "type": "postback",
                                                                             "label": "桃園市",
                                                                             "data": "桃園市"
                                                                            }
                                                                  },
                                                                 {"type": "button",
                                                                  "action": {
                                                                     "type": "postback",
                                                                     "label": "新竹市",
                                                                     "data": "新竹市"
                                                                            }
                                                                  }
                                                                ]
                                                 },
                                                 {
                                                    "type": "box",
                                                    "layout": "vertical",
                                                    "flex": 2,
                                                    "contents": [
                                                                 {"type": "button",
                                                                  "action": {
                                                                              "type": "postback",
                                                                              "label": "基隆市",
                                                                              "data": "基隆市"
                                                                            }
                                                                  },
                                                                 {"type": "button",
                                                                  "action": {
                                                                              "type": "postback",
                                                                              "label": "宜蘭縣",
                                                                              "data": "宜蘭縣"
                                                                            }
                                                                  },
                                                                 {"type": "button",
                                                                  "action": {
                                                                              "type": "postback",
                                                                              "label": "新竹縣",
                                                                              "data": "新竹縣"
                                                                            }
                                                                  },
                                                                 {"type": "button",
                                                                  "action": {
                                                                              "type": "postback",
                                                                              "label": "區域列表",
                                                                              "data": "menu3"
                                                                            }
                                                                  }
                                                                ]
                                                 }
                                                ]
                                            },
                                            "styles": {
                                                "header": {
                                                          "backgroundColor": "#67C9D4FF",
                                                            }

                                            }
                            }
            }
    return message


def central():
    message = {
                "type": "flex",
                "altText": "this is a flex message",
                "contents": {
                    "type": "bubble",
                    "header": {
                        "type": "box",
                        "layout": "horizontal",
                        "justifyContent": "center",
                        "contents": [
                            {
                                "type": "text",
                                "text": "查詢",
                                "weight": "bold",
                                "size": "xl",
                                "color": "#FFFFFFFF",
                                "align": "center",
                                "contents": []
                            },
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "horizontal",
                        "backgroundColor": "#D6F2EDFF",
                        "contents": [{
                            "type": "box",
                            "layout": "vertical",
                            "flex": 1,
                            "contents": [
                                {"type": "button",
                                 "action": {
                                     "type": "postback",
                                     "label": "苗栗縣",
                                     "data": "苗栗縣"
                                 }
                                 },
                                {"type": "button",
                                 "action": {
                                     "type": "postback",
                                     "label": "台中市",
                                     "data": "台中市"
                                 }
                                 },
                                {"type": "button",
                                 "action": {
                                     "type": "postback",
                                     "label": "彰化縣",
                                     "data": "彰化縣"
                                 }
                                 }

                            ]
                        },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "flex": 2,
                                "contents": [
                                    {"type": "button",
                                     "action": {
                                         "type": "postback",
                                         "label": "雲林縣",
                                         "data": "雲林縣"
                                     }
                                     },
                                    {"type": "button",
                                     "action": {
                                         "type": "postback",
                                         "label": "南投縣",
                                         "data": "南投縣"
                                     }
                                     },
                                    {"type": "button",
                                     "action": {
                                         "type": "postback",
                                         "label": "區域列表",
                                         "data": "menu3"
                                     }
                                     }
                                ]
                            }
                        ]
                    },
                    "styles": {
                        "header": {
                            "backgroundColor": "#67C9D4FF",
                        }

                    }
                }
            }
    return message


def south():
    message = {
                "type": "flex",
                "altText": "this is a flex message",
                "contents": {
                                "type": "bubble",
                                "header": {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "justifyContent": "center",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "人流查詢",
                                            "weight": "bold",
                                            "size": "xl",
                                            "color": "#FFFFFFFF",
                                            "align": "center",
                                            "contents": []
                                        },
                                    ]
                                },
                                "footer": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "backgroundColor": "#D6F2EDFF",
                                    "contents": [
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "postback",
                                                                 "label": "嘉義縣",
                                                                 "data": "嘉義縣"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "postback",
                                                                 "label": "嘉義市",
                                                                 "data": "嘉義市"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "postback",
                                                                 "label": "台南市",
                                                                 "data": "台南市"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "postback",
                                                                 "label": "高雄市",
                                                                 "data": "高雄市"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "postback",
                                                                 "label": "屏東縣",
                                                                 "data": "屏東縣"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "postback",
                                                                 "label": "區域列表",
                                                                 "data": "menu3"
                                                               }
                                                    }
                                                 ]
                                            },
                                            "styles": {
                                                "header": {
                                                          "backgroundColor": "#67C9D4FF",
                                                            }

                                                          }
                            }
            }
    return message


def east():
    message = {
                "type": "flex",
                "altText": "this is a flex message",
                "contents": {
                                "type": "bubble",
                                "header": {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "justifyContent": "center",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "人流查詢",
                                            "weight": "bold",
                                            "size": "xl",
                                            "color": "#FFFFFFFF",
                                            "align": "center",
                                            "contents": []
                                        },
                                    ]
                                },
                                "footer": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "backgroundColor": "#D6F2EDFF",
                                    "contents": [
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "postback",
                                                                 "label": "花蓮縣",
                                                                 "data": "花蓮縣"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                         "type": "postback",
                                                         "label": "台東縣",
                                                         "data": "台東縣"
                                                     }
                                                     },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "postback",
                                                                 "label": "區域列表",
                                                                 "data": "menu3"
                                                               }
                                                    }
                                                 ]
                                            },
                                            "styles": {
                                                "header": {
                                                          "backgroundColor": "#67C9D4FF",
                                                            }

                                                          }
                            }
            }
    return message


def island():
    message = {
                "type": "flex",
                "altText": "this is a flex message",
                "contents": {
                                "type": "bubble",
                                "header": {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "justifyContent": "center",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "人流查詢",
                                            "weight": "bold",
                                            "size": "xl",
                                            "color": "#FFFFFFFF",
                                            "align": "center",
                                            "contents": []
                                        },
                                    ]
                                },
                                "footer": {
                                    "type": "box",
                                    "layout": "vertical",
                                    "backgroundColor": "#D6F2EDFF",
                                    "contents": [
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "postback",
                                                                 "label": "連江縣",
                                                                 "data": "連江縣"
                                                               }
                                                    },
                                                    {"type": "button",
                                                     "action": {
                                                         "type": "postback",
                                                         "label": "金門縣",
                                                         "data": "金門縣"
                                                     }
                                                     },
                                                    {"type": "button",
                                                     "action": {
                                                         "type": "postback",
                                                         "label": "澎湖縣",
                                                         "data": "澎湖縣"
                                                     }
                                                     },
                                                    {"type": "button",
                                                     "action": {
                                                                 "type": "postback",
                                                                 "label": "區域列表",
                                                                 "data": "menu3"
                                                               }
                                                    }
                                                 ]
                                            },
                                            "styles": {
                                                "header": {
                                                          "backgroundColor": "#67C9D4FF",
                                                            }

                                                          }
                            }
            }
    return message


def AtmSearch(x):
    con = sqlite3.connect('taiwan_atm.sqlite')

    cursor = con.cursor()

    sql = f"""select atm_address 
              from atm 
              where atm_address like '%{x}%'
              limit 1;
                """
    cursor.execute(sql)
    result = cursor.fetchall()
    con.commit()
    cursor.close()
    con.close()

    return result


def GPS_Search(x, y, r=0.0005):
    connection = sqlite3.connect('taiwan_atm.sqlite')

    cursor = connection.cursor()

    sql = f"""select atm_address from atm 
              where abs(lat-{x})<{r} and abs(lng-{y})<{r}
              order by abs(lat-{x})+abs(lng-{y})
              limit 10;
            """
    cursor.execute(sql)
    result = cursor.fetchall()
    connection.commit()
    cursor.close()
    connection.close()

    return result


def keyword_search(x):
    connection = sqlite3.connect('taiwan_atm.sqlite')

    cursor = connection.cursor()

    sql = f"""select atm_location, atm_address from atm 
              where atm_location LIKE '%{x}%' OR atm_address LIKE '%{x}%'
              limit 10;
            """
    cursor.execute(sql)
    result = cursor.fetchall()
    connection.commit()
    cursor.close()
    connection.close()

    return result


def map_search(x):
    connection = sqlite3.connect('taiwan_atm.sqlite')

    cursor = connection.cursor()

    sql = f"""select atm_address , lat, lng from atm 
              where atm_location LIKE '%{x}%' OR atm_address LIKE '%{x}%'
              limit 10;
            """
    cursor.execute(sql)
    result = cursor.fetchall()
    connection.commit()
    cursor.close()
    connection.close()

    return result


if __name__ == "__main__":
    app.debug = True
    app.run()
