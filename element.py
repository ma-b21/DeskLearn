from typing import Union
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import (CaptionLabel, CardWidget, TitleLabel,
                            SwitchSettingCard, FluentIcon, PushSettingCard,
                            StrongBodyLabel, SubtitleLabel, ImageLabel,
                            ComboBoxSettingCard, OptionsConfigItem,
                            OptionsValidator, HyperlinkCard, SingleDirectionScrollArea,
                            BodyLabel, ProgressBar)
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QEvent, Qt
from qfluentwidgets.common.icon import FluentIconBase
from qfluentwidgets.components.widgets.info_bar import InfoBarIcon, InfoBarPosition
import icons_rc
import sys, os
import WebLearning as spider
from PyQt5 import sip


class Ui_Notice(object):
    def setupUi(self, Notice):
        Notice.setObjectName("Notice")
        Notice.resize(690, 115)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Notice.sizePolicy().hasHeightForWidth())
        Notice.setSizePolicy(sizePolicy)
        Notice.setMinimumSize(QtCore.QSize(0, 0))
        self.verticalLayout = QtWidgets.QVBoxLayout(Notice)
        self.verticalLayout.setContentsMargins(20, -1, 20, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.title = SubtitleLabel(Notice)
        self.title.setTextFormat(QtCore.Qt.RichText)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(14)
        font.setBold(True)
        self.title.setFont(font)
        self.title.setObjectName("title")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout.addWidget(self.title)
        self.course = StrongBodyLabel(Notice)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        font.setBold(True)
        self.course.setFont(font)
        self.course.setAlignment(QtCore.Qt.AlignCenter)
        self.course.setObjectName("course")
        self.horizontalLayout.addWidget(self.course)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.teacher = CaptionLabel(Notice)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(False)
        self.teacher.setFont(font)
        self.teacher.setAlignment(QtCore.Qt.AlignCenter)
        self.teacher.setObjectName("teacher")
        self.horizontalLayout_2.addWidget(self.teacher)
        self.time = CaptionLabel(Notice)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(False)
        self.time.setFont(font)
        self.time.setAlignment(QtCore.Qt.AlignCenter)
        self.time.setObjectName("time")
        self.horizontalLayout_2.addWidget(self.time)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 4)
        self.verticalLayout.setStretch(2, 1)
        self.setFixedHeight(115)

        self.retranslateUi(Notice)
        QtCore.QMetaObject.connectSlotsByName(Notice)

    def retranslateUi(self, Notice):
        _translate = QtCore.QCoreApplication.translate
        Notice.setWindowTitle(_translate("Notice", "Form"))
        self.title.setText(_translate("Notice", "title"))
        self.course.setText(_translate("Notice", "course"))
        self.teacher.setText(_translate("Notice", "teacher"))
        self.time.setText(_translate("Notice", "time"))


class Notice(CardWidget, Ui_Notice):
    notice_clicked = QtCore.pyqtSignal(spider.Notice)

    def __init__(self, parent=None, notice: spider.Notice = None):
        super().__init__(parent)
        self.setupUi(self)
        self.setClickEnabled(True)

        self.title.installEventFilter(self)
        self.title.setText(notice.title)

        fontMetrics = self.title.fontMetrics()
        if fontMetrics.width(self.title.text()) > self.title.width():
            elidedText = fontMetrics.elidedText(
                self.title.text(), QtCore.Qt.ElideRight, int(self.title.width() * 3.5))
            self.title.setText(elidedText)

        self.course.setText(notice.course.course_name)
        self.teacher.setText(notice.publisher)
        self.time.setText(notice.publish_time_str)
        self._notice = notice
        self.clicked.connect(lambda: self.notice_clicked.emit(self._notice))

    def eventFilter(self, obj, e):
        if e.type() == QEvent.MouseButtonPress and e.button() == QtCore.Qt.LeftButton\
                and obj == self.title:
            self.notice_clicked.emit(self._notice)
            return True
        return super().eventFilter(obj, e)

    def __str__(self):
        return f"Notice({self._notice})"


class NoticeWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("contentsWidget")

        self.notices = []

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setAlignment(
            QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter
        )

        self.size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.size_policy.setHorizontalStretch(0)
        self.size_policy.setVerticalStretch(0)

        self.empty = ImageLabel(self)
        self.empty.setObjectName("empty")
        image = QtGui.QImage(":/empty")
        self.empty.setImage(image)
        self.empty.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.empty)
        self.empty.setFixedSize(200, 200)
        self.empty.hide()

        # 增加文字提示
        self.empty_text = SubtitleLabel(self)
        self.empty_text.setObjectName("empty_text")
        self.empty_text.setText("暂无通知")
        self.empty_text.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.empty_text)
        self.empty_text.hide()

    def checkEmpty(self):
        if len(self.notices) == 0:
            self.empty.show()
            self.empty_text.show()
        else:
            self.empty.hide()
            self.empty_text.hide()

    def insert_notice(self, notice: spider.Notice):
        notice_ = Notice(notice=notice)
        notice_.setSizePolicy(self.size_policy)
        notice_.setObjectName("notice")
        self.verticalLayout.addWidget(notice_)
        self.notices.append(notice_)
        del notice
        del notice_
        pass

    def clear(self):
        for i in range(2, self.verticalLayout.count()):
            self.verticalLayout.itemAt(i).widget().deleteLater()
        for notice in self.notices:
            self.verticalLayout.removeWidget(notice)
            notice.clicked.disconnect()
            notice.notice_clicked.disconnect()
            notice.deleteLater()
            sip.delete(notice)
        self.notices.clear()


class Ui_Assignment(object):
    def setupUi(self, Assignment):
        Assignment.setObjectName("Assignment")
        Assignment.resize(690, 115)
        self.gridLayout = QtWidgets.QGridLayout(Assignment)
        self.gridLayout.setObjectName("gridLayout")
        self.course = StrongBodyLabel(Assignment)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        font.setBold(True)
        self.course.setFont(font)
        self.course.setAlignment(QtCore.Qt.AlignCenter)
        self.course.setObjectName("course")
        self.gridLayout.addWidget(self.course, 0, 2, 1, 2)
        self.deadline = CaptionLabel(Assignment)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(False)
        self.deadline.setFont(font)
        self.deadline.setObjectName("deadline")
        self.gridLayout.addWidget(self.deadline, 1, 3, 1, 1)
        self.teacher = CaptionLabel(Assignment)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(False)
        self.teacher.setFont(font)
        self.teacher.setAlignment(QtCore.Qt.AlignCenter)
        self.teacher.setObjectName("teacher")
        self.gridLayout.addWidget(self.teacher, 1, 0, 1, 2)
        self.title = SubtitleLabel(Assignment)
        self.title.setTextFormat(QtCore.Qt.RichText)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(14)
        font.setBold(True)
        self.title.setFont(font)
        self.title.setObjectName("title")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.title, 0, 0, 1, 2)
        self.label = CaptionLabel(Assignment)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        font.setBold(False)
        self.label.setFont(font)
        self.label.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 2, 1, 1)
        self.setFixedHeight(115)
        self.retranslateUi(Assignment)
        QtCore.QMetaObject.connectSlotsByName(Assignment)

    def retranslateUi(self, Assignment):
        _translate = QtCore.QCoreApplication.translate
        Assignment.setWindowTitle(_translate("Assignment", "Form"))
        self.course.setText(_translate("Assignment", "course"))
        self.deadline.setText(_translate("Assignment", "deadline"))
        self.teacher.setText(_translate("Assignment", "teacher"))
        self.title.setText(_translate("Assignment", "title"))
        self.label.setText(_translate("Assignment", "截止时间"))


class Assignment(CardWidget, Ui_Assignment):
    assignment_clicked = QtCore.pyqtSignal(spider.Assignment)

    def __init__(self, parent=None, assignment: spider.Assignment = None):
        super().__init__(parent)
        self.setupUi(self)
        self.setClickEnabled(True)

        self.title.installEventFilter(self)
        self.title.setText(assignment.title)

        fontMetrics = self.title.fontMetrics()
        if fontMetrics.width(self.title.text()) > self.title.width():
            elidedText = fontMetrics.elidedText(
                self.title.text(), QtCore.Qt.ElideRight, int(self.title.width() * 3.5))
            self.title.setText(elidedText)

        self.course.setText(assignment.course.course_name)
        self.teacher.setText(assignment.course.teacher_name)
        self.deadline.setText(assignment.str_end_time)
        self._assignment = assignment
        self.clicked.connect(
            lambda: self.assignment_clicked.emit(self._assignment))

    def eventFilter(self, obj, e):
        if e.type() == QEvent.MouseButtonPress and e.button() == QtCore.Qt.LeftButton\
                and obj == self.title:
            self.assignment_clicked.emit(self._assignment)
            return True
        return super().eventFilter(obj, e)


class AssignmentWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.assignments = []

        self.setObjectName("contentsWidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setAlignment(
            QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter
        )

        self.size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.size_policy.setHorizontalStretch(0)
        self.size_policy.setVerticalStretch(0)

        self.empty = ImageLabel(self)
        self.empty.setObjectName("empty")
        image = QtGui.QImage(":/empty")
        self.empty.setImage(image)
        self.empty.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.empty)
        self.empty.hide()
        self.empty.setFixedSize(200, 200)

        # 增加文字提示
        self.empty_text = SubtitleLabel(self)
        self.empty_text.setObjectName("empty_text")
        self.empty_text.setText("暂无作业")
        self.empty_text.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.empty_text)
        self.empty_text.hide()

    def checkEmpty(self):
        # self.assignments中任一个可见即不为空
        if any(assignment.isVisible() for assignment in self.assignments):
            self.empty.hide()
            self.empty_text.hide()
        else:
            self.empty.show()
            self.empty_text.show()

    def insert_assignment(self, assignment: spider.Assignment):
        assignment_ = Assignment(assignment=assignment)
        assignment_.setSizePolicy(self.size_policy)
        assignment_.setObjectName("assignment")
        self.verticalLayout.addWidget(assignment_)
        self.assignments.append(assignment_)
        del assignment
        del assignment_
        pass

    def clear(self):
        for i in range(2, self.verticalLayout.count()):
            self.verticalLayout.itemAt(i).widget().deleteLater()
        for assignment in self.assignments:
            self.verticalLayout.removeWidget(assignment)
            assignment.clicked.disconnect()
            assignment.assignment_clicked.disconnect()
            assignment.deleteLater()
            sip.delete(assignment)
        self.assignments.clear()

    def count(self):
        return len(self.assignments)


class Ui_File(object):
    def setupUi(self, File):
        File.setObjectName("File")
        File.resize(690, 115)
        self.gridLayout = QtWidgets.QGridLayout(File)
        self.gridLayout.setObjectName("gridLayout")
        self.file_type = CaptionLabel(File)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(False)
        self.file_type.setFont(font)
        self.file_type.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.file_type.setObjectName("file_type")
        self.gridLayout.addWidget(self.file_type, 1, 0, 1, 1)
        self.file_size = CaptionLabel(File)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(False)
        self.file_size.setFont(font)
        self.file_size.setObjectName("file_size")
        self.gridLayout.addWidget(self.file_size, 1, 1, 1, 1)
        self.course = StrongBodyLabel(File)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        font.setBold(True)
        self.course.setFont(font)
        self.course.setAlignment(QtCore.Qt.AlignCenter)
        self.course.setObjectName("course")
        self.gridLayout.addWidget(self.course, 0, 2, 1, 2)
        self.time = CaptionLabel(File)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(False)
        self.time.setFont(font)
        self.time.setAlignment(QtCore.Qt.AlignCenter)
        self.time.setObjectName("time")
        self.gridLayout.addWidget(self.time, 1, 2, 1, 2)
        self.title = SubtitleLabel(File)
        self.title.setTextFormat(QtCore.Qt.RichText)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(14)
        font.setBold(True)
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setObjectName("title")
        self.gridLayout.addWidget(self.title, 0, 0, 1, 2)
        self.setFixedHeight(115)

        self.retranslateUi(File)
        QtCore.QMetaObject.connectSlotsByName(File)

    def retranslateUi(self, File):
        _translate = QtCore.QCoreApplication.translate
        File.setWindowTitle(_translate("File", "Form"))
        self.file_type.setText(_translate("File", "type"))
        self.file_size.setText(_translate("File", "size"))
        self.course.setText(_translate("File", "course"))
        self.time.setText(_translate("File", "time"))
        self.title.setText(_translate("File", "title"))


