import solax
import asyncio
import json
import sys

from http.server import HTTPServer, BaseHTTPRequestHandler

async def LoadSolaxData():
    r = await solax.real_time_api('5.8.8.8')
    return await r.get_data()

offline_message = '{ "PV1 Current": 0, "PV2 Current": 0,"PV1 Voltage": 0,  "PV2 Voltage": 0,  "Output Current": 0,  "Network Voltage": 0,  "AC Power": 0,  "Inverter Temperature": 0,  "Today\'s Energy": 0,  "Total Energy": 0,  "Exported Power": 0,  "PV1 Power": 0,  "PV2 Power": 0,  "Battery Voltage": 0,  "Battery Current": 0,  "Battery Power": 0,  "Battery Temperature": 0,  "Battery Remaining Capacity": 0,  "Total Feed-in Energy": 0,  "Total Consumption": 0,  "Power Now": 0,  "Grid Frequency": 0,  "EPS Voltage": 0,  "EPS Current": 0,  "EPS Power": 0,  "EPS Frequency": null } '

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(404)
            self.end_headers()
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            responseTasks, timedout = loop.run_until_complete(asyncio.wait([LoadSolaxData()],timeout=10))
            replyMessage = ""
            solaxIsOnline = ""
            if timedout:
                [task.cancel() for task in timedout]
                loop.run_until_complete(asyncio.wait(timedout))
                replyMessage = offline_message
                solaxIsOnline = "false"
            else:
                responseTask = responseTasks.pop()
                response = responseTask.result()
                replyMessage = json.dumps(response.data)
                solaxIsOnline = "true"
            replyMessage = replyMessage[:1] + '"DeviceIsOnline": ' + solaxIsOnline + ', ' +  replyMessage[1:] 
            self.send_response(200)
            self.end_headers()
            self.wfile.write(replyMessage.encode('utf-8'))

    
print("Starting server...")
httpd = HTTPServer(('', 8000), SimpleHTTPRequestHandler)
httpd.serve_forever()
