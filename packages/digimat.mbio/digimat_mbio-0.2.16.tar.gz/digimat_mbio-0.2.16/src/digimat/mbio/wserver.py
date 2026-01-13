import functools

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import socket
import threading
import time
import shutil
import pathlib
import hashlib
import requests
import os
import json
from urllib.parse import urlparse, parse_qs

# warning: importing pathlib replace any "import os" order

# https://nachtimwald.com/2019/12/10/python-http-server/
# SSL: https://realpython.com/python-http-server/


class QuietSimpleHTTPRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, mformat, *args):
        pass

    def log_error(self, mformat, *args):
        pass

    def setup(self):
        super().setup()
        self.request.settimeout(60)

    def handle_one_request(self):
        try:
            return super().handle_one_request()
        except socket.timeout:
            # --- Handle the timeout gracefully ---
            # print(f"[TIMEOUT] {self.client_address} request timed out")
            try:
                self.send_error(408, "Request Timeout")
            except Exception:
                pass  # ignore if client already disconnected
            self.close_connection = True
        except ConnectionResetError:
            # print(f"[RESET] {self.client_address} connection reset")
            self.close_connection = True


class QuietSimpleHTTPRequestHandlerWithLogger(QuietSimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, logger=None, callbacks={}, **kwargs):
        self._logger = logger
        self._callbacks=callbacks
        super().__init__(*args, directory=directory, **kwargs)

    @property
    def logger(self):
        return self._logger

    def log_message(self, mformat, *args):
        logger=self.logger
        if logger:
            host,port=self.client_address
            message='WS REQUEST %s %s' % (host, mformat % args)
            logger.debug(message)

    def log_error(self, mformat, *args):
        logger=self.logger
        if logger:
            host,port=self.client_address
            message='WS ERROR %s %s' % (host, mformat % args)
            logger.error(message)

    def handle_one_request(self):
        logger=self.logger
        try:
            return super().handle_one_request()
        except socket.timeout:
            # --- Handle the timeout gracefully ---
            # print(f"[TIMEOUT] {self.client_address} request timed out")
            try:
                self.send_error(408, "Request Timeout")
                if logger:
                    logger.error('WS request timeout')
            except Exception:
                if logger:
                    logger.exception('WS request exception')
                pass  # ignore if client already disconnected
            self.close_connection = True
        except ConnectionResetError:
            # print(f"[RESET] {self.client_address} connection reset")
            if logger:
                logger.exception('WS request exception')
            self.close_connection = True

    def do_GET(self):
        logger=self.logger
        try:
            callbacks=self._callbacks.get('GET')
            if callbacks:
                parsed = urlparse(self.path)
                callback=callbacks.get(parsed.path)
                if callback:
                    params = parse_qs(parsed.query)
                    # retain only 1 value for each args
                    for key in params.keys():
                        params[key]=params[key][0]

                    if logger:
                        self.logger.debug('WS GET callback %s(%s) %s' % (parsed.path, params, callback))
                    callback(self, params)
                    return
        except:
            self.logger.exception('do_GET')
            pass

        try:
            # Fallback to default file handling for all other paths
            return super().do_GET()
        except:
            pass

    def do_POST(self):
        logger=self.logger
        try:
            callbacks=self._callbacks.get('POST')
            if callbacks:
                parsed = urlparse(self.path)
                callback=callbacks.get(parsed.path)
                if callback:
                    params = parse_qs(parsed.query)
                    # retain only 1 value for each args
                    for key in params.keys():
                        params[key]=params[key][0]

                    content_length = int(self.headers.get('Content-Length', 0))
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data)

                    if logger:
                        self.logger.debug('WS POST callback %s(%s) %s' % (parsed.path, params, callback))
                        # self.logger.debug(data)
                    callback(self, params, data)
                    return
        except:
            # self.logger.exception('do_POST')
            pass


