#!/usr/bin/env python3
import http.server
import os
from email.parser import BytesParser
from email.policy import default

# Save uploads in the directory where the server is running
UPLOAD_DIR = os.getcwd()

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_type = self.headers.get("Content-Type")
        if not content_type or "multipart/form-data" not in content_type:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid request\n")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        # Parse multipart body
        msg = BytesParser(policy=default).parsebytes(
            b"Content-Type: " + content_type.encode() + b"\r\n\r\n" + body
        )

        for part in msg.iter_parts():
            if part.get_content_disposition() == "form-data":
                filename = part.get_filename()
                if filename:
                    safe_name = os.path.basename(filename)  # strip dangerous paths
                    filepath = os.path.join(UPLOAD_DIR, safe_name)
                    with open(filepath, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(f"Uploaded {safe_name}\n".encode())
                    return

        self.send_response(400)
        self.end_headers()
        self.wfile.write(b"No file uploaded\n")


if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", 8000), SimpleHTTPRequestHandler)
    print(f"Serving on port 8000, saving uploads to: {UPLOAD_DIR}")
    server.serve_forever()
