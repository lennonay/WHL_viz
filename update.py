from datetime import datetime

def updater():
    today = datetime.today().strftime('%Y-%m-%d')
    file1 = open("data/update.txt", "w")
    file1.write('last updated: ' + today + '\n')
    file1.close()

if __name__ == '__main__':
    updater()