import solax
import asyncio
import json
import sys

from http.server import HTTPServer, BaseHTTPRequestHandler

async def LoadSolaxData():
    r = await solax.real_time_api('5.8.8.8')
    return await r.get_data()


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

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
                self.send_response(408)
                self.end_headers()
            else:
                responseTask = responseTasks.pop()
                response = responseTask.result()
                dataAsJson = json.dumps(response.data)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(dataAsJson.encode('utf-8'))

    
print("Starting server...")
httpd = HTTPServer(('', 80), SimpleHTTPRequestHandler)
httpd.serve_forever()
