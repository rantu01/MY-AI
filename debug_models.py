import requests
key='AIzaSyBCiKubEw-7Nu3C7w54AV0I2a7EMaqHxqY'
for path in ['v1','v1beta','v1beta2']:
    url=f'https://generativelanguage.googleapis.com/{path}/models?key={key}'
    try:
        r=requests.get(url,timeout=10)
        print('\nAPI version:', path, 'status:', r.status_code)
        print(r.text[:2000])
    except Exception as e:
        print(path, 'ERR', e)
