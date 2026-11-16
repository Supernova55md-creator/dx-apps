#!/usr/bin/env python3
"""DXナビ（dx-apps）復号：編集用の元ファイルを取り出す
使い方: python3 decrypt.py <dx-apps リポジトリ> <PASSPHRASE.txt> <出力フォルダ>
  <repo>/<slug>/app.enc を復号して <出力>/<slug>/index.html に書く。SALT.txt も出力フォルダに書く。
  編集後は encrypt.py <出力フォルダ> <repo> で暗号化し直す（PASSPHRASE.txt を出力フォルダに置く）。
"""
import sys,os,json,base64,hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from encrypt import norm
repo,pf,out=sys.argv[1:4]
pw=norm(open(pf,encoding='utf-8').read()); keys={}
for slug in sorted(os.listdir(repo)):
    f=os.path.join(repo,slug,'app.enc')
    if not os.path.isfile(f): continue
    e=json.load(open(f)); salt=base64.b64decode(e['salt'])
    k=keys.get(e['salt']) or keys.setdefault(e['salt'],hashlib.pbkdf2_hmac('sha256',pw.encode(),salt,e['it'],32))
    html=AESGCM(k).decrypt(base64.b64decode(e['iv']),base64.b64decode(e['ct']),e.get('aad','').encode() or None)
    os.makedirs(os.path.join(out,slug),exist_ok=True)
    open(os.path.join(out,slug,'index.html'),'wb').write(html)
    open(os.path.join(out,'SALT.txt'),'w').write(e['salt'])
    print('decrypted',slug)
