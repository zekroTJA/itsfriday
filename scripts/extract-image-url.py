import re
import sys

RX_IMAGE = r'(?:!\[[\w\s\d]*\]\()?(https:\/\/[\w\d\-\_\.\?#&=\/]+)\)?'


def main():
    content = sys.argv[1]
    res = re.findall(RX_IMAGE, content)[0]
    print(res)


if __name__ == '__main__':
    main()
