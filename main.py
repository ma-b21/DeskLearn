from WebLearning import Student, NoUser
from login import login_window
from floating import FloatWindow
from mainwindow import MainWindow
import icons_rc
from PyQt5.QtWidgets import QAction, QApplication, QMenu, QSystemTrayIcon
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtWidgets, QtCore
from qfluentwidgets import (setThemeColor, InfoBar, StateToolTip,
                            InfoBarIcon, InfoBarPosition)
import sys
import time
import os
import psutil

MEMORY_MAX = 200  # MB

class DeskWebLearn(QApplication):
    floating_window = None
    main_window = None
    student = None
    tray_icon = None

    waitRing = None

    login_fail = QtCore.pyqtSignal()

    def __init__(self, sys_argv):
        super(DeskWebLearn, self).__init__(sys_argv)
        setThemeColor("#E040FB")

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(":/icon"))

        self.tray_icon.activated.connect(self.trayClick)
        self.floating_window = FloatWindow()
        self.login_window = login_window()
        self.login_window.setWindowIcon(QIcon(":/icon"))

        self.mask = QtWidgets.QWidget()
        self.mask.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.Tool
        )
        self.mask.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        # 全屏
        self.mask.setGeometry(QApplication.desktop().screenGeometry())
        self.mask.show()

        show_action = QAction("显示", self)
        quit_action = QAction("退出", self)
        show_action.triggered.connect(self.showMain)
        quit_action.triggered.connect(QCoreApplication.instance().quit)

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self.login_window.login_signal.connect(self.login)
        self.login_fail.connect(self.login_window.show)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._checkMemory)
        self.timer.start(1000 * 60 * 30)  # 30分钟检查一次内存占用

        try:
            self.student = Student()
        except NoUser:
            self.login_fail.emit()
            return
        except Exception as e:
            print(e)
            if e.__str__().startswith("获取ticket失败"):
                infobar = InfoBar(InfoBarIcon.ERROR, "登录失败", "学号或密码错误!",
                                  position=InfoBarPosition.TOP)
                infobar.setWindowFlags(
                    QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint
                )
                infobar.show()
                self.login_fail.emit()
            else:
                infobar = InfoBar(InfoBarIcon.ERROR, "登录失败", "请稍后再试!",
                                  position=InfoBarPosition.TOP)
                infobar.setWindowFlags(
                    QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
                infobar.show()
            return

        self.main_window = MainWindow(self.student)
        self.floating_window.show()
        self.floating_window.clicked.connect(self.showMain)
        self.main_window.minimizeSignal.connect(self.showFloat)
        self.main_window.logoutSignal.connect(self.logout)

    def _waitRing(self):
        self.waitRing = StateToolTip("登录中...", "请耐心等待", parent=self.mask)
        # self.waitRing移动到窗口中间
        self.waitRing.move(
            self.login_window.x() + self.login_window.width() // 2 -
            self.waitRing.width() // 2 + 10,
            self.login_window.y() + 60
        )
        self.waitRing.closeButton.hide()
        self.waitRing.show()
        QApplication.processEvents()
        QApplication.processEvents()

    def login(self, studentNo, password):
        self._waitRing()
        try:
            self.student = Student(studentNo, password)
        except Exception as e:
            self.waitRing.hide()
            if e.__str__().startswith("获取ticket失败"):
                infobar = InfoBar(InfoBarIcon.ERROR, "登录失败", "学号或密码错误!",
                                  position=InfoBarPosition.TOP)
                infobar.setWindowFlags(
                    QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint
                )
                infobar.show()
                self.login_fail.emit()
            else:
                infobar = InfoBar(InfoBarIcon.ERROR, "登录失败", "请稍后再试!",
                                  position=InfoBarPosition.TOP)
                infobar.setWindowFlags(
                    QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
                infobar.show()
            return

        self.main_window = MainWindow(self.student)
        self.waitRing.setState(True)
        time.sleep(2)
        self.login_window.close()
        self.floating_window.show()
        self.floating_window.clicked.connect(self.showMain)
        self.main_window.minimizeSignal.connect(self.showFloat)
        self.main_window.logoutSignal.connect(self.logout)

    def logout(self):
        self.student.logout()
        self.main_window.close()
        self.floating_window.close()
        QCoreApplication.instance().quit()

    def trayClick(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.showMain()

    def showMain(self):
        self.main_window.resize(5, 5)
        pos = self.floating_window.pos()
        pos.setX(pos.x() + 25)
        pos.setY(pos.y() + 25)
        self.main_window._showNormal(pos)
        self.floating_window.hide()

    def showFloat(self, pos: QtCore.QPoint):
        screen_geometry = QApplication.desktop().screenGeometry()
        # 确保窗口右下角不超出屏幕边界
        x = min(pos.x(), screen_geometry.width() - 50)
        y = min(pos.y(), screen_geometry.height() - 50)

        # 确保窗口左上角不超出屏幕边界
        x = max(0, x)
        y = max(0, y)

        adjusted_pos = QtCore.QPoint(x, y)
        self.floating_window.move(adjusted_pos)
        self.floating_window.show()
        self.floating_window.setFocus()
        self.floating_window.setFocusOut()

    def _checkMemory(self):
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        memory_usage = mem_info.rss / (1024 * 1024)  # 将字节转换为MB
        print("内存占用: %f MB" % memory_usage)
        if memory_usage > MEMORY_MAX:
            self.tray_icon.hide()
            os.execl(sys.executable, sys.executable, *sys.argv)


if __name__ == '__main__':
    try:
        app = DeskWebLearn(sys.argv)
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
