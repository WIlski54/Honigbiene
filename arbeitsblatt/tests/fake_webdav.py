"""In-Memory-WebDAV für Tests: PROPFIND, PUT (If-None-Match), GET, DELETE."""

from urllib.parse import unquote, urlsplit


class FakeWebDAV:
    def __init__(self):
        self.dateien: dict[str, bytes] = {}
        self.aufrufe: list[tuple[str, str, dict]] = []
        self.fehler_bei: dict[str, int] = {}          # Methode -> Statuscode erzwingen
        self.download_manipulieren = False
        self.download_tauschen: bytes | None = None
        self.ordner_fehlt = False

    def __call__(self, method, url, headers, data, auth, timeout, verify):
        assert url.startswith("https://"), "nur HTTPS"
        assert verify is True or isinstance(verify, str)
        assert 2 <= timeout <= 60
        pfad = unquote(urlsplit(url).path)
        name = pfad.rstrip("/").rsplit("/", 1)[-1] if pfad.count("/") >= 2 else ""
        self.aufrufe.append((method, name, dict(headers)))
        if method in self.fehler_bei:
            return self.fehler_bei[method], {}, b""
        if method == "PROPFIND":
            if self.ordner_fehlt:
                return 404, {}, b""
            tiefe = headers.get("Depth", "1")
            eintraege = ['<D:response><D:href>/webdav/ordner/</D:href><D:propstat><D:prop><D:resourcetype><D:collection/></D:resourcetype></D:prop></D:propstat></D:response>']
            if tiefe == "1":
                for n, inhalt in self.dateien.items():
                    eintraege.append(f'<D:response><D:href>/webdav/ordner/{n}</D:href><D:propstat><D:prop><D:getcontentlength>{len(inhalt)}</D:getcontentlength><D:resourcetype/></D:prop><D:status>HTTP/1.1 200 OK</D:status></D:propstat></D:response>')
            xml = '<?xml version="1.0" encoding="utf-8"?><D:multistatus xmlns:D="DAV:">' + "".join(eintraege) + "</D:multistatus>"
            return 207, {}, xml.encode("utf-8")
        if method == "PUT":
            if headers.get("If-None-Match") == "*" and name in self.dateien:
                return 412, {}, b""
            self.dateien[name] = bytes(data)
            return 201, {}, b""
        if method == "GET":
            if name not in self.dateien:
                return 404, {}, b""
            inhalt = self.dateien[name]
            if self.download_tauschen is not None:
                inhalt = self.download_tauschen
            elif self.download_manipulieren:
                inhalt = inhalt[:-1] + bytes([inhalt[-1] ^ 0x01])
            return 200, {"Content-Length": str(len(inhalt))}, inhalt
        if method == "DELETE":
            if name not in self.dateien:
                return 404, {}, b""
            del self.dateien[name]
            return 204, {}, b""
        return 405, {}, b""
