#!/usr/bin/env python3
"""DXナビ（dx-apps）暗号化ビルド
使い方: python3 encrypt.py <元ファイルのフォルダ dx-apps-src> <dx-apps リポジトリ>
  - <src>/PASSPHRASE.txt のパスフレーズで、<src>/<slug>/index.html を
    AES-256-GCM（鍵は PBKDF2-SHA256・60万回）で暗号化し <repo>/<slug>/app.enc に書く。
  - salt は DXナビ全体で1つ（<src>/SALT.txt、無ければ作る）。端末は1回の入力で全ツールを開ける。
  - <repo>/<slug>/index.html はローダー（tools/loader.html から生成）に置き換える。
  - パスフレーズの正規化（JS側と同じ）：NFKC → カタカナをひらがなに → 空白・「・」を除く。
"""
import sys,os,json,base64,secrets,hashlib,unicodedata,re
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
ITER=600000
def norm(p):
    p=unicodedata.normalize('NFKC',p)
    p=''.join(chr(ord(c)-0x60) if 'ァ'<=c<='ヶ' else c for c in p)
    return re.sub(r'[\s・･]','',p)
def main(src,repo):
    pw=norm(open(os.path.join(src,'PASSPHRASE.txt'),encoding='utf-8').read())
    sp=os.path.join(src,'SALT.txt')
    if not os.path.exists(sp): open(sp,'w').write(base64.b64encode(secrets.token_bytes(16)).decode())
    salt=base64.b64decode(open(sp).read().strip())
    key=hashlib.pbkdf2_hmac('sha256',pw.encode('utf-8'),salt,ITER,32)
    loader=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'loader.html'),encoding='utf-8').read()
    for slug in sorted(os.listdir(src)):
        f=os.path.join(src,slug,'index.html')
        if slug.startswith('_') or not os.path.isfile(f): continue
        html=open(f,encoding='utf-8').read()
        m=re.search(r'<title>(.*?)</title>',html,re.S); title=m.group(1).strip() if m else slug
        m=re.search(r'apple-mobile-web-app-title" content="([^"]*)"',html); short=m.group(1) if m else title
        m=re.search(r'name="theme-color" content="([^"]*)"',html); color=m.group(1) if m else '#3730a3'
        iv=secrets.token_bytes(12)
        ct=AESGCM(key).encrypt(iv,html.encode('utf-8'),slug.encode())
        enc={"v":1,"kdf":"PBKDF2-SHA256","it":ITER,"salt":base64.b64encode(salt).decode(),"iv":base64.b64encode(iv).decode(),"aad":slug,"ct":base64.b64encode(ct).decode()}
        os.makedirs(os.path.join(repo,slug),exist_ok=True)
        json.dump(enc,open(os.path.join(repo,slug,'app.enc'),'w'))
        out=loader.replace('{{TITLE}}',title).replace('{{SHORT}}',short).replace('{{COLOR}}',color)
        open(os.path.join(repo,slug,'index.html'),'w',encoding='utf-8').write(out)
        print('encrypted',slug,len(html),'bytes')
if __name__=='__main__': main(sys.argv[1],sys.argv[2])