class TemporaryWebServer(object):
    def __init__(self, fpath='/tmp/wserver', port=8000, host=None, logger=None):
        self._path: pathlib.Path = pathlib.Path(fpath)
        self._host=host
        self._port=int(port)
        self._interface=''
        self._thread=None
        self._httpd=None
        self._files={}
        self._enableAutoShutdown=True
        self._timeout=0
        self._callbacks={'GET': {}, 'POST': {}}
        self._logger=logger

    @property
    def logger(self):
        return self._logger

    def url(self, path=None):
        host=self._host or self._interface
        if host:
            url='http://%s:%d' % (host, self._port)
            if path:
                if path[0]!='/':
                    url += '/'
                url += path
            return url

    def registerCallback(self, method, rpath, callback):
        try:
            if rpath and callback and callable(callback):
                data=self._callbacks.get(method.upper())
                if data is not None:
                    data[rpath]=callback
        except:
            pass

    def registerGetCallback(self, rpath, callback):
        return self.registerCallback('GET', rpath, callback)

    def registerPostCallback(self, rpath, callback):
        return self.registerCallback('POST', rpath, callback)

    def registerGetPostCallback(self, rpath, callback):
        self.registerGetCallback(rpath, callback)
        self.registerPostCallback(rpath, callback)

    def server(self):
        # handler=functools.partial(QuietSimpleHTTPRequestHandler, directory=self.pathstr())
        handler=functools.partial(QuietSimpleHTTPRequestHandlerWithLogger,
                                  directory=self.pathstr(),
                                  logger=self.logger,
                                  callbacks=self._callbacks)

        with ThreadingHTTPServer((self._interface, self._port), handler) as httpd:
            try:
                self._httpd=httpd
                httpd.serve_forever()
            except:
                pass

            try:
                httpd.server_close()
            except:
                pass

        self._httpd=None

    def pathstr(self):
        try:
            return str(self._path)
        except:
            pass

    def createPath(self):
        try:
            self._path.mkdir(parents=True, exist_ok=True)
            return True
        except:
            pass
        return False

    def linkPath(self, fpath, name=None):
        try:
            p: pathlib.Path = pathlib.Path(fpath).expanduser()
            if p.exists() and p.is_dir():
                self.createPath()
                fname=p.name
                if name:
                    fname=name
                os.symlink(str(p), str(self.getPathForFile(fname)))
        except:
            pass

    def getPathForFile(self, fname):
        try:
            return self._path.joinpath(fname)
        except:
            pass

    def isFile(self, fname):
        try:
            p=self.getPathForFile(fname)
            if p.exists() and p.is_file():
                return True
        except:
            pass
        return False

    def computeDataHashCodeForFile(self, f):
        try:
            return hashlib.file_digest(f, 'sha256').hexdigest()
        except:
            pass

    def importFile(self, fpath, fname=None, timeout=0):
        try:
            sp=pathlib.Path(fpath)
            if sp.is_file():
                self.start()
                if not fname:
                    fname=sp.name
                tp=self.getPathForFile(fname)
                # only copy file is not already exists (prevent file corruption while exposed)
                if not tp.is_file():
                    shutil.copyfile(str(sp), str(tp))
                self._files[fname]={'fname': fname, 'stamp': time.time(), 'timeout': timeout}
                self._timeout=time.time()+60
                url=self.url(fname)
                if url:
                    return url
        except:
            pass
        return False

    def getFileContent(self, fname):
        try:
            if fname:
                p=self.getPathForFile(fname)
                # print(p)
                with open(str(p), 'rb') as f:
                    data=f.read()
                    return data
        except:
            pass

    def removeFile(self, fname):
        try:
            if fname:
                p=self.getPathForFile(fname)
                p.unlink()
                try:
                    del self._files[fname]
                except:
                    pass
                return True
        except:
            pass
        return False

    def isTimeout(self, stamp):
        if time.time()>=stamp:
            return True
        return False

    def isFileTimeout(self, fname):
        try:
            timeout=self._files[fname].get('timeout', 0)
            stamp=self._files[fname].get('stamp', 0)
            p=self.getPathForFile(fname)
            if not self.isFile(fname):
                return True
            if timeout>0 and self.isTimeout(stamp+timeout):
                return True
                # p=self.getPathForFile(fname)
                # info=p.stat()
                # age=time.time()-info.st_mtime
                # if age>=timeout:
                    # return True
        except:
            pass
        return False

    def getFiles(self):
        try:
            files=[]
            for f in self._path.iterdir():
                fname=f.name
                if not self.isFile(fname):
                    continue
                if self.isFileTimeout(fname):
                    self.removeFile(fname)
                    continue
                files.append(fname)
            return files
        except:
            pass

    def start(self):
        if not self._thread:
            self.createPath()
            self._thread=threading.Thread(target=self.server)
            self._thread.daemon=True
            self._thread.start()

    def stop(self):
        self.enableAutoShutdown()
        if self._thread:
            try:
                self._httpd.shutdown()
            except:
                pass

            try:
                # force a fake request to the server (may be waiting for a request)
                proxies = { 'http': '', 'https': '' }
                requests.get('http://localhost:%d/shutdown' % self._port, timeout=1.0, proxies=proxies)
            except:
                pass

            self._thread.join()
            self._thread=None

    def isRunning(self):
        if self._thread:
            return True
        return False

    def keelAlive(self):
        if self.isRunning():
            self._timeout=time.time()+15

    def enableAutoShutdown(self, state=True):
        self._enableAutoShutdown=state

    def disableAutoShutdown(self):
        self.enableAutoShutdown(False)

    def manager(self):
        files=self.getFiles()
        if files:
            self._timeout=time.time()+60

        if not self._enableAutoShutdown:
            self.keelAlive()

        if time.time()>self._timeout:
            self.stop()

    def __del__(self):
        self.stop()


if __name__ == '__main__':
    ws=TemporaryWebServer('/tmp/wserver')
    ws.importFile('/tmp/myfile', 'fhe', 600)
    ws.start()