class File(CardWidget, Ui_File):
    file_clicked = QtCore.pyqtSignal(spider.File)

    def __init__(self, parent=None, file: spider.File = None):
        super().__init__(parent)
        self.setupUi(self)
        self.setClickEnabled(True)

        self.title.installEventFilter(self)
        self.title.setText(file.file_name)

        fontMetrics = self.title.fontMetrics()
        if fontMetrics.width(self.title.text()) > self.title.width():
            elidedText = fontMetrics.elidedText(
                self.title.text(), QtCore.Qt.ElideRight, int(self.title.width() * 3.5))
            self.title.setText(elidedText)

        self.course.setText(file.course.course_name)
        self.file_type.setText(file.file_type)
        size = file.file_size
        if size > 1024 * 1024 * 1024:
            size = str(round(size / 1024 / 1024 / 1024, 2)) + "GB"
        elif size > 1024 * 1024:
            size = str(round(size / 1024 / 1024, 2)) + "MB"
        elif size > 1024:
            size = str(round(size / 1024, 2)) + "KB"
        else:
            size = str(size) + "B"
        self.file_size.setText(size)
        self.time.setText(file.file_time_str)
        self._file = file
        self.clicked.connect(lambda: self.file_clicked.emit(self._file))

    def eventFilter(self, obj, e):
        if e.type() == QEvent.MouseButtonPress and e.button() == QtCore.Qt.LeftButton\
                and obj == self.title:
            self.file_clicked.emit(self._file)
            return True
        return super().eventFilter(obj, e)


class FileWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.files = []

        self.setObjectName("contentsWidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setAlignment(
            QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter
        )

        self.size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.size_policy.setHorizontalStretch(0)
        self.size_policy.setVerticalStretch(0)

        self.empty = ImageLabel(self)
        self.empty.setObjectName("empty")
        image = QtGui.QImage(":/empty")
        self.empty.setImage(image)
        self.empty.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.empty)
        self.empty.setFixedSize(200, 200)
        self.empty.hide()

        # 增加文字提示
        self.empty_text = SubtitleLabel(self)
        self.empty_text.setObjectName("empty_text")
        self.empty_text.setText("暂无文件")
        self.empty_text.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.empty_text)
        self.empty_text.hide()

    def checkEmpty(self):
        if len(self.files) == 0:
            self.empty.show()
            self.empty_text.show()
        else:
            self.empty.hide()
            self.empty_text.hide()

    def insert_file(self, file: spider.File):
        file_ = File(file=file)
        file_.setSizePolicy(self.size_policy)
        file_.setObjectName("file")
        self.verticalLayout.addWidget(file_)
        self.files.append(file_)
        del file
        del file_
        pass

    def clear(self):
        for i in range(2, self.verticalLayout.count()):
            self.verticalLayout.itemAt(i).widget().deleteLater()
            QtWidgets.QApplication.processEvents()
        for file in self.files:
            self.verticalLayout.removeWidget(file)
            file.clicked.disconnect()
            file.file_clicked.disconnect()
            file.deleteLater()
            sip.delete(file)
        self.files.clear()


class Ui_Course(object):
    def setupUi(self, Course):
        Course.setObjectName("Course")
        Course.resize(690, 115)
        self.gridLayout = QtWidgets.QGridLayout(Course)
        self.gridLayout.setObjectName("gridLayout")
        self.course = TitleLabel(Course)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(14)
        font.setBold(True)
        self.course.setAlignment(QtCore.Qt.AlignCenter)
        self.course.setObjectName("course")
        self.course.setFont(font)
        self.gridLayout.addWidget(self.course, 0, 0, 1, 1)
        self.course_number = StrongBodyLabel(Course)
        font.setPointSize(12)
        font.setBold(False)
        self.course_number.setFont(font)
        self.course_number.setAlignment(QtCore.Qt.AlignCenter)
        self.course_number.setObjectName("course_number")
        self.gridLayout.addWidget(self.course_number, 0, 1, 1, 1)
        self.teacher = SubtitleLabel(Course)
        self.teacher.setAlignment(QtCore.Qt.AlignCenter)
        self.teacher.setObjectName("teacher")
        font.setPointSize(13)
        font.setBold(True)
        self.teacher.setFont(font)
        self.gridLayout.addWidget(self.teacher, 1, 0, 1, 1)
        self.setFixedHeight(115)

        self.retranslateUi(Course)
        QtCore.QMetaObject.connectSlotsByName(Course)

    def retranslateUi(self, Course):
        _translate = QtCore.QCoreApplication.translate
        Course.setWindowTitle(_translate("Course", "Form"))
        self.course.setText(_translate("Course", "Course"))
        self.course_number.setText(_translate("Course", "course_number"))
        self.teacher.setText(_translate("Course", "teacher"))


