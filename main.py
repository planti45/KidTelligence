import sys
import sqlite3
import random as rnd
from pymorphy2 import MorphAnalyzer

from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication

morph = MorphAnalyzer()

OBJECTS = ['яблоко', 'банан', 'апельсин',
           'абрикос', 'слива', 'груша',
           'ананас', 'лимон', 'персик']

NAMES = ['Саша', 'Серёжа', 'Дима', 'Лёша', 'Максим',
         'Ваня', 'Артем', 'Миша', 'Кирилл', 'Егор',
         'Лена', 'Оля', 'Таня', 'Аня', 'Катя',
         'Маша', 'Ира', 'Даша', 'Настя', 'Юля']

PLACES = ['на столе', 'в тарелке', 'в ящике', 'в коробке', 'в миске', ]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.con = sqlite3.connect('kidData.sqlite')
        self.difficulty = 'easy'
        self.name = ''
        self.form = 1
        self.balance = 1000
        self.medals = []
        self.medal_types = ['medal', 'heart', 'globus', 'book', 'feather', 'star']
        self.answer = 0
        self.initUI()

    def initUI(self):
        uic.loadUi('main.ui', self)
        self.changeColor()
        self.emptyNameLabel.hide()
        self.setFixedSize(1229, 789)
        self.pages.setCurrentWidget(self.greetingPage)
        self.balanceLabel.setText(f'{self.balance} IC')
        for medal in self.medal_types:
            eval(f'self.{medal}Frame.hide()')

        self.startButton.clicked.connect(self.openRegistrationPage)
        self.anotherQuitGameButton.clicked.connect(self.quitGame)

        self.saveNameButton.clicked.connect(self.openFormMenu)
        self.nameEdit.textChanged.connect(self.setName)
        self.quitRegistrationPageButton.clicked.connect(self.openGreetingPage)

        self.firstClassButton.clicked.connect(self.setForm)
        self.secondClassButton.clicked.connect(self.setForm)

        self.startGameButton.clicked.connect(self.openGameMenu)
        self.shopButton.clicked.connect(self.openShop)
        self.quitGameButton.clicked.connect(self.quitGame)

        self.easyDifficultButton.clicked.connect(self.openGame)
        self.hardDifficultButton.clicked.connect(self.openGame)
        self.quitChooseDifficultPageButton.clicked.connect(self.openMainWindow)

        self.generateTaskButton.clicked.connect(self.generateTask)
        self.checkAnswerButton.clicked.connect(self.checkAnswer)

        self.quitMainGameButton.clicked.connect(self.openGameMenu)
        self.medalBuyButton.clicked.connect(self.addMedal)
        self.heartBuyButton.clicked.connect(self.addMedal)
        self.globusBuyButton.clicked.connect(self.addMedal)
        self.bookBuyButton.clicked.connect(self.addMedal)
        self.featherBuyButton.clicked.connect(self.addMedal)
        self.starBuyButton.clicked.connect(self.addMedal)
        self.medalBuyButton.clicked.connect(self.changeColor)
        self.heartBuyButton.clicked.connect(self.changeColor)
        self.globusBuyButton.clicked.connect(self.changeColor)
        self.bookBuyButton.clicked.connect(self.changeColor)
        self.featherBuyButton.clicked.connect(self.changeColor)
        self.starBuyButton.clicked.connect(self.changeColor)
        self.quitShopButton.clicked.connect(self.openMainWindow)

    def setName(self):
        self.name = self.nameEdit.text()
        self.emptyNameLabel.hide()

    def setForm(self):
        cur = self.con.cursor()
        if cur.execute(f'SELECT name, form, balance, medals FROM data WHERE name = "{self.name}"').fetchone():
            self.loadData()
        if self.sender().objectName() == 'firstClassButton':
            self.form = 1
        elif self.sender().objectName() == 'secondClassButton':
            self.form = 2
        self.pages.setCurrentWidget(self.mainMenuPage)

    def openRegistrationPage(self):
        self.pages.setCurrentWidget(self.registrationPage)

    def openMainWindow(self):
        self.pages.setCurrentWidget(self.mainMenuPage)

    def openFormMenu(self):
        if self.name:
            self.pages.setCurrentWidget(self.chooseClassPage)
            self.emptyNameLabel.hide()
        else:
            self.emptyNameLabel.show()

    def openGameMenu(self):
        self.pages.setCurrentWidget(self.chooseDifficultPage)

    def openGreetingPage(self):
        self.pages.setCurrentWidget(self.greetingPage)

    def openGame(self):
        self.pages.setCurrentWidget(self.gamePage)
        if self.sender() == self.easyDifficultButton:
            self.difficulty = 'easy'
        elif self.sender() == self.hardDifficultButton:
            self.difficulty = 'hard'

    def openShop(self):
        self.pages.setCurrentWidget(self.shopPage)

    def addMedal(self):
        price = int(self.sender().text()[9:])
        name = self.sender().objectName()[:-9]
        if self.balance >= price and self.sender().objectName()[:-9] not in self.medals:
            self.balance -= price
            self.balanceLabel.setText(f'{self.balance} IC')
            eval(f'self.{name}Frame.show()')
            self.medals.append(name)
            self.saveData(edited=True)

    def generateTask(self):
        self.currentTaskLabel.setStyleSheet('''
        border: 2px solid black;
        border-radius: 25px;
        background-color: rgb(255, 255, 255);
        ''')

        form = str(self.form)
        difficulty = self.difficulty
        names = rnd.sample(NAMES, 3)
        objects = rnd.sample(OBJECTS, 3)
        n1 = rnd.randint(1, 9)
        n2 = rnd.randint(1, 9)
        difference_under_10 = rnd.randint(1, 10 - min(n1, n2))

        tasks = {
            '1': {
                'easy': [
                    (f'''У {morph.parse(names[0])[0].inflect({"gent"}).word.capitalize()} есть {min(n1, n2)} {morph.parse(objects[0])[0].make_agree_with_number(min(n1, n2)).word}. {morph.parse(names[0])[0].inflect({"datv"}).word.capitalize()} дали еще {difference_under_10} штуки. Сколько стало {morph.parse(objects[0])[0].inflect({"plur", "gent"}).word} у {morph.parse(names[0])[0].inflect({"gent"}).word.capitalize()}?''',
                     min(n1, n2) + difference_under_10)]
            }
        }
        task = tasks['1']['easy'][0]
        self.currentTaskLabel.setText(task[0])
        self.answer = task[1]

    def checkAnswer(self):
        if self.answerSpinBox.value() == self.answer:
            self.currentTaskLabel.setStyleSheet('''
                        border: 2px solid rgb(0, 103, 0);
                        border-radius: 25px;
                        background-color: rgb(0, 255, 127);
                        ''')
        else:
            self.currentTaskLabel.setStyleSheet('''
                        border: 2px solid rgb(148, 0, 0);
                        border-radius: 25px;
                        background-color: rgb(255, 61, 61);
                        ''')

    def changeColor(self):
        for btn in self.buyButtons.buttons():
            if int(btn.text()[9:]) <= self.balance and btn.objectName()[:-9] not in self.medals:
                btn.setStyleSheet('QPushButton#' + btn.objectName() + '''{
                                        border-radius: 25px;
                                        background-color: rgb(255, 255, 127);
                                        border: 1px solid #000000;
                                        color: green;
                                    }
                                    QPushButton#''' + btn.objectName() + ''':hover{
                                        background-color: rgb(235, 235, 107)
                                    }''')
            else:
                btn.setStyleSheet('QPushButton#' + btn.objectName() + '''{
                                        border-radius: 25px;
                                        background-color: rgb(255, 255, 127);
                                        border: 1px solid #000000;
                                        color: red;
                                    }
                                    QPushButton#''' + btn.objectName() + ''':hover{
                                        background-color: rgb(235, 235, 107)
                                    }''')

    def saveData(self, edited=False):
        cur = self.con.cursor()

        if edited:
            cur.execute(f'''
                    UPDATE data
                    SET balance = {self.balance},
                    medals = "{'|'.join(self.medals) if self.medals else ''}",
                    form = {self.form if self.form else 0},
                    name = "{self.name if self.name else ''}"
                    WHERE name = "{self.name}"
                    ''')
        else:
            cur.execute(f'''
                    INSERT INTO data(balance, medals, form, name)
                    VALUES (
                    {self.balance},
                    "{'|'.join(self.medals) if self.medals else ''}",
                    {self.form if self.form else 0},
                    "{self.name if self.name else ''}"
                    )''')

        self.con.commit()

    def loadData(self):
        cur = self.con.cursor()
        data = cur.execute(f'SELECT name, form, balance, medals FROM data WHERE name = "{self.name}"').fetchone()
        self.name = data[0]
        self.form = data[1]
        self.balance = data[2]
        self.medals = data[3].split('|')
        self.changeColor()
        self.balanceLabel.setText(f'{self.balance} IC')
        for medal in self.medal_types:
            if medal in self.medals:
                eval(f'self.{medal}Frame.show()')
        self.changeColor()

    def quitGame(self):
        cur = self.con.cursor()
        if cur.execute(f'SELECT name, form, balance, medals FROM data WHERE name = "{self.name}"').fetchone():
            self.saveData(edited=True)
        else:
            self.saveData()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
