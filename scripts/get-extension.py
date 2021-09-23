import sys


def main():
    content = sys.argv[1]
    res = content.split('.')[-1]
    print(res)


if __name__ == '__main__':
    main()
