import sys
sys.path.insert(0, './solax')

import solax
import asyncio
import json
import os

from solax import inverter
from http.server import HTTPServer, BaseHTTPRequestHandler


async def LoadSolaxData():
    # r = await solax.real_time_api(os.environ['SOLAX_IP'],80,'admin')
    r = solax.RealTimeAPI(inverter.X1MiniV34(os.environ['SOLAX_IP'],80,'admin'))
    return await r.get_data()

def syncLoadData():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    responseTasks, timedout = loop.run_until_complete(
        asyncio.wait([LoadSolaxData()], timeout=30))
    response=None

    if(timedout):
        [task.cancel() for task in timedout]
        loop.run_until_complete(asyncio.wait(timedout))
    else:
        responseTask = responseTasks.pop()
        response=responseTask.result()

    return (response, timedout)
            


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    offline_message = '{ }'

    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(404)
            self.end_headers()
        elif self.path == "/raw_json":
            response, timedout = syncLoadData()

            print("timedout{}, response: {}".format(timedout,response))
            if(timedout):
                replyMessage='{ "DeviceIsOnline":0  }'
            else:    
                replyMessage = response.raw_json
            self.send_response(200)
            self.end_headers()
            self.wfile.write(replyMessage.encode('utf-8'))
        else:
            replyMessage = ""
            solaxIsOnline = False

            response, timedout = syncLoadData()
          
            if timedout:
                replyMessage = SimpleHTTPRequestHandler.offline_message
                solaxIsOnline = False
            else:
                replyMessage = json.dumps(response.data)
                SimpleHTTPRequestHandler.offline_message = replyMessage
                solaxIsOnline = True

            replyJson = json.loads(replyMessage)
            
            if solaxIsOnline is False:
                replyJson['DeviceIsOnline'] = 0
                replyJson["PV1 Current"] = 0
                replyJson["PV2 Current"] = 0
                replyJson["PV1 Voltage"] = 0
                replyJson["PV2 Voltage"] = 0
                replyJson["Output Current"] = 0
                replyJson["Network Voltage"] = 0
                replyJson["AC Power"] = 0
                replyJson["Inverter Temperature"] = 0
                replyJson["Exported Power"] = 0
                replyJson["PV1 Power"] = 0
                replyJson["PV2 Power"] = 0
                replyJson["Battery Voltage"] = 0
                replyJson["Battery Current"] = 0
                replyJson["Battery Power"] = 0
                replyJson["Battery Temperature"] = 0
                replyJson["Battery Remaining Capacity"] = 0
                replyJson["Power Now"] = 0
                replyJson["Grid Frequency"] = 0
                replyJson["EPS Voltage"] = 0
                replyJson["EPS Current"] = 0
                replyJson["EPS Power"] = 0
                replyJson["EPS Frequency"] = 0
                replyJson["Total Energy"] =  replyJson["Total Energy"] if "Total Energy" in replyJson else 0
                replyJson["Total Feed-in Energy"] = replyJson["Total Feed-in Energy"] if "Total Feed-in Energy" in replyJson else 0
                replyJson["Total Consumption"] = replyJson["Total Consumption"] if "Total Consumption" in replyJson else 0
                replyJson["Today's Energy"] = 0
            else:
                replyJson['DeviceIsOnline'] = 1
            replyMessage = json.dumps(replyJson, indent=4)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(replyMessage.encode('utf-8'))


print("Starting server on Port 8000, using Solax-IP " + os.environ['SOLAX_IP'] + "...")
httpd = HTTPServer(('', 8000), SimpleHTTPRequestHandler)
httpd.serve_forever()
