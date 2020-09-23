import solax
import asyncio
import json
import sys

from http.server import HTTPServer, BaseHTTPRequestHandler

async def LoadSolaxData():
    r = await solax.real_time_api('5.8.8.8')
    return await r.get_data()

offline_message = '{ "PV1 Current": null, "PV2 Current": null,"PV1 Voltage": null,  "PV2 Voltage": null,  "Output Current": null,  "Network Voltage": null,  "AC Power": null,  "Inverter Temperature": null,  "Today\'s Energy": null,  "Total Energy": null,  "Exported Power": null,  "PV1 Power": null,  "PV2 Power": null,  "Battery Voltage": null,  "Battery Current": null,  "Battery Power": null,  "Battery Temperature": null,  "Battery Remaining Capacity": null,  "Total Feed-in Energy": null,  "Total Consumption": null,  "Power Now": null,  "Grid Frequency": null,  "EPS Voltage": null,  "EPS Current": null,  "EPS Power": null,  "EPS Frequency": null } '

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(404)
            self.end_headers()
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            responseTasks, timedout = loop.run_until_complete(asyncio.wait([LoadSolaxData()],timeout=10))
            if timedout:
                [task.cancel() for task in timedout]
                loop.run_until_complete(asyncio.wait(timedout))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(offline_message.encode('utf-8'))
            else:
                responseTask = responseTasks.pop()
                response = responseTask.result()
                dataAsJson = json.dumps(response.data)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(dataAsJson.encode('utf-8'))

    
print("Starting server...")
httpd = HTTPServer(('', 8000), SimpleHTTPRequestHandler)
httpd.serve_forever()
