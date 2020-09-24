import sys
from tendo import singleton
from OSGApp import OSledgeGraphApplication

def main():
    instance = singleton.SingleInstance()
    app = OSledgeGraphApplication(sys.argv)
    return sys.exit(app.exec())


if __name__ == '__main__':
    main()
