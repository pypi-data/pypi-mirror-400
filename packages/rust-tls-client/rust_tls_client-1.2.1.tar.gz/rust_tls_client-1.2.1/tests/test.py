from rust_tls_client import Client


c = Client(proxy='http://127.0.0.1:8881', split_cookies=True, impersonate='chrome_141')

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en",
    'accept-encoding':'gzip, deflate, br, zstd',
    "content-type": "application/json",
    "origin": "https://www.cebupacificair.com",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
    "referer": "https://www.cebupacificair.com/",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "authorization": "Bearer 03cb404844gOuWpvjSqwRj3mtKcwyN59drCGLa",
    "x-auth-token": "9fac630315U2FsdGVkX1+3heYU0KgEttapN6gpVKV9PHH8L3DR/A6RoOEZAev0Vpk1uhkQyhSQx7K/eu7Qh8nc125k66wh9s4We6o5q8qdbCMhzC1/nzX9HgXsLsIfkn2NRUUZjGjVAExL8elzxgXB5wSxQ20abrrbQCh1w1dB+v+Uh9HhTF+zBUTJ6r3lNlB5QT9wuJmfPMu0fXQu+5XzoR224PFWWlBMEsCP/MRAPEQlkszjd0cwfW43S37792LOkh62Gc2F6FYdatr5WB7dgpGXmQcNXSlmYYT4j/lYKdo38IMt01w=",
    "x-path": "U2FsdGVkX18xBksZupSVaMqeaF8xA4+QrvUfUD+F9CA=",
    'ccc':'aaa'
}

url = "https://soar.cebupacificair.com/ceb-omnix-proxy-v3/availability"
data = {
    "content": "U2FsdGVkX1/F5Ic8v3u7GG7FDCol3q76dMO/ZofggkzXX3HKMXhwFTUTpZgPecsjP7dTLEKdR8rakps9Av97YH2HFnlMr+Fi130r52H27BbSdNyWlOtqnswiZnc0ahs9Pj04EPOG0rahvw9ASeAvHkmT6NTJUSEdUE6f+aY5vzdBtyZJLtLTvAz4EsH4Q7LNj0UXUyRnGIN+PZ09XIzwlXlvayTh3lT28mWEkKs0cX1zhNelos3difTeQ4EjSjWp7FXvdzLGEelz1ozFkqx/NvTI6+mHyOn/dhLpJnQlsCx8ooW/E+KcOWi3jWarLDAJ+hy7JgeKJqJ03cb404844gOuWpvjSqwRj3mtKcwyN59drCGLalgIsecmZEwSeMFlh9XA8lt4uP2uB8S/iuqhkf9cBNN6NdeKY7Mj/KnWcDo9fac630315U2FsdGVkX1+3heYU0KgEttapN6gpVKV9PHH8L3DR/A6RoOEZAev0Vpk1uhkQyhSQx7K/eu7Qh8nc125k66wh9s4We6o5q8qdbCMhzC1/nzX9HgXsLsIfkn2NRUUZjGjVAExL8elzxgXB5wSxQ20abrrbQCh1w1dB+v+Uh9HhTF+zBUTJ6r3lNlB5QT9wuJmfPMu0fXQu+5XzoR224PFWWlBMEsCP/MRAPEQlkszjd0cwfW43S37792LOkh62Gc2F6FYdatr5WB7dgpGXmQcNXSlmYYT4j/lYKdo38IMt01w=WB60VQWD9tC227pGtUAQ2uHuYWCFtP4dLMO4xJRBT4qHiMchlaq2BD4Rps4kwSDmbCXrD5J4SbnUo6cWCWjTuAD0Fb1xi0CcxqT38N3iGBlXvuAe+8hmENQvp6ACLPUAoe4XPl8CtlbpVABch3Z55HOWK1y8GNVAWZ9WdVEHjQ8zPjmTtGskOwCeEIAlXzIvAN90QcF3C3j/gPYpIkbovHs3dzqVKDogfVUFVhFX3AjNxnSuZFD9ojpcxLN"
}

r = c.post(url,json=data,
    headers = headers,)
print(r.text)