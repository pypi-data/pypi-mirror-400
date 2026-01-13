import os, sys, re
from urllib import parse

class FieldStorage:
    def __init__(self):
        self.encoding       = "UTF-8"
        self.method         = os.environ.get("REQUEST_METHOD", "GET")
        if self.method      == "GET": 
            self.query      = os.environ.get("QUERY_STRING", "")            # GET : URL の ? 以降が QUERY_STRING に入る
            self.params     = parse.parse_qs(self.query)                    # URL クエリ形式の文字列を辞書形式に変換

        elif self.method    == "POST": 
            length          = int(os.environ.get("CONTENT_LENGTH", 0))      # POST データの長さ(バイト数)を環境変数 CONTENT_LENGTH から取得
            raw             = sys.stdin.buffer.read(length)
            contentType= os.environ.get("CONTENT_TYPE", "")

            if contentType.startswith("multipart/form-data"): 
                boundary            = None 
                for part in contentType.split(";"): 
                    part            = part.strip() 
                    if part.startswith("boundary="): 
                        boundary    = part.split("=", 1)[1].encode() 
                self.params = self.parse_mp(raw, boundary) 
            else: 
                self.query  = raw.decode(self.encoding, "replace") 
                self.params = parse.parse_qs(self.query)                    # URL クエリ形式の文字列を辞書形式に変換
        else:
            self.query      = ""
            self.params     = dict()

        
    def parse_mp(self, raw, boundary): 
        result                      = {} 
        parts                       = raw.split(b"--" + boundary) 
        for part in parts: 
            part                    = part.strip() 
            if part in (b"", b"--"):
                continue 
            
            # 余計な改行を吸収 
            header, _, body         = part.lstrip(b"\r\n").partition(b"\r\n\r\n") 
            body                    = body.rstrip(b"\r\n") 
            headers                 = header.decode(self.encoding, "replace").split("\r\n") 
            name                    = None 
            filename                = None 
            for h in headers: 
                h_low               = h.lower() 
                if h_low.startswith("content-disposition"): 
                    # name="xxx" 
                    m               = re.search(r'name="([^"]+)"', h) 
                    if m: 
                        name        = m.group(1) 
                        
                    # filename="xxx" 
                    m               = re.search(r'filename="([^"]+)"', h) 
                    if m: 
                        filename    = m.group(1) 
                            
            if name is None: 
                continue 

            if filename and filename != "":
                result.setdefault(name, []).append(
                    { 
                        "filename": filename, 
                        "content": body 
                    }
                ) 
            else: 
                result.setdefault(name, []).append( 
                    body.decode(self.encoding, "replace") 
                ) 
        return result
    
    def getlist(
        self,
        formName            = "formName",
        default             = ""
    ):
        return self.params.get(formName, [default])
    
    def getfirst(
        self,
        formName            = "formName",
        default             = ""
    ):
        return self.getlist(formName, default)[0]
    
    def getvalue(
        self,
        formName            = "formName",
        default             = ""
    ):
        value               = self.getlist(formName, default)
        if len(value) > 1:
            return value
        else:
            return value[0]