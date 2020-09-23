import solax
import asyncio
import json
import sys

from http.server import HTTPServer, BaseHTTPRequestHandler

async def LoadSolaxData():
    r = await solax.real_time_api('5.8.8.8')
    return await r.get_data()


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    OFFLINE_MESSAGE = """{
  "PV1 Current": NaN,
  "PV2 Current": NaN,
  "PV1 Voltage": NaN,
  "PV2 Voltage": NaN,
  "Output Current": NaN,
  "Network Voltage": NaN,
  "AC Power": NaN,
  "Inverter Temperature": NaN,
  "Today's Energy": NaN,
  "Total Energy": NaN,
  "Exported Power": NaN,
  "PV1 Power": NaN,
  "PV2 Power": NaN,
  "Battery Voltage": NaN,
  "Battery Current": NaN,
  "Battery Power": NaN,
  "Battery Temperature": NaN,
  "Battery Remaining Capacity": NaN,
  "Total Feed-in Energy": NaN,
  "Total Consumption": NaN,
  "Power Now": NaN,
  "Grid Frequency": NaN,
  "EPS Voltage": NaN,
  "EPS Current": NaN,
  "EPS Power": NaN,
  "EPS Frequency": NaN
}"""
    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(404)
            self.end_headers()
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            responseTasks, timedout = loop.run_until_complete(asyncio.wait([LoadSolaxData()],timeout=30))
            if timedout:
                [task.cancel() for task in timedout]
                loop.run_until_complete(asyncio.wait(timedout))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(OFFLINE_MESSAGE.encode.encode('utf-8'))
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
