from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import signal

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/hello':
            logging.info('Hello endpoint was called')
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Hello World')
        else:
            self.send_response(404)
            self.end_headers()


def run():
    def shutdown_handler(signal_received, frame):
        logging.info('Service is shutting down...')
        exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    server = HTTPServer(('127.0.0.1', 6814), Handler)
    logging.info('Service started on port 6814')
    server.serve_forever()


if __name__ == '__main__':
    run()
