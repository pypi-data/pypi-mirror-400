#!/usr/bin/env python3
import sys, ast, os, subprocess, copy
from http.server import SimpleHTTPRequestHandler, HTTPServer
from http import HTTPStatus
from urllib import parse

class CGIHTTPRequestHandler(SimpleHTTPRequestHandler):
    cgi_dirs    = ["/cgi-bin", "/htbin"]
    have_fork   = hasattr(os, "fork")
    encoding    = "UTF-8"

    # --- Logging (UTF-8 safe) ---
    def log_message(self, fmt, *args):
        msg     = fmt % args
        try:
            sys.stderr.write(msg + "\n")
        except Exception:
            sys.stderr.write(msg.encode(self.encoding, "replace").decode() + "\n")

    # --- Request dispatch ---
    def do_POST(self):
        if self.is_cgi():
            self.run_cgi()
        else:
            self.send_error(HTTPStatus.NOT_IMPLEMENTED, "POST is only for CGI")

    def send_head(self):
        if self.is_cgi():
            return self.run_cgi()
        return super().send_head()

    # --- CGI detection (判定だけ) ---
    def is_cgi(self):
        parsed  = parse.urlsplit(self.path)
        path    = parsed.path

        for d in self.cgi_dirs:
            if path.startswith(d + "/") or path == d:
                script = path[len(d):].lstrip("/")
                self.cgi_info = (d, script)
                return True
        return False

    # --- Build environment variables ---
    def build_env(self, scriptname, path_info, query):
        env     = copy.deepcopy(os.environ)
        env.update({
            "SERVER_SOFTWARE"   : self.version_string(),
            "SERVER_NAME"       : self.server.server_name,
            "GATEWAY_INTERFACE" : "CGI/1.1",
            "SERVER_PROTOCOL"   : self.protocol_version,
            "SERVER_PORT"       : str(self.server.server_port),
            "REQUEST_METHOD"    : self.command,
            "SCRIPT_NAME"       : scriptname,
            "QUERY_STRING"      : query,
            "REMOTE_ADDR"       : self.client_address[0],
        })

        # PATH_INFO / PATH_TRANSLATED
        uqrest  = parse.unquote(path_info)
        env["PATH_INFO"]        = uqrest
        env["PATH_TRANSLATED"]  = self.translate_path(uqrest)

        # Content headers
        env["CONTENT_TYPE"]     = self.headers.get("content-type", "")
        length  = self.headers.get("content-length")
        if length:
            env["CONTENT_LENGTH"] = length

        # Common HTTP headers
        for h in ("user-agent", "cookie", "referer"):
            v   = self.headers.get(h)
            if v:
                env["HTTP_" + h.upper().replace("-", "_")] = v

        return env

    # --- Execute CGI script ---
    def run_cgi(self): # self.path から path と query を再解析（本家と同じ）
        parsed  = parse.urlsplit(self.path)
        path    = parsed.path
        query   = parsed.query

        dir, rest               = self.cgi_info

        # PATH_INFO を抽出
        script, _, extra        = rest.partition("/")
        scriptname              = f"{dir}/{script}"
        scriptfile              = self.translate_path(scriptname)

        if not os.path.isfile(scriptfile):
            self.send_error(HTTPStatus.NOT_FOUND, f"No such CGI script: {scriptname}")
            return

        # PATH_INFO の構築
        if extra:
            path_info           = "/" + extra
        else:
            path_info           = ""

        env     = self.build_env(scriptname, path_info, query)

        self.send_response(HTTPStatus.OK, "Script output follows")
        self.flush_headers()

        if self.have_fork:
            self.run_cgi_unix(scriptfile, env, query)
        else:
            self.run_cgi_subprocess(scriptfile, env, query)

    # --- Unix fork/exec ---
    def run_cgi_unix(self, scriptfile, env, query):
        args    = [scriptfile]
        if "=" not in query:
            args.append(query)

        pid     = os.fork()
        if pid  != 0:
            os.waitpid(pid, 0)
            return

        os.dup2(self.rfile.fileno(), 0)
        os.dup2(self.wfile.fileno(), 1)
        os.execve(scriptfile, args, env)

    # --- Windows / non-Unix subprocess ---
    def run_cgi_subprocess(self, scriptfile, env, query):
        cmd     = [scriptfile]
        if scriptfile.lower().endswith(".py"):
            cmd = [sys.executable, "-u"] + cmd
        if "=" not in query:
            cmd.append(query)

        # CONTENT_LENGTH の長さを読む
        length              = int(self.headers.get("content-length", 0) or 0)
        body                = b""
        while len(body)     < length:
            chunk           = self.rfile.read(length - len(body))
            if not chunk:
                break
            body            += chunk
        if length           == 0:
            body            = None

        proc                = subprocess.Popen(
            cmd,
            stdin           = subprocess.PIPE,
            stdout          = subprocess.PIPE,
            stderr          = subprocess.PIPE,
            env             = env,
        )

        stdout, stderr      = proc.communicate(body)
        self.wfile.write(stdout)

        if stderr:
            self.log_error("%s", stderr.decode(self.encoding, "replace"))

class UTF8CGIHandler(CGIHTTPRequestHandler):
    def log_message(self, format, *args):
        msg                 = format % args

        if msg.startswith(("b'", 'b"')):
            try:
                raw         = ast.literal_eval(msg)
                msg         = raw.decode("UTF-8", "replace")
            except Exception:
                pass

        sys.stderr.write(f"{msg}\n")

class CGIHTTP:
    def __init__(
        self, 
        ip                  = "0.0.0.0", 
        port                = 8000,
        handler             = UTF8CGIHandler
    ):
        self.ip             = ip
        self.port           = port
        self.handler        = handler
    
    def serve_forever(self):
        HTTPServer(
            (self.ip, self.port), 
            self.handler
        ).serve_forever()


if __name__ == "__main__":
    CGIHTTP().serve_forever()