class Course(CardWidget, Ui_Course):
    course_clicked = QtCore.pyqtSignal(spider.Course)

    def __init__(self, parent=None, course: spider.Course = None):
        super().__init__(parent)
        self.setupUi(self)
        self.setClickEnabled(True)

        self.course.setText(course.course_name)
        self.course_number.setText(course.course_number)
        self.teacher.setText(course.teacher_name)

        self._course = course
        self.clicked.connect(lambda: self.course_clicked.emit(self._course))


class CourseWidget(QtWidgets.QWidget):
    courses = []

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("contentsWidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setAlignment(
            QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter
        )

    def insert_course(self, course: spider.Course):
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        course = Course(self, course)
        sizePolicy.setHeightForWidth(
            course.sizePolicy().hasHeightForWidth()
        )
        course.setSizePolicy(sizePolicy)
        course.setObjectName("course")
        self.verticalLayout.addWidget(course)
        self.courses.append(course)

    def clear(self):
        for i in range(self.verticalLayout.count()):
            self.verticalLayout.itemAt(i).widget().deleteLater()
        self.courses.clear()

    def count(self):
        return len(self.courses)


class SettingWidget(QtWidgets.QWidget):
    semesterChanged = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("settingsWidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(80, 50, 80, 50)
        self.verticalLayout.setAlignment(
            QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter
        )

        self.brightness = SwitchSettingCard(
            FluentIcon("Brightness"), "夜间模式", parent=self)
        self.brightness.setFixedHeight(60)
        self.brightness.iconLabel.setFixedSize(25, 25)
        self.brightness.switchButton.setFixedHeight(30)
        self.brightness.setObjectName("brightness")
        self.verticalLayout.addWidget(self.brightness)

        self.issue = HyperlinkCard(
            "https://github.com/ma-b21/DeskLearn/issues/new",
            "前往GitHub",
            FluentIcon("GitHub"),
            "问题反馈",
            parent=self
        )
        self.issue.setFixedHeight(60)
        self.issue.iconLabel.setFixedSize(25, 25)
        self.issue.setObjectName("issue")
        self.verticalLayout.addWidget(self.issue)

        self.logout = PushSettingCard(
            "退出",
            FluentIcon("PowerButton"),
            "退出登录",
            parent=self
        )
        self.logout.setFixedHeight(60)
        self.logout.iconLabel.setFixedSize(23, 23)
        self.logout.setObjectName("logout")
        self.verticalLayout.addWidget(self.logout)

    def insertSemester(self, semesters):
        self.configItem = OptionsConfigItem(
            "semesters", "semesters",
            semesters[0], validator=OptionsValidator(semesters)
        )

        semester_dict = {
            "1": "秋季学期",
            "2": "春季学期",
            "3": "夏季学期"
        }

        semesters_texts = [
            f"{semester[:9]}学年{semester_dict[semester[-1]]}"
            for semester in semesters
        ]

        self.semester = ComboBoxSettingCard(
            self.configItem,
            FluentIcon("Education"),
            "学年学期",
            texts=semesters_texts,
        )
        self.semester.setFixedHeight(60)
        self.semester.iconLabel.setFixedSize(25, 25)
        self.semester.setObjectName("semester")
        self.verticalLayout.insertWidget(1, self.semester)
        self.configItem.valueChanged.connect(
            lambda: self.semesterChanged.emit(self.configItem.value))


class Ui_download(object):
    def setupUi(self, download):
        download.setObjectName("download")
        download.resize(380, 60)
        self.gridLayout = QtWidgets.QGridLayout(download)
        self.gridLayout.setContentsMargins(30, 3, 30, 3)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.ProgressBar = ProgressBar(download)
        self.ProgressBar.setObjectName("ProgressBar")
        self.gridLayout.addWidget(self.ProgressBar, 1, 0, 1, 2)
        self.speed = CaptionLabel(download)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(9)
        font.setBold(False)
        self.speed.setFont(font)
        self.speed.setObjectName("speed")
        self.gridLayout.addWidget(self.speed, 2, 0, 1, 1)
        self.current_and_total = CaptionLabel(download)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(9)
        font.setBold(False)
        self.current_and_total.setFont(font)
        self.current_and_total.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.current_and_total.setObjectName("current_and_total")
        self.gridLayout.addWidget(self.current_and_total, 2, 1, 1, 1)
        self.filename = BodyLabel(download)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(False)
        self.filename.setFont(font)
        self.filename.setObjectName("filename")
        self.gridLayout.addWidget(self.filename, 0, 0, 1, 1)
        self.percent = CaptionLabel(download)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(9)
        font.setBold(False)
        self.percent.setFont(font)
        self.percent.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.percent.setObjectName("percent")
        self.gridLayout.addWidget(self.percent, 0, 1, 1, 1)
        self.gridLayout.setColumnStretch(0, 1)

        self.retranslateUi(download)
        QtCore.QMetaObject.connectSlotsByName(download)

    def retranslateUi(self, download):
        _translate = QtCore.QCoreApplication.translate
        download.setWindowTitle(_translate("download", "Form"))
        self.speed.setText(_translate("download", "speed"))
        self.current_and_total.setText(_translate("download", "current/total"))
        self.filename.setText(_translate("download", "filename"))
        self.percent.setText(_translate("download", "persent"))


class download(CardWidget, Ui_download):
    def __init__(self, filename: str, path: str, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setClickEnabled(True)
        self.setFixedSize(275, 60)
        self.ProgressBar.setValue(0)
        self.speed.setText("0KB/s")
        self.current_and_total.setText("0/0")
        self.percent.setText("0%")
        self.filename.setText(filename)
        fontMetrics = self.filename.fontMetrics()
        if fontMetrics.width(self.filename.text()) > self.filename.width():
            elidedText = fontMetrics.elidedText(
                self.filename.text(), QtCore.Qt.ElideRight, int(self.filename.width() * 1.8))
            self.filename.setText(elidedText)
            self.filename.setToolTip(filename)
        
        self._path = path
        self.clicked.connect(self.open_file)

    def open_file(self):
        if self.ProgressBar.value() != 100:
            return
        # 判定文件是否存在
        if not os.path.exists(self._path):
            # 设置speed为红色
            self.speed.setStyleSheet("color: red;")
            self.speed.setText("文件被移动或删除")
            return
        os.startfile(self._path)

    # 定义hover事件
    def enterEvent(self, event):
        if self.ProgressBar.value() == 100:
            self.setCursor(QtCore.Qt.PointingHandCursor)
            self.percent.setText("点击打开")
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        if self.ProgressBar.value() == 100:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.percent.setText("100%")
        super().leaveEvent(event)


class Ui_download_window(object):
    def setupUi(self, download_window):
        download_window.setObjectName("download_window")
        download_window.resize(300, 300)
        download_window.setStyleSheet("#container.QFrame{\n"
"      background-color: #f0f0f0;\n"
"      border:1px solid #000000;   /*边框的粗细，颜色*/\n"
"      border-radius:15px;    /*设置圆角半径 */\n"
"      padding:2px 4px;  /*QFrame边框与内部其它部件的距离*/\n"
"}")
        download_window.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.gridLayout = QtWidgets.QGridLayout(download_window)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.container = QtWidgets.QFrame(download_window)
        self.container.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.container.setFrameShadow(QtWidgets.QFrame.Raised)
        self.container.setObjectName("container")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.container)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.SingleDirectionScrollArea = SingleDirectionScrollArea(self.container)
        self.SingleDirectionScrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.SingleDirectionScrollArea.setWidgetResizable(True)
        self.SingleDirectionScrollArea.setObjectName("SingleDirectionScrollArea")
        self.download_widget = QtWidgets.QWidget()
        self.download_widget.setGeometry(QtCore.QRect(0, 0, 290, 294))
        self.download_widget.setObjectName("download_widget")
        self.SingleDirectionScrollArea.setWidget(self.download_widget)
        self.gridLayout_2.addWidget(self.SingleDirectionScrollArea, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.container, 0, 0, 1, 1)

        self.retranslateUi(download_window)
        QtCore.QMetaObject.connectSlotsByName(download_window)

    def retranslateUi(self, download_window):
        _translate = QtCore.QCoreApplication.translate
        download_window.setWindowTitle(_translate("download_window", "Frame"))


class download_window(QtWidgets.QFrame, Ui_download_window):
    obj_dict = {}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setObjectName("download_window")
        # 设置窗口背景透明
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.verticalLayout = QtWidgets.QVBoxLayout(self.download_widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 20, 0, 30)
        self.verticalLayout.setAlignment(
            QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter
        )

        self.empty = ImageLabel(self)
        self.empty.setObjectName("empty")
        image = QtGui.QImage(":/empty")
        self.empty.setImage(image)
        self.empty.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.empty)
        self.empty.setFixedSize(150, 150)
        self.empty.hide()

        # 增加文字提示
        self.empty_text = SubtitleLabel(self)
        self.empty_text.setObjectName("empty_text")
        self.empty_text.setText("暂无文件")
        self.empty_text.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.empty_text)
        self.empty_text.hide()

        self.animation_1 = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.animation_1.setDuration(300)

        self.animation_2 = QtCore.QPropertyAnimation(self, b"geometry")
        self.animation_2.setDuration(300)

    def checkEmpty(self):
        if len(self.obj_dict) == 0:
            self.empty.show()
            self.empty_text.show()
        else:
            self.empty.hide()
            self.empty_text.hide()

    def insert_download(self, filename: str, path: str):
        down = download(filename, path)
        down.setFixedHeight(60)
        self.verticalLayout.insertWidget(0, down)
        self.obj_dict[filename] = down

    def clear(self):
        for i in range(0, self.verticalLayout.count()):
            self.verticalLayout.itemAt(i).widget().deleteLater()
        self.obj_dict.clear()
    
    def set_progress(self, filename: str, value: int):
        self.obj_dict[filename].ProgressBar.setValue(value)
        QtWidgets.QApplication.processEvents()

    def set_speed(self, filename: str, speed: str):
        self.obj_dict[filename].speed.setText(speed)
        self.obj_dict[filename].speed.update()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()

    def set_percent(self, filename: str, percent: str):
        self.obj_dict[filename].percent.setText(percent)
        self.obj_dict[filename].percent.update()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
    
    def set_current_and_total(self, filename: str, current_and_total: str):
        self.obj_dict[filename].current_and_total.setText(current_and_total)
        self.obj_dict[filename].current_and_total.update()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()

    def _changeTheme(self, theme: str):
        if theme == "dark":
            self.setStyleSheet("#container.QFrame{\n"
            "      background-color: #444449;\n"
            "      border:1px solid #ffffff;   /*边框的粗细，颜色*/\n"
            "      border-radius:15px;    /*设置圆角半径 */\n"
            "      padding:2px 4px;  /*QFrame边框与内部其它部件的距离*/\n"
            "}")
            self.empty.setImage(QtGui.QImage(":/empty_night"))
            self.empty.setFixedSize(150, 150)
            self.download_widget.setStyleSheet("background-color: #444449;")
        else:
            self.setStyleSheet("#container.QFrame{\n"
            "      background-color: #f0f0f0;\n"
            "      border:1px solid #000000;   /*边框的粗细，颜色*/\n"
            "      border-radius:15px;    /*设置圆角半径 */\n"
            "      padding:2px 4px;  /*QFrame边框与内部其它部件的距离*/\n"
            "}")
            self.empty.setImage(QtGui.QImage(":/empty"))
            self.empty.setFixedSize(150, 150)
            self.download_widget.setStyleSheet("")

    # def show(self, pos: QtCore.QPoint):
    #     # 设置窗口动画
    #     super().show()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    download = download_window()
    download.show()
    sys.exit(app.exec_())
