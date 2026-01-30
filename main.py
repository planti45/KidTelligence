import sys
import sqlite3
import random as rnd
import pymorphy3
import textwrap
from enum import Enum

import pygame

from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication, QDialog
from PyQt6.QtCore import Qt, QTimer

morph = pymorphy3.MorphAnalyzer()

OBJECTS = ['яблоко', 'банан', 'апельсин',
           'абрикос', 'слива', 'груша',
           'ананас', 'лимон', 'персик']

NAMES = ['Саша', 'Серёжа', 'Дима', 'Лёша', 'Максим',
         'Ваня', 'Артем', 'Миша', 'Кирилл', 'Егор',
         'Лена', 'Оля', 'Таня', 'Аня', 'Катя',
         'Маша', 'Даша', 'Настя', 'Юля']

SIMPLE = [2, 3, 5, 7, 11, 13, 17, 19, 23, 27, 29,
          31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
          73, 79, 83, 89, 97]

MEDALS = ['medal', 'heart', 'globus', 'book', 'feather', 'star']


def is_not_simple(n):
    return n not in SIMPLE


class Sound(Enum):
    CORRECT_ANSWER_SOUND = 0
    INCORRECT_ANSWER_SOUND = 1


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
        self.task_history = []
        self.current_task_index = 0
        self.is_logged = False
        self.initUI()

    def initUI(self):

        # Запуск интерфейса

        uic.loadUi('ui/main.ui', self)
        self.setFixedSize(2112, 1413)
        self.changeColor()
        self.mainPages.setCurrentWidget(self.greetPage)
        self.pages.setCurrentWidget(self.gamePage)
        self.pages.hide()
        self.balanceLabel.setText(
            f'{self.balance} {morph.parse("очко")[0].make_agree_with_number(self.balance).word}')
        for medal in self.medal_types:
            eval(f'self.{medal}Frame.hide()')

        # Титульная страница

        self.startButton.clicked.connect(self.startGame)

        # Регистрация

        self.firstFormRadioButton.toggled.connect(self.setForm)
        self.secondFormRadioButton.toggled.connect(self.setForm)
        self.saveButton.clicked.connect(self.register)
        self.registerLabel.show()

        # Главное меню

        for btn in self.addedMenuButtons.buttons():
            btn.hide()

        self.goToMainGameButton.clicked.connect(self.openGameMenu)
        self.goToShopButton.clicked.connect(self.openShop)
        self.goToHelpButton.clicked.connect(self.openTutorial)
        self.leaveGameButton.clicked.connect(self.quitGame)

        # Страница магазина

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

        # Выбор сложности

        self.easyDifficultButton.clicked.connect(self.openGame)
        self.hardDifficultButton.clicked.connect(self.openGame)

        # Страница с задачей

        self.anotherGenerateTaskButton.clicked.connect(self.generateTask)
        self.checkAnswerButton.clicked.connect(self.checkAnswer)
        self.undoButton.clicked.connect(self.undoTask)
        self.redoButton.clicked.connect(self.redoTask)
        self.answerSpinBox.setSpecialValueText(' ')
        self.clearAnswerSpinBox()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_0:
            self.answerSpinBox.setValue(int(f'{self.answerSpinBox.value()}0'))
        if event.key() == Qt.Key.Key_1:
            self.answerSpinBox.setValue(int(f'{self.answerSpinBox.value()}1'))
        if event.key() == Qt.Key.Key_2:
            self.answerSpinBox.setValue(int(f'{self.answerSpinBox.value()}2'))
        if event.key() == Qt.Key.Key_3:
            self.answerSpinBox.setValue(int(f'{self.answerSpinBox.value()}3'))
        if event.key() == Qt.Key.Key_4:
            self.answerSpinBox.setValue(int(f'{self.answerSpinBox.value()}4'))
        if event.key() == Qt.Key.Key_5:
            self.answerSpinBox.setValue(int(f'{self.answerSpinBox.value()}5'))
        if event.key() == Qt.Key.Key_6:
            self.answerSpinBox.setValue(int(f'{self.answerSpinBox.value()}6'))
        if event.key() == Qt.Key.Key_7:
            self.answerSpinBox.setValue(int(f'{self.answerSpinBox.value()}7'))
        if event.key() == Qt.Key.Key_8:
            self.answerSpinBox.setValue(int(f'{self.answerSpinBox.value()}8'))
        if event.key() == Qt.Key.Key_9:
            self.answerSpinBox.setValue(int(f'{self.answerSpinBox.value()}9'))
        if event.key() == Qt.Key.Key_Backspace:
            if len(str(self.answerSpinBox.value())) > 1:
                self.answerSpinBox.setValue(int(f'{self.answerSpinBox.value()}'[:-1]))
            elif len(str(self.answerSpinBox.value())) == 1:
                self.answerSpinBox.setValue(0)
            else:
                pass
        if event.key() == Qt.Key.Key_Enter:
            self.checkAnswer()

    def getDivisors(self, n):
        divisors = []
        for i in range(2, n):
            if n % i == 0:
                divisors.append(i)
        return divisors

    def setName(self):
        self.name = self.nameEdit.text().lower()

    def setForm(self):
        if self.firstFormRadioButton.isChecked():
            self.form = 1
        elif self.secondFormRadioButton.isChecked():
            self.form = 2

    def reset(self):
        self.balance = 1000
        self.medals = []
        self.difficulty = 'easy'

    def register(self):
        cur = self.con.cursor()
        if self.name:
            if cur.execute(f'SELECT name, form, balance, medals FROM data WHERE name = "{self.name}"').fetchone():
                self.saveData(edited=True)
            else:
                self.saveData()
        self.reset()
        print(self.medals)
        for medal in self.medal_types:
            if medal in self.medals:
                eval(f'self.{medal}Frame.show()')
            else:
                eval(f'self.{medal}Frame.hide()')
        self.changeColor()

        self.setForm()
        self.setName()

        if not cur.execute(f'SELECT name, form, balance, medals FROM data WHERE name = "{self.name}"').fetchone():
            self.saveData()
        self.loadData()

        self.registerLabel.hide()

        self.anotherGenerateTaskButton.setText('Нажми на стрелку справа чтобы появилась новая задача')
        self.changeColor()
        self.openGameMenu()

        for btn in self.addedMenuButtons.buttons():
            btn.show()

    def startGame(self):
        self.openGameMenu()
        self.mainPages.setCurrentWidget(self.mainPage)

    def resetMenuButtons(self):
        self.goToMainGameButton.setStyleSheet('''
        QPushButton#goToMainGameButton {
            background-color: rgb(255, 253, 167);
            border: 2px solid black;
            border-radius: 25px;
            color: black;
            }
            QPushButton#goToMainGameButton:hover {
            background-color: rgb(225, 223, 137)
            }
        ''')

        self.goToShopButton.setStyleSheet('''
        QPushButton#goToShopButton {
            background-color: rgb(255, 253, 167);
            border: 2px solid black;
            border-radius: 25px;
            color: black;
            }
            QPushButton#goToShopButton:hover {
            background-color: rgb(225, 223, 137)
            }
        ''')

        self.goToHelpButton.setStyleSheet('''
        QPushButton#goToHelpButton {
            background-color: rgb(255, 253, 167);
            border: 2px solid black;
            border-radius: 25px;
            color: black;
            }
            QPushButton#goToHelpButton:hover {
            background-color: rgb(225, 223, 137)
            }
        ''')

    def openGameMenu(self):
        self.pages.setCurrentWidget(self.chooseDifficultPage)

        self.resetMenuButtons()
        self.goToMainGameButton.setStyleSheet('''
                        QPushButton#goToMainGameButton {
                            background-color: rgb(158, 255, 181);
                            border: 2px solid black;
                            border-radius: 25px;
                            color: black;
                            }
                            QPushButton#goToMainGameButton:hover {
                            background-color: rgb(128, 225, 151)
                            }
                        ''')

    def openGame(self):
        self.pages.setCurrentWidget(self.gamePage)
        self.is_signed = False
        if self.sender() == self.easyDifficultButton:
            self.difficulty = 'easy'
        elif self.sender() == self.hardDifficultButton:
            self.difficulty = 'hard'
        self.anotherGenerateTaskButton.setText('Нажми на стрелку справа чтобы появилась новая задача')

    def openTutorial(self):
        self.resetMenuButtons()
        self.goToHelpButton.setStyleSheet('''
        QPushButton#goToHelpButton {
            background-color: rgb(158, 255, 181);
            border: 2px solid black;
            border-radius: 25px;
            color: black;
            }
            QPushButton#goToHelpButton:hover {
            background-color: rgb(128, 225, 151)
            }
        ''')

        TutorialDialog().exec()

    def openShop(self):
        self.resetMenuButtons()
        self.goToShopButton.setStyleSheet('''
                QPushButton#goToShopButton {
                    background-color: rgb(158, 255, 181);
                    border: 2px solid black;
                    border-radius: 25px;
                    color: black;
                    }
                    QPushButton#goToShopButton:hover {
                    background-color: rgb(128, 225, 151)
                    }
                ''')

        self.pages.setCurrentWidget(self.shopPage)

    def addMedal(self):
        name = self.sender().objectName()[:-9]
        if name in self.medals:
            return
        elif self.balance >= int(self.sender().text().split()[0]) and name not in self.medals:
            self.balance -= int(self.sender().text().split()[0])
            self.balanceLabel.setText(
                f'{self.balance} {morph.parse("очко")[0].make_agree_with_number(self.balance).word}')
            eval(f'self.{name}Frame.show()')
            self.medals.append(name)
            self.saveData(edited=True)

            if name in ['medal', 'heart', 'globus']:
                self.leftBackgroundFrame.show()
            else:
                self.rightBackgroundFrame.show()

        self.changeColor()

    def generateTask(self):
        self.checkAnswerButton.clicked.disconnect()
        self.checkAnswerButton.clicked.connect(self.checkAnswer)
        self.checkAnswerButton.setText('Проверить')

        self.currentTaskLabel.setStyleSheet('''
        border: 2px solid black;
        border-radius: 25px;
        background-color: rgb(255, 255, 255);
        color: #000000;
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
        multer1 = rnd.randint(2, 4)

        # Числа для задач на остаток

        ost1 = rnd.randint(10, 100)
        ost2 = rnd.randint(4, ost1 - 3)
        ost3 = rnd.randint(1, ost1 - ost2 - 1)
        ost4 = ost1 - ost2 - ost3
        difference_under_100_1 = rnd.randint(1, 100 - nums2[0])
        difference_under_100_2 = rnd.choice(self.getDivisors(nums2[0]))
        difference_under_10 = rnd.randint(1, 10 - nums1[0])
        nums3 = sorted([rnd.randint(5, 101), rnd.randint(5, 101), rnd.randint(5, 101)], reverse=True)

        tasks = {
            '1': {
                'easy': [
                    (f'У {names_gent[0]} есть {nums1[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums1[0]).word}, {names_datv[0]} дали еще {difference_under_10}.',
                     nums1[0] + difference_under_10, f'Сколько стало {objects_plur_gent[0]} у {names_gent[0]}?'),
                    (f'У {names_gent[0]} есть {max(nums1[0], difference_under_10)} {morph.parse(objects[0])[0].make_agree_with_number(max(nums1[0], difference_under_10)).word}, {names[0]} {"съел" if NAMES.index(names[0]) < 10 else "съела"} {min(nums1[0], difference_under_10)} {morph.parse(objects[0])[0].make_agree_with_number(min(nums1[0], difference_under_10)).word}.',
                     abs(nums1[0] - difference_under_10), f'Сколько стало {objects_plur_gent[0]} у {names_gent[0]}?'),
                    (f'У {names_gent[0]} {nums1[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums1[0]).word}, а у {names_gent[1]} {nums1[0] + difference_under_10} {morph.parse(objects[0])[0].make_agree_with_number(nums1[0] + difference_under_10).word}.',
                     difference_under_10,
                     f'На сколько у {names_gent[1]} {objects_plur_gent[0]} больше, чем у {names_gent[0]}?'),
                    (f'У {names_gent[0]} {nums1[0] + difference_under_10} {morph.parse(objects[0])[0].make_agree_with_number(nums1[0] + difference_under_10).word}, а у {names_gent[1]} {nums1[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums1[0]).word}.',
                     difference_under_10,
                     f'На сколько у {names_gent[1]} {objects_plur_gent[0]} меньше, чем у {names_gent[0]}?')
                ],
                'hard': [
                    (f'У {names_gent[0]} есть {nums1[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums1[0]).word} и {objects_plur[1]}, причем {objects_plur_gent[1]} на {difference_under_10} больше, чем {objects_plur_gent[0]}.',
                     nums1[0] * 2 + difference_under_10, f'Сколько всего фруктов у {names_gent[0]}?'),
                    (f'У {names_gent[0]} есть {max(nums1[0], difference_under_10)} {morph.parse(objects[0])[0].make_agree_with_number(max(nums1[0], difference_under_10)).word} и {objects_plur[1]}, причем {objects_plur_gent[1]} на {min(nums1[0], difference_under_10)} меньше, чем {objects_plur_gent[0]}.',
                     max(nums1[0], difference_under_10) * 2 - min(nums1[0], difference_under_10),
                     f'Сколько всего фруктов у {names_gent[0]}?')
                ]
            },
            '2': {
                'easy': [
                    (f'У {names_gent[0]} есть {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word}, {names_datv[0]} дали еще {difference_under_100_1}.',
                     nums2[0] + difference_under_100_1, f'Сколько стало {objects_plur_gent[0]} у {names_gent[0]}?'),
                    (f'У {names_gent[0]} есть {max(nums2[0], difference_under_100_1)} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word}, {names[0]} {"съел" if NAMES.index(names[0]) < 10 else "съела"} {min(nums2[0], difference_under_100_1)} {morph.parse(objects[0])[0].make_agree_with_number(difference_under_100_1).word}.',
                     abs(nums2[0] - difference_under_100_1),
                     f'Сколько стало {objects_plur_gent[0]} у {names_gent[0]}?'),
                    (f'У {names_gent[0]} {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word}, а у {names_gent[1]} {nums2[0] + difference_under_100_1} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0] + difference_under_100_1).word}.',
                     difference_under_100_1,
                     f'На сколько у {names_gent[1]} {objects_plur_gent[0]} больше, чем у {names_gent[0]}?'),
                    (f'У {names_gent[0]} {nums2[0] + difference_under_100_1} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0] + difference_under_100_1).word}, а у {names_gent[1]} {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word}.',
                     difference_under_100_1,
                     f'На сколько у {names_gent[1]} {objects_plur_gent[0]} меньше, чем у {names_gent[0]}?'),
                    (f'У {names_gent[0]} есть {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word}, а у {names_gent[1]} - в {difference_under_100_2} {"раза" if int(str(difference_under_100_2)[-1]) in range(1, 5) and int(str(difference_under_100_2)[0]) != 1 else "раз"} меньше.',
                     nums2[0] // difference_under_100_2, f'Сколько {objects_plur_gent[0]} у {names_gent[1]}?'),
                    (f'У {names_gent[0]} есть {nums2[0] if nums2[0] <= 20 else nums2[0] - 20} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0] if nums2[0] <= 20 else nums2[0] - 20).word}, а у {names_gent[1]} - в {multer1} раза больше.',
                     (nums2[0] if nums2[0] <= 20 else nums2[0] - 20) * multer1,
                     f'Сколько {objects_plur_gent[0]} у {names_gent[1]}?'),
                    (f'У {names_gent[0]} есть {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word}, а у {names_gent[1]} – {nums2[0] * difference_under_100_2 if nums2[0] * difference_under_100_2 <= 100 else nums2[0] * self.getDivisors(nums2[0])[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0] * difference_under_100_2 if nums2[0] * difference_under_100_2 <= 100 else nums2[0] * self.getDivisors(nums2[0])[0]).word}.',
                     (nums2[0] * difference_under_100_2 if nums2[0] * difference_under_100_2 <= 100 else nums2[0] *
                                                                                                         self.getDivisors(
                                                                                                             nums2[0])[
                                                                                                             0]) //
                     nums2[0], f'Во сколько у {names_gent[1]} {objects_plur_gent[0]} больше, чем у {names_gent[0]}?'),
                    (f'У {names_gent[0]} есть {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word}, а у {names_gent[1]} – {nums2[0] // difference_under_100_2} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0] // difference_under_100_2).word}.',
                     difference_under_100_2,
                     f'Во сколько раз у {names_gent[1]} {objects_plur_gent[0]} меньше, чем у {names_gent[0]}?')
                ],
                'hard': [
                    (f'У {names_gent[0]} есть {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word} и {morph.parse(objects[1])[0].inflect({"plur"}).word}, причем {objects_plur_gent[1]} на {difference_under_100_1} больше, чем {objects_plur_gent[0]}.',
                     nums2[0] * 2 + difference_under_100_1, f'Сколько всего фруктов у {names_gent[0]}?'),
                    (f'У {names_gent[0]} есть {max(nums2[0], difference_under_100_1)} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word} и {morph.parse(objects[1])[0].inflect({"plur"}).word}, причем {objects_plur_gent[1]} на {min(nums2[0], difference_under_100_1)} меньше, чем {objects_plur_gent[0]}.',
                     max(nums2[0], difference_under_100_1) * 2 - min(nums2[0], difference_under_100_1),
                     f'Сколько всего фруктов у {names_gent[0]}?'),
                    (f'У {names_gent[0]} есть {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word} и {morph.parse(objects[1])[0].inflect({"plur"}).word}, причем {objects_plur_gent[1]} в {difference_under_100_2 if difference_under_100_2 <= 10 else self.getDivisors(nums2[0])[0]} {"раза" if int(str(nums2[0])[-1]) in range(1, 5) and int(str(nums2[0])[0]) != 1 else "раз"} больше, чем {objects_plur_gent[0]}.',
                     nums2[0] * (
                         difference_under_100_2 if difference_under_100_2 <= 10 else self.getDivisors(nums2[0])[0] + 1),
                     f'Сколько всего фруктов у {names_gent[0]}?'),
                    (f'У {names_gent[0]} есть {nums2[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums2[0]).word} и {morph.parse(objects[1])[0].inflect({"plur"}).word}, причем {objects_plur_gent[1]} в {difference_under_100_2} {"раза" if int(str(nums2[0])[-1]) in range(1, 5) and int(str(nums2[0])[0]) != 1 else "раз"} меньше, чем {objects_plur_gent[0]}.',
                     nums2[0] * (difference_under_100_2 + 1) // difference_under_100_2,
                     f'Сколько всего фруктов у {names_gent[0]}?'),
                    (f'У {names_gent[0]} есть {ost1} {morph.parse("фрукт")[0].make_agree_with_number(ost1).word}: {ost2} {morph.parse(objects[0])[0].make_agree_with_number(ost2).word}, {ost3} {morph.parse(objects[1])[0].make_agree_with_number(ost3).word} и {objects_plur[2]}.',
                     ost4, f'Сколько {objects_plur_gent[2]} у {names_gent[0]}?'),
                    (f'У {names_gent[0]} есть {nums3[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums3[0]).word}, {objects_plur[1]} и {objects_plur[2]}, причем {objects_plur_gent[1]} на {nums3[0] - nums3[1]} меньше, чем {objects_plur_gent[0]}, а {objects_plur_gent[2]} на {nums3[1] - nums3[2]} меньше, чем {objects_plur_gent[1]}.',
                     sum(nums3), f'Сколько всего фруктов у {names_gent[0]}?'),
                    (f'У {names_gent[0]} есть {nums3[0]} {morph.parse(objects[0])[0].make_agree_with_number(nums3[0]).word}, {objects_plur[1]} и {objects_plur[2]}, причем {objects_plur_gent[1]} на {nums3[0] - nums3[1]} меньше, чем {objects_plur_gent[0]}, а {objects_plur_gent[2]} на {nums3[1] - nums3[2]} меньше, чем {objects_plur_gent[1]}.',
                     nums3[2], f'Сколько {objects_plur_gent[2]} у {names_gent[0]}?'),
                    (f'У {names_gent[0]} есть {ost2} {morph.parse(objects[0])[0].make_agree_with_number(ost2).word}, {objects_plur[1]} и {objects_plur[2]}, причем {objects_plur_gent[1]} на {abs(ost2 - ost3) if abs(ost2 - ost3) <= 20 else abs(ost2 - ost3) - 20} больше, чем {objects_plur_gent[0]}, а {objects_plur_gent[2]} на {abs(ost3 - ost4)} больше, чем {objects_plur_gent[1]}.',
                     ost2 * 3 + (abs(ost2 - ost3) if abs(ost2 - ost3) <= 20 else abs(ost2 - ost3) - 20) * 2 + abs(
                         ost3 - ost4), f'Сколько всего фруктов у {names_gent[0]}?'),
                    (f'У {names_gent[0]} есть {ost2} {morph.parse(objects[0])[0].make_agree_with_number(ost2).word}, {objects_plur[1]} и {objects_plur[2]}, причем {objects_plur_gent[1]} на {abs(ost2 - ost3)} больше, чем {objects_plur_gent[0]}, а {objects_plur_gent[2]} на {abs(ost3 - ost4)} больше, чем {objects_plur_gent[1]}.',
                     ost2 + abs(ost2 - ost3) + abs(ost3 - ost4), f'Сколько {objects_plur_gent[2]} у {names_gent[0]}?')
                ]
            }
        }
        task = tasks[form][difficulty][rnd.randint(0, len(tasks[form][difficulty]) - 1)]
        task = (task[0], task[1], task[2])
        self.setTask(task)
        if len(self.task_history) < 10:
            self.task_history.append(task)
            self.current_task_index = len(self.task_history) - 1
        else:
            self.task_history.pop(0)
            self.task_history.append(task)
            self.current_task_index = 9

    def undoTask(self):
        if self.current_task_index > 0:
            self.current_task_index -= 1
            self.setTask(self.task_history[self.current_task_index])
            self.checkAnswerButton.clicked.disconnect()
            self.checkAnswerButton.clicked.connect(self.checkAnswer)
        else:
            pass

    def redoTask(self):
        if self.current_task_index == len(
                self.task_history) - 1 or not self.task_history or self.anotherGenerateTaskButton.text() == 'Нажми на стрелку справа чтобы появилась новая задача':
            self.generateTask()
        if self.current_task_index < len(self.task_history) - 1:
            self.current_task_index += 1
            self.setTask(self.task_history[self.current_task_index])

    def setTask(self, task):
        ex_text = '\n'.join(list(map(lambda x: x.ljust(50), textwrap.wrap(task[0], 50))))
        self.anotherGenerateTaskButton.setText(ex_text)
        qu_text = '\n'.join(list(map(lambda x: x.ljust(35), textwrap.wrap(task[2], 35))))
        self.currentQuestionLabel.setText(qu_text)
        self.answer = task[1]

    def resetGame(self):
        self.answerSpinBox.setValue(0)
        self.anotherGenerateTaskButton.setText('Нажми на стрелку справа чтобы появилась новая задача')
        self.answerSpinBox.cleanText()
        self.currentQuestionLabel.clear()

    def clearAnswerSpinBox(self):
        if self.answerSpinBox.value() == 0:
            self.answerSpinBox.clear()

    def playAudio(self, audio):
        pygame.mixer.init()
        if audio == Sound.CORRECT_ANSWER_SOUND:
            pygame.mixer.music.load("audios/correct answer sound.mp3")
        elif audio == Sound.INCORRECT_ANSWER_SOUND:
            pygame.mixer.music.load("audios/incorrect answer.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.quit()

    def checkAnswer(self):
        if self.answerSpinBox.value() == self.answer:
            self.playAudio(Sound.CORRECT_ANSWER_SOUND)
            if self.difficulty == 'hard':
                self.balance += 20
                Dialog(20).exec()
                self.changeColor()
            else:
                self.balance += 10
                Dialog(10).exec()
                self.changeColor()
            self.resetGame()
            self.balanceLabel.setText(
                f'{self.balance} {morph.parse("очко")[0].make_agree_with_number(self.balance).word}')
            self.changeColor()
            if len(self.task_history) < 10:
                self.current_task_index += 1
            else:
                self.task_history.pop(0)
                self.current_task_index = 9

        else:
            self.playAudio(Sound.INCORRECT_ANSWER_SOUND)
            Dialog(10, False).exec()

    def changeColor(self):
        for btn in self.buyButtons.buttons():
            if btn.objectName()[:-9] in self.medals:
                btn.setStyleSheet('QPushButton#' + btn.objectName() + '''{
                                                        border-radius: 25px;
                                                        background-color: rgb(255, 255, 127);
                                                        border: 1px solid #000000;
                                                        color: red;
                                                    }
                                                    QPushButton#''' + btn.objectName() + ''':hover{
                                                        background-color: rgb(235, 235, 107)
                                                    }''')
                btn.setText('Уже есть')
            else:
                if MEDALS.index(btn.objectName()[:-9]) != 5:
                    btn.setText(f'{(MEDALS.index(btn.objectName()[:-9]) + 1) * 100} очков')
                else:
                    btn.setText('1000 очков')
                if btn.text() != 'Уже есть':
                    if int(btn.text().split()[0]) <= self.balance and btn.objectName()[:-9] not in self.medals:
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
        self.changeColor()

    def loadData(self):
        self.registerLabel.hide()
        self.pages.show()

        cur = self.con.cursor()
        data = cur.execute(
            f'SELECT name, form, balance, medals FROM data WHERE name = "{self.name.lower()}"').fetchone()
        self.name = data[0]
        self.form = data[1]
        self.balance = data[2]
        self.medals = data[3].split('|')
        self.changeColor()
        self.balanceLabel.setText(
            f'{self.balance} {morph.parse("очко")[0].make_agree_with_number(self.balance).word}')
        for medal in self.medal_types:
            if medal in self.medals:
                eval(f'self.{medal}Frame.show()')
            else:
                eval(f'self.{medal}Frame.hide()')
        self.changeColor()

    def quitGame(self):
        cur = self.con.cursor()
        if cur.execute(f'SELECT name, form, balance, medals FROM data WHERE name = "{self.name}"').fetchone():
            self.saveData(edited=True)
        else:
            self.saveData()
        self.close()

    def closeEvent(self, event):
        self.quitGame()


class Dialog(QDialog):
    def __init__(self, reward=10, is_correct=True):
        super().__init__()
        uic.loadUi('ui/dialog.ui', self)

        self.smileEmoji.hide()
        self.froudEmoji.hide()

        self.reward = reward
        self.is_correct = is_correct

        self.acceptButton.clicked.connect(self.acceptButtonClicked)

        if self.is_correct:
            self.smileEmoji.show()
            self.setWindowTitle('Молодец!')
            self.setStyleSheet('''QDialog#Dialog {
            background-color: rgb(170, 255, 127);
            }''')
            self.label.setText(f'Молодец! Ты правильно решил задачу. Ты получаешь {self.reward} очков!')
            self.label.setStyleSheet('color: rgb(0, 71, 0)')
            self.acceptButton.setStyleSheet(
                '''QPushButton#acceptButton {
                color: rgb(0, 0, 0);
                background-color: rgb(0, 162, 0);
                border: 2px solid rgb(0, 62, 0);
                border-radius: 30px;
                }
                QPushButton#acceptButton:hover {
                background-color: rgb(0, 140, 0);
                }'''
            )
        else:
            self.froudEmoji.show()
            self.setWindowTitle('Попробуй сначала!')
            self.setStyleSheet('QDialog#Dialog{background-color: rgb(255, 166, 166);}')
            self.label.setText('Неправильно. Попробуй сначала.')
            self.label.setStyleSheet('color: rgb(0, 0, 0)')
            self.acceptButton.setStyleSheet(
                '''QPushButton#acceptButton {
                color: rgb(0, 0, 0);
                background-color: rgb(255, 117, 117);
                border: 2px solid rgb(101, 0, 0);
                border-radius: 30px;
                }
                QPushButton#acceptButton:hover {
                background-color: rgb(225, 87, 87);
                }'''
            )

    def acceptButtonClicked(self):
        self.close()


class TutorialDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/tutorialDialog.ui', self)

        self.quitButton.clicked.connect(self.quit)
        self.goToChooseDifficultyPageButton.clicked.connect(self.openChooseDifficultyPage)
        self.goToMainGameButton.clicked.connect(self.openMainGamePage)
        self.goToShopButton.clicked.connect(self.openShopPage)

    def openChooseDifficultyPage(self):
        self.pages.setCurrentWidget(self.chooseDifficultyPage)

    def openMainGamePage(self):
        self.pages.setCurrentWidget(self.mainGamePage)

    def openShopPage(self):
        self.pages.setCurrentWidget(self.shopPage)

    def quit(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
