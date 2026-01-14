import never_primp as pp_primp
import requests
import random



def bm_s(sess, sensor, px):
    # cks = '; '.join([f'{k}={v}' for k, v in sess.get_all_cookies()])
    # js_code = sess.get("https://www.cebupacificair.com/en-PH/booking/select-flight?o1=SIN&d1=NGO&adt=1&chd=0&inl=0&inf=0&dd1=2025-04-08&dd2=2025-04-23", headers={
        # "accept": "*/*",
        # "accept-language": "ja",
        # "cache-control": "no-cache",
        # "content-type": "application/json",
        # "origin": "https://www.cebupacificair.com",
        # "pragma": "no-cache",
        # "priority": "u=1, i",
        # "referer": "https://www.cebupacificair.com/",
        # "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
        # "sec-ch-ua-mobile": "?0",
        # "sec-ch-ua-platform": "\"macOS\"",
        # "sec-fetch-dest": "empty",
        # "sec-fetch-mode": "cors",
        # "sec-fetch-site": "same-origin",
        # "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        # "x-dtpc": "7$235381251_169h23vTBTSPRQMGNCBIHUCGOIRAMMCGFKKDNSU-0e0"
    # }).text

    r = requests.post(f'http://127.0.0.1:3000/sbsd/run', json={
        # 'url': 'https://www.cebupacificair.com/en-PH/',
        'url': "https://www.cebupacificair.com/en-PH/booking/select-flight?o1=SIN&d1=NGO&adt=1&chd=0&inl=0&inf=0&dd1=2025-04-08&dd2=2025-04-23",
        # 'js_code':js_code,
        # 'cookies': cks,
        'proxy': px,
    })
    print(r.text)
    # # # cc = {"status":"success","output":{"country_code":"SG","longitude":"103.86","bm_sz":"5FE15918F51E78CA3E8FB597A659E55B~YAAQTxQgF3z9o72aAQAAVIRy2h1Zy44Ao5m6CsaEqbpK68WRLYmW8/W94UdIQ00S/t7qYbP7+3Qwyh6WrCVv3ixM1NhqAQjSSoF87kkMBmbqPge+jzpc5Sezehd11oHMJlt5PCa/ovGgReCZN3BVnwB/FVfrMEimZSsOkEwnKcOTVwX8nz0/ssh8Zid28IWJgvu0UoRXdBuXnxrlEcL6gz+kPdwFFJRpVFZbA4xyDWW0j3ifmVdMnJ15wqjGxqWUEDxDh6ZSUQst/u8ro4yuO0NHr8/QcGoR7mULqlWHLA0PYC5ExlLJnyAsvqLaqlYSoen/3HehiU1R39z1AwZZsxP3X5KYKjJiSj4DB8dfEpeyVNAA2HUBysAxXnijdFjIC1X4WidIdhqiA4+XLpl9G5m6K6s/FK+sZQ","latitude":"1.29","dtCookie":"v_4_srv_1_sn_E4A08CDFB64703B5C7F2A1B596525C1C_perc_100000_ol_0_mul_1_app-3Ab471fd2b229e5313_0_rcs-3Acss_1","AKA_A2":"A","bm_ss":"ab8e18ef4e","bm_so":"EFC4E95E9BB5E1C0978E2BDFBD860A886E16C7CD3F030E8497F4E0154018524F~YAAQTxQgF3v9o72aAQAAVIRy2gXlaNnEPC5/xrL/Bm0L/zQY62rijj7s8VlSrrPtvMVhaBAwfYAlPTMaF7Sln0C4bzyJsIXrDKCmZFv/GEBaZ2leRnVWQfmSBS5WcrWXl/y7RylAg/dXciYxdPkAhObmSqlp9MdRLeC7CoHDA5yB2ntT+tq4oEgCgj+c+XGTb5XXT4H0xM8FcwTYdXLWV17O+avP4DDjvDmtLL6Bfr17wk1khK5cto3gsoupTths29U3Ex/r84Ra0+VXHEyyKHu//ExYEuZD5USglPGDvLnXrJLH7mVfsMH9cs5LrXIEF4sJmCmxs6ohmOpitDft4InHbeBnmX7I11ZnJPiHWn99qSVfJH3hQQC0aumyK58Y63O6q2s8iTc854Czc0eCBAHJnxaQdN+Lf55wrkA6pj+jbDGSq7gYhpeQiyVbqE4UaZiDZoYkcNDFc98rNnQWhvhyUqpwi/eI","ak_bmsc":"B6AD99E09EC5C5820BC481E0CC362268~000000000000000000000000000000~YAAQTxQgF3n9o72aAQAAVIRy2h0RVk26GCWQyk8KqLRA4L6e+BC/cEzU35OeCrd9aQe5fYT40uCLFmpg5NPj4D+D3vs4XkJGLI6UwkbR7o+2MDigK0fKwWHDKZUrWrod76tygWBLbwYq1gYtx5+7WPcKgcN4qcuQWhNubIJeWvWsNiwv4hzrHl9cRljymaRTOoof6BVVlswVeimdd/5wWnyFU3WdvwkiyE4LaUcboFF1J1sjhqZCpcM4rLJVB66J6NJr6B5jCqnlzEHTz97a483Zt98KFduECDJ2U0nKRQB55hiFKlM4ZXzMDqGm71EMduuUrHoCaXo6yPrKEjZenkPVh9RIhtq4e/E6rmVawKi/tmnSV3t8QxRdIQ6qKfwB3GrPax5qJmhw2USaC4aBU3EXgtog4Q","bm_s":"YAAQTxQgF9b9o72aAQAAY5Vy2gQTCOVs9FWDDT3DTJQ3smBrgBcw6O5fGzoBIVhWl70sLL5P7OKtw3Lb/qsxiaCI3hk8Y9akNgzjiyZ7fxr7T2otex9uuqETq7BJwDaMcY/PmLj6degqYSzvvc7eaGkKl9GT7SmjXUC5seynY8skfn1Vi7yH3Q1M78LxiNT8hfSJHgqzHNCbCHqBFePvArRnyYht01dIieuvnwvPpSz5MdGIRZFfFxlPJlhUp07r4ix+1wcN3FsrUiW1UzIeVnGzQrekXXW5G/bbNl/LQBwj52oIa7bIlUOTAqbX1FeRomca04Byskclh4dYlGdCT/UKNybPtqDJOZz+Ehr1mXqJ/ZX4jTRAEkzMwl+VqO39Wvf10WNclPX3vReWQYtptsGR0N30pOYJQ38cCTbpd7Tt6lJiDnnsATBx0KQf2yiQnw1ou1+b5FHcM2omOs7F98Aot3D0y0figqdeEwygrZ/uvpLlVlOrzdsCQOpsEEJ0AS0C07bSlhCE5TTVnhaZiM9jpovs8svyhSuhqcixHFJXiIh9doRBJphIUYcXruvjWEBfSxgLw4tazQpoQRc5yw","_abck":"F38B8123D72FE953EDAEE2EA8CF5E48E~-1~YAAQTxQgF3j9o72aAQAAVIRy2g6N00o+S2rVSljT+rgjHp0WKzPo9JDBFvVt54P0ZB+k/GzcxFErjWZvQoxYDajNPBHF3v4LOUootsS+2kx/Sqv8Mf/jGiOVepTY2WAUCD39URC2wa+oi7nk0ncUfMDz0ddnt9PgN5UycgzbxvAl/EA+wNH36jfT1lZYrpuwQ9K9LRxaVmylQy6n8OyJPrN5DQz54KwHhDra/7/oLFs9vhIvjM/HoXl/YII+Zo5SNA21la+haAr5Ktxe1RI2wvuQde/TxXnrdMV6bWe8+CPtYVMacbQhtCLs+T2YAvA72cdx2uY3gCyK1H4fVapMiSexuX4CZYlgcRPCqwnJ5X7ywg16w7fT1klTNnsWXMQygFVzFEPexDuMba5XqO3kWQXXcs46xlSdNdBVKsGbGoELA3Vs7YIxlZi9Srvw/27QKOdGaeYH8X1Jj2eHeYZ2+S0"}}
    output = r.json()['output']['infos']
    # output = json.loads(output)

    for o in output:
        r = sess.post(o['url'], headers={
            "accept": "*/*",
            "accept-language": "ja",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://www.cebupacificair.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://www.cebupacificair.com/",
            "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        }, data=o['body'])
        print(r.status_code)
        print(r.cookies)

    bm_s = sensor.get_cookie('bm_s')
    print('len(bm_s)', len(bm_s))
    # for o in output:
    #     r = sess.post(sensor.bm_s_url, data=o['body'], headers={
    #         "accept": "*/*",
    #         "accept-language": "ja",
    #         "cache-control": "no-cache",
    #         "content-type": "application/json",
    #         "origin": "https://www.cebupacificair.com",
    #         "pragma": "no-cache",
    #         "priority": "u=1, i",
    #         "referer": "https://www.cebupacificair.com/",
    #         "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
    #         "sec-ch-ua-mobile": "?0",
    #         "sec-ch-ua-platform": "\"macOS\"",
    #         "sec-fetch-dest": "empty",
    #         "sec-fetch-mode": "cors",
    #         "sec-fetch-site": "same-origin",
    #         "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    #         "x-dtpc": "7$235381251_169h23vTBTSPRQMGNCBIHUCGOIRAMMCGFKKDNSU-0e0"
    #     })
    #     print(r.headers)
    # bm_s = r.json()['output']['bm_s']
    # bm_so = r.json()['output']['bm_so']
    # print(len(bm_s), bm_s)
    # output = {
    #     "bm_s": "YAAQKBU7F9+4KjybAQAAVgEyTwQ8V/lmPeX6RYoVXbJmNJZZSaqG8279rlvCf1GXBqj9+KY5sZPBrHm/Cb2UnrZaQxVk6t2vI4Zz6NK7vwglKbpBKtyeo+6/Zw3C3+uvGwWsK7qkHav9OF0wX8t4paio+j9kih/LhwwrcdgucALR+n+oTLM08IjJyJnALIoyrISWx26nWZytU+ZrSKFbz5SIGsGlWdZZXrnHYKNLzVcgk3axMnq5rW5BcwwsubsaWBpAmX73yzdGl8Kkmta2BG1LD4qhDSmKLIYsC7B5CtZkfazewIoYG6Ruph+E/vBkktFGwTNvL0ZSN0ilu2lmi6h4cncBNqDLo7dUPrshhqsCq0gDIw05fne3sI537xA9PXgQ0HhKWtxc5TleWl8krhhbpBSffJznJGKaEpKxmjZ/11GCF8QxsN9BH0OP+AjQBdKsbpVOqAtpWc0ksb3Axrra9YN/Ju+29bKDtWbFEhQEUELuTsZa/gvg2Nnm1FJgyjwb+nGciYNLt9W5jhPFEn4/AVdtE3uL9wB+YW2aElXEJxigFpw1w/0eqKjYQiSpneMbI1DxDCIMy64=",
    # }
    # print(len(bm_s))
    # for k, v in output.items():
    #     sess.cookies.set(name=k, value=v, domain='cebupacificair.com', path='/')


url = "https://soar.cebupacificair.com/ceb-omnix-proxy-v3/availability"
data = {
        "content": "U2FsdGVkX19tJzcPoKf31g/gdFDSTbRWJz44izgGtW+fM2Je1vox9m1MEavTyAw6zjyakzH11L6f5TWYQM40hLaxS4eT/VOYysHATYURjRiDebzEc/Vkqzuuen7DPxSClvCkNxHOqjW4DQ3YpTRJZOMqmLJCTMA4Be7ZYW9mFPvCFW8ajzLvd6YiFQqBgP4B9/WGRJJpJx7G2g0U01IHVkIGoxtc3f8jCxkaNhM0KFtOeah32hjkMNiBkEOy7nWP4ovrEM1fxqlt0MwjKlrfd8f4517cbe59fcU2FsdGVkX1+6bP9Tnfiqf9+msnA4+LwMXKMpwDoEt7Hr3fiCJvFHhSQAR6hSTuPdhyFd85VEBSZFtfuyFseBQ4nk73GB7NQzBO77Jsxv3ChK7qq6u5nNtU9M7VB+QIGc7R3IxPEIvoXWEAmmqX1dLzn9qSs1p1b/tlJJIV+f/8vxjwylejVsEOk5RllI0+A91A8MS5Hh/rvHa4tdx+7mxWXr6iJzP2GWDusm2VoeZ9uBSTY4/SIbcBSGdSrl8JIAJxgoYbT/UJmhcscPkTOTDC2TeIhX2/+bR8p/oM5fV7Q=f774a6esGMNgtLhYAViaHmVplKcWdl93SPBmlAbYPC2nIx+0sdbk0uXcVQ5sIGDgads4g4/VBGjXj6nFbU9GRfReOgw20OhwLp3CsyJXqF6UlguQDXQ0VqmkjlAdc8Hk3HDcWdrBZVG+ScPN0IGB4T7Oc5IfT4+CEZ3lC4bqzBQKc2L4E8s2q4qimv2zNj4DWA7MMt2drgUKg12jFIFf/ev+r5iRTBf8YgiiS/U21sfYGWq5e1V5vwR8/bRBkqsDoxGmL3MlaaS9PskKgae3pw9fabD745UHxyLW5w58BckJGH9ZaJ/7P3A/xaDf0cmxnlg5g++0w9cqNTAt1eJ56GpYMHTlvIUod8QmxR/DGuUl/m1ZtwbFGv6Oa4ucChFckLsZYXKGNQMgNX"}


px = 'http://127.0.0.1:7890'
# px = f'http://user-jetstar01-region-jp-sessid-twe{random.randint(123123, 4567789)}-sesstime-5-keep-true:C3Ngy7Fs@43.135.155.176:8881'
session = pp_primp.Client(impersonate='safari_ios_26',impersonate_os='macos',cookie_store=True, proxy=px, split_cookies=True)
bm_s(session,session,px)
r = requests.post('http://127.0.0.1:59001/akamai/gen', json={
        # r = requests.post('http://43.135.155.176:59001/akamai/gen', json={
        # r = requests.post('http://lcc.unififi.com/akamai/gen', json={
        'type': '5J',
        'proxy': px
    })
cookies = r.json()['cookies']


# res = session.get('https://fanpa.weneedstudy.cn:8443/complexTest')
# px = 'http://127.0.0.1:8881'
# px = f'http://user-jetstar01-region-jp-sessid-twe{random.randint(123123, 4567789)}-sesstime-5-keep-true:C3Ngy7Fs@43.135.155.176:8881'


session.update_cookies(cookies)

for i in range(10):
# res = session.get('https://47.113.101.23:4442/')
    response = session.post(url, headers={
                "sec-ch-ua-platform": "\"macOS\"",
                "X-Auth-Token": "517cbe59fcU2FsdGVkX1+6bP9Tnfiqf9+msnA4+LwMXKMpwDoEt7Hr3fiCJvFHhSQAR6hSTuPdhyFd85VEBSZFtfuyFseBQ4nk73GB7NQzBO77Jsxv3ChK7qq6u5nNtU9M7VB+QIGc7R3IxPEIvoXWEAmmqX1dLzn9qSs1p1b/tlJJIV+f/8vxjwylejVsEOk5RllI0+A91A8MS5Hh/rvHa4tdx+7mxWXr6iJzP2GWDusm2VoeZ9uBSTY4/SIbcBSGdSrl8JIAJxgoYbT/UJmhcscPkTOTDC2TeIhX2/+bR8p/oM5fV7Q=",
                "Authorization": "Bearer fd8f4f774a6esGMNgtLhYAViaHmVplKcWdl93S",
                "X-Path": "U2FsdGVkX18wB9/tKt46By0mFYbll0LtXxbU8jJL1po=",
                "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?0",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
                "origin": "https://www.cebupacificair.com",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://www.cebupacificair.com/",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "ja",
                "priority": "u=1, i"
            }, json=data)
    print(response.text)
