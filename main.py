import sys
import sqlite3
import random as rnd
from pymorphy3 import MorphAnalyzer

from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication, QDialog

morph = MorphAnalyzer()

OBJECTS = ['яблоко', 'банан', 'апельсин',
           'абрикос', 'слива', 'груша',
           'ананас', 'лимон', 'персик']

NAMES = ['Саша', 'Серёжа', 'Дима', 'Лёша', 'Максим',
         'Ваня', 'Артем', 'Миша', 'Кирилл', 'Егор',
         'Лена', 'Оля', 'Таня', 'Аня', 'Катя',
         'Маша', 'Даша', 'Настя', 'Юля']

PLACES = ['на столе', 'в тарелке', 'в ящике', 'в коробке', 'в миске', ]

SIMPLE = [2, 3, 5, 7, 11, 13, 17, 19, 23, 27, 29,
          31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
          73, 79, 83, 89, 97]


def is_not_simple(n):
    return n not in SIMPLE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.con = sqlite3.connect('kidData.sqlite')
        self.difficulty = 'easy'
        self.name = ''
        self.form = 1
        self.balance = 0
        self.medals = []
        self.medal_types = ['medal', 'heart', 'globus', 'book', 'feather', 'star']
        self.answer = 0
        self.initUI()

    def initUI(self):

        # Запуск интерфейса

        uic.loadUi('main.ui', self)
        self.changeColor()
        self.emptyNameLabel.hide()
        self.setFixedSize(1229, 789)
        self.pages.setCurrentWidget(self.greetingPage)
        self.balanceLabel.setText(f'{self.balance} IC')
        for medal in self.medal_types:
            eval(f'self.{medal}Frame.hide()')

        # Стартовое окно

        self.startButton.clicked.connect(self.openRegistrationPage)
        self.anotherQuitGameButton.clicked.connect(self.quitGame)

        # Ввод имени

        self.saveNameButton.clicked.connect(self.openFormMenu)
        self.nameEdit.textChanged.connect(self.setName)
        self.quitRegistrationPageButton.clicked.connect(self.openGreetingPage)

        # Ввод класса

        self.firstClassButton.clicked.connect(self.setForm)
        self.secondClassButton.clicked.connect(self.setForm)

        # Основное окно

        self.startGameButton.clicked.connect(self.openGameMenu)
        self.shopButton.clicked.connect(self.openShop)
        self.quitGameButton.clicked.connect(self.quitGame)
        self.quitMainGameButton.clicked.connect(self.openGameMenu)

        # Выбор сложности

        self.easyDifficultButton.clicked.connect(self.openGame)
        self.hardDifficultButton.clicked.connect(self.openGame)
        self.quitChooseDifficultPageButton.clicked.connect(self.openMainWindow)

        # Игровое окно

        self.generateTaskButton.clicked.connect(self.generateTask)
        self.checkAnswerButton.clicked.connect(self.checkAnswer)

        # Магазин

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

    def getDivisors(self, n):
        divisors = []
        for i in range(2, n):
            if n % i == 0:
                divisors.append(i)
        return divisors

    def setName(self):
        self.name = self.nameEdit.text().lower()
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
        names = list(rnd.sample(NAMES, 3))
        names_gent = list(map(lambda x: morph.parse(x)[0].inflect({"gent"}).word.capitalize(), names))
        names_datv = list(map(lambda x: morph.parse(x)[0].inflect({"datv"}).word.capitalize(), names))
        objects = rnd.sample(OBJECTS, 3)
        objects_plur = list(map(lambda x: morph.parse(x)[0].inflect({"plur"}).word, objects))
        objects_plur_gent = list(map(lambda x: morph.parse(x)[0].inflect({"plur", "gent"}).word, objects))
        nums1 = sorted([rnd.randint(1, 9), rnd.randint(1, 9)])
        nums2 = sorted([rnd.choice(list(filter(is_not_simple, range(2, 101)))),
                        rnd.choice(list(filter(is_not_simple, range(2, 101))))])

        # Числа для задач на остаток

        ost1 = rnd.randint(10, 100)
        ost2 = rnd.randint(4, ost1 - 3)
        ost3 = rnd.randint(1, ost1 - ost2 - 1)
        ost4 = ost1 - ost2 - ost3
        print(ost1, ost2, ost3, ost4)
        difference_under_100_1 = rnd.randint(1, 100 - nums2[0])
        difference_under_100_2 = rnd.choice(self.getDivisors(nums2[0]))
        difference_under_10 = rnd.randint(1, 10 - nums1[0])

        tasks = {
            '1': {
                'easy': [
                    (f'У {names_gent[0]} есть {nums1[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums1[0]).word}, {names_datv[0]} дали еще {difference_under_10}. Сколько стало {objects_plur_gent[0]} у {names_gent[0]}?',
                     nums1[0] + difference_under_10),
                    (f'У {names_gent[0]} есть {max(nums1[0], difference_under_10)} {morph.parse(objects[0])[0].make_agree_with_number(nums1[0]).word}, {names[0]} {"съел" if NAMES.index(names[0]) < 10 else "съела"} {min(nums1[0], difference_under_10)} {morph.parse(objects[0])[0].make_agree_with_number(difference_under_10).word}. Сколько стало {objects_plur_gent[0]} у {names_gent[0]}?',
                     abs(nums1[0] - difference_under_10)),
                    (f'У {names_gent[0]} {nums1[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums1[0]).word}, а у {names_gent[1]} {nums1[0] + difference_under_10} {morph.parse(objects[0])[0].make_agree_with_number(nums1[0] + difference_under_10).word}. На сколько у {names_gent[1]} {objects_plur_gent[0]} больше, чем у {names_gent[0]}?',
                     difference_under_10),
                    (f'У {names_gent[0]} {nums1[0] + difference_under_10} {morph.parse(objects[0])[0].make_agree_with_number(nums1[0] + difference_under_10).word}, а у {names_gent[1]} {nums1[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums1[0]).word}. На сколько у {names_gent[1]} {objects_plur_gent[0]} меньше, чем у {names_gent[0]}?',
                     difference_under_10)
                ],
                'hard': [
                    (f'У {names_gent[0]} есть {nums1[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums1[0]).word} и {objects_plur[1]}, причем {objects_plur_gent[1]} на {difference_under_10} больше, чем {objects_plur_gent[0]}. Сколько всего фруктов у {names_gent[0]}?',
                     nums1[0] * 2 + difference_under_10),
                    (f'У {names_gent[0]} есть {max(nums1[0], difference_under_10)} {morph.parse(objects[0])[0].make_agree_with_number(nums1[0]).word} и {objects_plur[1]}, причем {objects_plur_gent[1]} на {min(nums1[0], difference_under_10)} меньше, чем {objects_plur_gent[0]}. Сколько всего фруктов у {names_gent[0]}?',
                     max(nums1[0], difference_under_10) * 2 - min(nums1[0], difference_under_10))
                ]
            },
            '2': {
                'easy': [
                    (f'У {names_gent[0]} есть {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word}, {names_datv[0]} дали еще {difference_under_100_1}. Сколько стало {objects_plur_gent[0]} у {names_gent[0]}?',
                     nums2[0] + difference_under_100_1),
                    (f'У {names_gent[0]} есть {max(nums2[0], difference_under_100_1)} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word}, {names[0]} {"съел" if NAMES.index(names[0]) < 10 else "съела"} {min(nums2[0], difference_under_100_1)} {morph.parse(objects[0])[0].make_agree_with_number(difference_under_100_1).word}. Сколько стало {objects_plur_gent[0]} у {names_gent[0]}?',
                     abs(nums2[0] - difference_under_100_1)),
                    (f'У {names_gent[0]} {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word}, а у {names_gent[1]} {nums2[0] + difference_under_100_1} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0] + difference_under_100_1).word}. На сколько у {names_gent[1]} {objects_plur_gent[0]} больше, чем у {names_gent[0]}?',
                     difference_under_100_1),
                    (f'У {names_gent[0]} {nums2[0] + difference_under_100_1} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0] + difference_under_100_1).word}, а у {names_gent[1]} {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word}. На сколько у {names_gent[1]} {objects_plur_gent[0]} меньше, чем у {names_gent[0]}?',
                     difference_under_100_1),
                    (f'У {names_gent[0]} есть {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word}, а у {names_gent[1]} - в {difference_under_100_2} {"раза" if int(str(difference_under_100_2)[-1]) in range(1, 5) and int(str(difference_under_100_2)[0]) != 1 else "раз"} меньше. Сколько {objects_plur_gent[0]} у {names_gent[1]}?',
                     nums2[0] // difference_under_100_2),
                    (f'У {names_gent[0]} есть {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word}, а у {names_gent[1]} - в {difference_under_100_2} {"раза" if int(str(nums2[0])[-1]) in range(1, 5) and int(str(nums2[0])[0]) != 1 else "раз"} больше. Сколько {objects_plur_gent[0]} у {names_gent[1]}?',
                     nums2[0] * difference_under_100_2),
                    (f'У {names_gent[0]} есть {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word}, а у {names_gent[1]} - {nums2[0] * difference_under_100_2 if nums2[0] * difference_under_100_2 <= 100 else nums2[0] * self.getDivisors(nums2[0])[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0] * difference_under_100_2 if nums2[0] * difference_under_100_2 <= 100 else nums2[0] * self.getDivisors(nums2[0])[0]).word}. Во сколько у {names_gent[1]} {objects_plur_gent[0]} больше, чем у {names_gent[0]}?',
                     (nums2[0] * difference_under_100_2 if nums2[0] * difference_under_100_2 <= 100 else nums2[0] * self.getDivisors(nums2[0])[0]) // nums2[0]),
                    (f'У {names_gent[0]} есть {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word}, а у {names_gent[1]} - {nums2[0] // difference_under_100_2} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0] // difference_under_100_2).word}. Во сколько у {names_gent[1]} {objects_plur_gent[0]} меньше, чем у {names_gent[0]}?',
                     difference_under_100_2)
                ],
                'hard': [
                    (f'У {names_gent[0]} есть {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word} и {morph.parse(objects[1])[0].inflect({"plur"}).word}, причем {objects_plur_gent[1]} на {difference_under_100_1} больше, чем {objects_plur_gent[0]}. Сколько всего фруктов у {names_gent[0]}?',
                     nums2[0] * 2 + difference_under_100_1),
                    (f'У {names_gent[0]} есть {max(nums2[0], difference_under_100_1)} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word} и {morph.parse(objects[1])[0].inflect({"plur"}).word}, причем {objects_plur_gent[1]} на {min(nums2[0], difference_under_100_1)} меньше, чем {objects_plur_gent[0]}. Сколько всего фруктов у {names_gent[0]}?',
                     max(nums2[0], difference_under_100_1) * 2 - min(nums2[0], difference_under_100_1)),
                    (f'У {names_gent[0]} есть {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word} и {morph.parse(objects[1])[0].inflect({"plur"}).word}, причем {objects_plur_gent[1]} в {difference_under_100_2 if difference_under_100_2 <= 10 else self.getDivisors(nums2[0])[0]} {"раза" if int(str(nums2[0])[-1]) in range(1, 5) and int(str(nums2[0])[0]) != 1 else "раз"} больше, чем {objects_plur_gent[0]}. Сколько всего фруктов у {names_gent[0]}?',
                     nums2[0] * (difference_under_100_2 + 1)),
                    (f'У {names_gent[0]} есть {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word} и {morph.parse(objects[1])[0].inflect({"plur"}).word}, причем {objects_plur_gent[1]} в {difference_under_100_2} {"раза" if int(str(nums2[0])[-1]) in range(1, 5) and int(str(nums2[0])[0]) != 1 else "раз"} меньше, чем {objects_plur_gent[0]}. Сколько всего фруктов у {names_gent[0]}?',
                     nums2[0] * (difference_under_100_2 + 1) // difference_under_100_2),
                    (f'У {names_gent[0]} есть {ost1} {morph.parse("фрукт")[0].make_agree_with_number(ost1).word}: {ost2} {morph.parse(objects[0])[0].make_agree_with_number(ost2).word}, {ost3} {morph.parse(objects[1])[0].make_agree_with_number(ost3).word} и {objects_plur[2]}. Сколько {objects_plur_gent[2]} у {names_gent[0]}?',
                     ost4),
                    (f'У {names_gent[0]} есть {ost2} {morph.parse(objects[0])[0].make_agree_with_number(ost2).word}, {objects_plur[1]} и {objects_plur[2]}, причем {objects_plur_gent[1]} на {abs(ost2 - ost3)} меньше, чем {objects_plur_gent[0]}, а {objects_plur_gent[2]} на {abs(ost3 - ost4)} меньше, чем {objects_plur_gent[1]}. Сколько всего фруктов у {names_gent[0]}?',
                     ost2 + (ost2 - abs(ost2 + ost3)) + (ost2 - abs(ost2 + ost3) - abs(ost3 - ost4))),
                    (f'У {names_gent[0]} есть {ost2} {morph.parse(objects[0])[0].make_agree_with_number(ost2).word}, {objects_plur[1]} и {objects_plur[2]}, причем {objects_plur_gent[1]} на {abs(ost2 - ost3)} меньше, чем {objects_plur_gent[0]}, а {objects_plur_gent[2]} на {abs(ost3 - ost4)} меньше, чем {objects_plur_gent[1]}. Сколько {objects_plur_gent[2]} у {names_gent[0]}?',
                     ost2 + abs(ost2 - ost3) + abs(ost3 - ost4)),
                    (f'У {names_gent[0]} есть {ost2} {morph.parse(objects[0])[0].make_agree_with_number(ost2).word}, {objects_plur[1]} и {objects_plur[2]}, причем {objects_plur_gent[1]} на {abs(ost2 - ost3) if abs(ost2 - ost3) <= 20 else abs(ost2 - ost3) - 20} больше, чем {objects_plur_gent[0]}, а {objects_plur_gent[2]} на {abs(ost3 - ost4)} больше, чем {objects_plur_gent[1]}. Сколько всего фруктов у {names_gent[0]}?',
                     ost2 * 3 + (abs(ost2 - ost3) if abs(ost2 - ost3) <= 20 else abs(ost2 - ost3) - 20) * 2 + abs(ost3 - ost4)),
                    (f'У {names_gent[0]} есть {ost2} {morph.parse(objects[0])[0].make_agree_with_number(ost2).word}, {objects_plur[1]} и {objects_plur[2]}, причем {objects_plur_gent[1]} на {abs(ost2 - ost3)} больше, чем {objects_plur_gent[0]}, а {objects_plur_gent[2]} на {abs(ost3 - ost4)} больше, чем {objects_plur_gent[1]}. Сколько {objects_plur_gent[2]} у {names_gent[0]}?',
                     ost2 - abs(ost2 - ost3) - abs(ost3 - ost4))
                ]
            }
        }
        task = tasks[form][difficulty][rnd.randint(0, len(tasks[form][difficulty]) - 1)]
        self.currentTaskLabel.setText(task[0])
        self.answer = task[1]

    def checkAnswer(self):
        if self.answerSpinBox.value() == self.answer:
            if self.difficulty == 'hard':
                self.balance += 20
                Dialog(20).exec()
            else:
                self.balance += 10
                Dialog(10).exec()
            self.currentTaskLabel.setText('')
            self.balanceLabel.setText(f'{self.balance} KC')

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
                    WHERE name = "{self.name.lower()}"
                    ''')
        else:
            cur.execute(f'''
                    INSERT INTO data(balance, medals, form, name)
                    VALUES (
                    {self.balance},
                    "{'|'.join(self.medals) if self.medals else ''}",
                    {self.form if self.form else 0},
                    "{self.name.lower() if self.name else ''}"
                    )''')

        self.con.commit()

    def loadData(self):
        cur = self.con.cursor()
        data = cur.execute(f'SELECT name, form, balance, medals FROM data WHERE name = "{self.name.lower()}"').fetchone()
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


class Dialog(QDialog):
    def __init__(self, reward):
        super().__init__()
        uic.loadUi('dialog.ui', self)
        self.reward = reward

        self.acceptButton.clicked.connect(self.acceptButtonClicked)
        self.label.setText(f'Молодец! Ты правильно решил задачу. Ты получаешь {self.reward} монет!')

    def acceptButtonClicked(self):
        self.close()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
