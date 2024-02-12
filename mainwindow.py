import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from mainwindow_ui import Ui_MainWindow
from qfluentwidgets import (FluentIcon, setThemeColor, 
                            setTheme, Theme, StateToolTip)
from WebLearning import Student
import WebLearning as spider
import base64
from PyQt5.QtCore import QByteArray
import icons_rc
from concurrent.futures import ThreadPoolExecutor
import time
from element import download_window
from utils import trans_size
import win32api

def get_self_version():
    try:
        # 获取当前运行的exe文件路径
        executable_path = sys.executable
        # 获取文件的版本信息
        info = win32api.GetFileVersionInfo(executable_path, "\\")
        # 提取产品版本的主版本号和次版本号
        product_version_ms = info['ProductVersionMS']
        major = product_version_ms >> 16
        minor = product_version_ms & 0xFFFF
        # 返回格式化的主版本号和次版本号
        return f"v{major}.{minor}"
    except Exception as e:
        return f"无法获取版本号: {str(e)}"

class MainWindow(QtWidgets.QWidget, Ui_MainWindow):
    theme = Theme.LIGHT

    noticeUpdated = QtCore.pyqtSignal(list)
    assignmentUpdated = QtCore.pyqtSignal(list)
    fileUpdated = QtCore.pyqtSignal(list)

    minimizeSignal = QtCore.pyqtSignal(QtCore.QPoint)
    logoutSignal = QtCore.pyqtSignal()
    downloadSignal = QtCore.pyqtSignal(str, str)
    downloadChanged = QtCore.pyqtSignal(str, str, int, int)

    student = None
    courses = None
    notices = None
    assignments = None
    files = None

    course_in_detail_widget = None

    showDirection = None

    def __init__(self, student: Student):
        super().__init__()
        self.setupUi(self)
        self.version = get_self_version()
        self.student = student
        self.courses = student.courses
        self.uname.setText(student.name)
        avatar_bytes = QByteArray(base64.b64decode(student.avatar))
        avatar = QtGui.QImage.fromData(avatar_bytes)
        self.avatar.setImage(avatar)
        self.avatar.setFixedSize(30, 30)
        self.avatar.setScaledContents(True)

        for i in range(100):
            QtWidgets.QApplication.processEvents()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint |
                            QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        setThemeColor("#E040FB")

        self.back_button.setIcon(FluentIcon("Return"))
        self.back_button.hide()
        self.back_button.clicked.connect(self._return)
        self.notice_content.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.notice_content.adjustSize()
        self.notice_content.setWordWrap(True)
        self.notice_content.setAlignment(QtCore.Qt.AlignTop)

        # 下载窗口
        self.downloadSignal.connect(self._showDownload)
        self.downloadWindow = download_window(self)
        self.downloadWindow.hide()
        
        self.download_button.setIcon(FluentIcon("Download"))
        self.download_button.clicked.connect(self._showDownloadWindow)

        self.downloadChanged.connect(self._updateDownload)

        for i in range(100):
            QtWidgets.QApplication.processEvents()
        self.maximize.clicked.connect(self.maximizeWindow)
        self.minimize.clicked.connect(self.minimizeWindow)

        self.noticeUpdated.connect(self._noticeUpdated)
        self.assignmentUpdated.connect(self._assignmentUpdated)
        self.fileUpdated.connect(self._fileUpdated)

        self._initMenu()
        for i in range(100):
            QtWidgets.QApplication.processEvents()
        self._initPivot()
        for i in range(100):
            QtWidgets.QApplication.processEvents()
        self._initSettings()
        for i in range(100):
            QtWidgets.QApplication.processEvents()

        self._updateAll()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._updateAll)
        self.timer.start(1000 * 60 * 5)  # 5分钟更新一次

        self.empty_timer = QtCore.QTimer()
        self.empty_timer.timeout.connect(self.assignment_list.checkEmpty)
        self.empty_timer.timeout.connect(self.notice_list.checkEmpty)
        self.empty_timer.timeout.connect(self.file_list.checkEmpty)
        self.empty_timer.timeout.connect(
            self.course_assignment_list.checkEmpty)
        self.empty_timer.timeout.connect(self.course_notice_list.checkEmpty)
        self.empty_timer.timeout.connect(self.course_file_list.checkEmpty)
        self.empty_timer.timeout.connect(self.downloadWindow.checkEmpty)
        self.empty_timer.start(50)

        # 设置动画
        self.animition_1 = QtCore.QPropertyAnimation(self, b"geometry")
        self.animition_1.setDuration(200)

        # 设置透明度渐变
        self.animition_2 = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.animition_2.setDuration(200)

        self.animition_1.finished.connect(
            lambda: self.minimizeSignal.emit(self.pos()))
        self.animition_2.finished.connect(self.hide)

        # 设置动画
        self.animition_3 = QtCore.QPropertyAnimation(self, b"geometry")
        self.animition_3.setDuration(200)

        # 设置透明度渐变
        self.animition_4 = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.animition_4.setDuration(200)
        self.animition_4.finished.connect(
            lambda: self.setMinimumSize(950, 650))

        self.setMinimumSize(QtCore.QSize(0, 0))

    def _return(self):
        self.back_button.hide()
        match self.mainWidget.currentIndex():
            case 6:
                self.mainWidget.setCurrentIndex(4)
                self.course_in_detail_widget = None
            case 1:
                if not self.course_in_detail_widget:
                    self.mainWidget.setCurrentIndex(0)
                else:
                    self.back_button.show()
                    self.mainWidget.setCurrentIndex(6)
            case 5:
                if not self.course_in_detail_widget:
                    self.mainWidget.setCurrentIndex(2)
                else:
                    self.back_button.show()
                    self.mainWidget.setCurrentIndex(6)
            case _:
                pass

    def _updateAll(self):
        with ThreadPoolExecutor(max_workers=3) as executor:
            future1 = executor.submit(self._updateNotice)
            future2 = executor.submit(self._updateAssignment)
            future3 = executor.submit(self._updateFile)
            # 等待所有任务完成
            while not (future1.done() and future2.done() and future3.done()):
                QtWidgets.QApplication.processEvents()

    def _noticeUpdated(self, notices):
        self.notice_list.clear()
        for notice in notices:
            self.notice_list.insert_notice(notice)
        for notice in self.notice_list.notices:
            notice.notice_clicked.connect(self._showNoticeDetail)
        self.notices = notices
        for notice in notices:
            del notice
        del notices

    def _assignmentUpdated(self, assignments):
        self.assignment_list.clear()
        for assignment in assignments:
            self.assignment_list.insert_assignment(assignment)
        for assignment in self.assignment_list.assignments:
            assignment.assignment_clicked.connect(self._showAssignmentDetail)
        self.assignments = assignments
        for assignment in assignments:
            del assignment
        del assignments

    def _fileUpdated(self, files):
        self.file_list.clear()
        for file in files:
            self.file_list.insert_file(file)
        for file in self.file_list.files:
            file.file_clicked.connect(self._downloadFile)
        self.files = files
        for file in files:
            del file
        del files

    def _updateNotice(self):
        notices = []
        for course in self.courses:
            notices.extend(course.notices)
        notices.sort(key=lambda x: x.publish_time, reverse=True)
        self.noticeUpdated.emit(notices)
        for notice in notices:
            del notice
        del notices

    def _updateAssignment(self):
        assignments = []
        for course in self.courses:
            assignments.extend(course.assignments)
        assignments.sort(key=lambda x: x.end_time, reverse=True)
        self.assignmentUpdated.emit(assignments)
        for assignment in assignments:
            del assignment
        del assignments

    def _updateFile(self):
        files = []
        for course in self.courses:
            files.extend(course.files)
        files.sort(key=lambda x: x.file_time, reverse=True)
        self.fileUpdated.emit(files)
        for file in files:
            del file
        del files

    def _showNotice(self):
        self.course_in_detail_widget = None
        self.back_button.hide()
        self.mainWidget.setCurrentIndex(0)

    def _showAssignment(self):
        self.back_button.hide()
        self.assignment_list.empty.hide()
        self.assignment_list.empty_text.hide()
        self.course_in_detail_widget = None
        self.mainWidget.setCurrentIndex(2)
        self.assignment_pivot.setCurrentItem("WJ")
        for assignment in self.assignment_list.assignments:
            if assignment._assignment.state == 1:
                assignment.show()
            else:
                assignment.hide()

    def _showFile(self):
        self.back_button.hide()
        self.course_in_detail_widget = None
        self.mainWidget.setCurrentIndex(3)

    def _showCourse(self):
        self.back_button.hide()
        self.course_in_detail_widget = None
        if self.course_list.count() == 0:
            for course in self.courses:
                self.course_list.insert_course(course)

            for course in self.course_list.courses:
                course.course_clicked.connect(self._showCourseDetail)
        self.mainWidget.setCurrentIndex(4)

    def _showCourseDetail(self, course: spider.Course):
        self.course_in_detail_widget = course
        self.back_button.show()
        self.course_name.setText(course.course_name)
        self.course_pivot.setCurrentItem("Notice")
        self.course_notice_list.clear()
        for notice in self.notices:
            if notice.course == course:
                self.course_notice_list.insert_notice(notice)
        for notice in self.course_notice_list.notices:
            notice.notice_clicked.connect(self._showNoticeDetail)
        self.detail_widget.setCurrentIndex(1)
        self.mainWidget.setCurrentIndex(6)

    def _showNoticeDetail(self, notice: spider.Notice):
        def _download_attachment():
            def thread_func(path):
                result = notice.attachment_save(path)
                file_name = next(result)
                total = next(result)
                
                self.downloadSignal.emit(file_name, path)
                start_time = time.time()
                for speed, current in result:
                    QtWidgets.QApplication.processEvents()
                    if current == total:
                        self.downloadChanged.emit(file_name, "下载完成√", total, total)
                        break
                    if time.time() - start_time > 0.3:
                        start_time = time.time()
                        self.downloadChanged.emit(file_name, trans_size(speed), current, total)
                    else:
                        QtWidgets.QApplication.processEvents()

            path = QtWidgets.QFileDialog.getExistingDirectory(
                self, "选择保存文件夹", "./")
            if not path:
                return
            # 后台下载
            with ThreadPoolExecutor() as executor:
                work = executor.submit(thread_func, path)
                while not work.done():
                    QtWidgets.QApplication.processEvents()

        self.back_button.show()
        self.notice_title_in_content.setText(notice.title)
        self.notice_content.setText(notice.content)
        self.notice_time.setText(notice.publish_time_str)
        if notice.attachment_file:
            self.notice_attach_area.show()
            self.notice_attach_link.setText(notice.attachment_file)
            self.notice_attach_link.clicked.disconnect()
            self.notice_attach_link.clicked.connect(_download_attachment)
        else:
            self.notice_attach_area.hide()
        self.mainWidget.setCurrentIndex(1)

    def _showAssignmentDetail(self, assignment: spider.Assignment):
        def _download_attachment(attach_type: int):
            def thread_func(path):
                result = assignment.attachment_save(attach_type, path)
                file_name = next(result)
                total = next(result)
                self.downloadSignal.emit(file_name, path)
                start_time = time.time()
                for speed, current in result:
                    QtWidgets.QApplication.processEvents()
                    if current == total:
                        self.downloadChanged.emit(file_name, "下载完成√", total, total)
                        break
                    if time.time() - start_time > 0.3:
                        start_time = time.time()
                        self.downloadChanged.emit(file_name, trans_size(speed), current, total)
                    else:
                        QtWidgets.QApplication.processEvents()

            path = QtWidgets.QFileDialog.getExistingDirectory(
                self, "选择保存文件夹", "./")
            if not path:
                return
            # assignment.attachment_save(attach_type, path)
            # 后台下载
            with ThreadPoolExecutor() as executor:
                work = executor.submit(thread_func, path)
                while not work.done():
                    QtWidgets.QApplication.processEvents()

        self.back_button.show()
        self.title_in_assignment.setText(assignment.title)
        self.start_time.setText(assignment.str_start_time)
        self.end_time.setText(assignment.str_end_time)
        self.range.setText(assignment.student_range)
        fontMetrics = self.range.fontMetrics()
        if fontMetrics.width(self.range.text()) > self.range.width():
            elidedText = fontMetrics.elidedText(
                self.range.text(), QtCore.Qt.ElideRight, self.range.width())
            self.range.setText(elidedText)
            self.range.setToolTip(assignment.student_range)
        self.course.setText("(" + assignment.course.course_name + ")")

        if assignment.description.strip():
            self.assignment_des.show()
            self.des_label.show()
            self.assignment_des.setText(assignment.description)
        else:
            self.assignment_des.hide()
            self.des_label.hide()

        if assignment.attachment_id:
            self.attachment.show()
            self.attachment_label.show()
            self.attachment.clicked.disconnect()
            self.attachment.clicked.connect(lambda: _download_attachment(1))
        else:
            self.attachment.hide()
            self.attachment_label.hide()

        if assignment.answer_description.strip():
            self.answer.show()
            self.answer_label.show()
            self.answer.setText(assignment.answer_description)
        else:
            self.answer.hide()
            self.answer_label.hide()

        if assignment.answer_attachment_id:
            self.answer_attachment.show()
            self.answer_attachment_label.show()
            self.answer_attachment.clicked.disconnect()
            self.answer_attachment.clicked.connect(
                lambda: _download_attachment(4)
            )
        else:
            self.answer_attachment.hide()
            self.answer_attachment_label.hide()

        if assignment.grade:
            self.grade.show()
            self.grade_label.show()
            self.grade_time.show()
            self.grade_time_label.show()
            self.grade.setText(str(assignment.grade))
            self.grade_time.setText(str(assignment.grade_time))
        else:
            self.grade.hide()
            self.grade_label.hide()
            self.grade_time.hide()
            self.grade_time_label.hide()

        if assignment.comment:
            self.comment.show()
            self.comment_label.show()
            self.comment.setText(assignment.comment)
        else:
            self.comment.hide()
            self.comment_label.hide()

        if assignment.comment_attachment_id:
            self.comment_attachment.show()
            self.comment_attachment_label.show()
            self.comment_attachment.clicked.disconnect()
            self.comment_attachment.clicked.connect(
                lambda: _download_attachment(3)
            )
        else:
            self.comment_attachment.hide()
            self.comment_attachment_label.hide()

        if assignment.teacher:
            self.teacher.show()
            self.teacher_label.show()
            self.teacher.setText(assignment.teacher)
        else:
            self.teacher.hide()
            self.teacher_label.hide()

        if assignment.submit_time:
            self.submit_time.show()
            self.submit_time_label.show()
            self.submit_label.show()
            self.submit_time.setText(assignment.str_submit_time)
        else:
            self.submit_time.hide()
            self.submit_time_label.hide()
            self.submit_label.hide()

        if assignment.submit_attachment_id:
            self.submit_attachment.show()
            self.submit_attachment.clicked.disconnect()
            self.submit_attachment.clicked.connect(
                lambda: _download_attachment(2)
            )
        else:
            self.submit_attachment.hide()

        self.mainWidget.setCurrentIndex(5)

    def _showDownloadWindow(self):
        self.downloadWindow.move(
            self.download_button.x() - self.downloadWindow.width() // 2 - 40,
            self.download_button.y() + self.download_button.height() + 5
        )
        if self.download_button.isChecked():
            self.downloadWindow.show()
        else:
            self.downloadWindow.hide()

    def _showDownload(self, file_name: str, path: str):
        self.download_button.setChecked(True)
        self._showDownloadWindow()
        self.downloadWindow.insert_download(file_name, path + "/" + file_name)

    def _updateDownload(self, file_name: str, speed: str, current: int, total: int):
        self.downloadWindow.set_speed(
            file_name,
            speed + "/s" if speed != "下载完成√" else speed,
        )
        self.downloadWindow.set_current_and_total(
            file_name,
            trans_size(current) + "/" + trans_size(total)
            if current != total else trans_size(total)
        )
        self.downloadWindow.set_percent(
            file_name,
            "{:.2f}%".format(current / total * 100)
        )
        self.downloadWindow.set_progress(
            file_name,
            int(current / total * 100)
        )

    def _downloadFile(self, file: spider.File):
        def thread_func(path):
            result = file.save(path)
            file_name = next(result)
            total = next(result)
            self.downloadSignal.emit(file_name, path)
            start_time = time.time()
            for speed, current in result:
                QtWidgets.QApplication.processEvents()
                if current == total:
                    self.downloadChanged.emit(file_name, "下载完成√", total, total)
                    break
                if time.time() - start_time > 0.3:
                    start_time = time.time()
                    self.downloadChanged.emit(file_name, trans_size(speed), current, total)
                else:
                    QtWidgets.QApplication.processEvents()

        path = QtWidgets.QFileDialog.getExistingDirectory(self, "选择保存文件夹")
        if not path:
            return
        # file.save(path)
        # 后台下载
        with ThreadPoolExecutor() as executor:
            work = executor.submit(thread_func, path)
            # 处理事件循环
            while not work.done():
                QtWidgets.QApplication.processEvents()

    def _initPivot(self):
        def _course_notice_list_update():
            self.course_notice_list.clear()
            for notice in self.notices:
                if notice.course == self.course_in_detail_widget:
                    self.course_notice_list.insert_notice(notice)
            for notice in self.course_notice_list.notices:
                notice.notice_clicked.connect(self._showNoticeDetail)
            self.detail_widget.setCurrentIndex(1)
        self.course_pivot.insertItem(
            0,
            "Notice",
            "课程公告",
            _course_notice_list_update
        )

        def _course_assignment_list_update():
            self.course_assignment_list.clear()
            for assignment in self.assignments:
                if assignment.course == self.course_in_detail_widget:
                    self.course_assignment_list.insert_assignment(assignment)
            for assignment in self.course_assignment_list.assignments:
                assignment.assignment_clicked.connect(
                    self._showAssignmentDetail)
            self.course_assignment_pivot.setCurrentItem("WJ")
            _course_assignment_wj_list()
            self.detail_widget.setCurrentIndex(0)
        self.course_pivot.insertItem(
            1,
            "Homework",
            "课程作业",
            _course_assignment_list_update
        )

        def _course_assignment_wj_list():
            self.course_assignment_page_ScrollArea.verticalScrollBar().setValue(0)
            self.course_assignment_list.empty.hide()
            self.course_assignment_list.empty_text.hide()
            for assignment in self.course_assignment_list.assignments:
                if assignment._assignment.state == 1:
                    assignment.show()
                else:
                    assignment.hide()
        self.course_assignment_pivot.insertItem(
            0,
            "WJ",
            "未交",
            _course_assignment_wj_list
        )

        def _course_assignment_yjwg_list():
            self.course_assignment_page_ScrollArea.verticalScrollBar().setValue(0)
            self.course_assignment_list.empty.hide()
            self.course_assignment_list.empty_text.hide()
            for assignment in self.course_assignment_list.assignments:
                if assignment._assignment.state == 2:
                    assignment.show()
                else:
                    assignment.hide()
        self.course_assignment_pivot.insertItem(
            1,
            "YJWG",
            "已提交未批改",
            _course_assignment_yjwg_list
        )

        def _course_assignment_ypg_list():
            self.course_assignment_page_ScrollArea.verticalScrollBar().setValue(0)
            self.course_assignment_list.empty.hide()
            self.course_assignment_list.empty_text.hide()
            for assignment in self.course_assignment_list.assignments:
                if assignment._assignment.state == 3:
                    assignment.show()
                else:
                    assignment.hide()
        self.course_assignment_pivot.insertItem(
            2,
            "YPG",
            "已批改",
            _course_assignment_ypg_list
        )

        def _course_file_list_update():
            self.course_file_list.clear()
            for file in self.files:
                if file.course == self.course_in_detail_widget:
                    self.course_file_list.insert_file(file)
            for file in self.course_file_list.files:
                file.file_clicked.connect(self._downloadFile)
            self.detail_widget.setCurrentIndex(2)
        self.course_pivot.insertItem(
            2,
            "File",
            "课程文件",
            _course_file_list_update
        )
        self.course_pivot.setCurrentItem("Notice")
        self.detail_widget.setCurrentIndex(1)

        def _assignment_wj_list():
            self.assignment_scrollArea.verticalScrollBar().setValue(0)
            self.assignment_list.empty.hide()
            self.assignment_list.empty_text.hide()
            for assignment in self.assignment_list.assignments:
                if assignment._assignment.state == 1:
                    assignment.show()
                else:
                    assignment.hide()
        self.assignment_pivot.insertItem(
            0,
            "WJ",
            "未交",
            _assignment_wj_list
        )

        def _assignment_yjwg_list():
            self.assignment_scrollArea.verticalScrollBar().setValue(0)
            self.assignment_list.empty.hide()
            self.assignment_list.empty_text.hide()
            for assignment in self.assignment_list.assignments:
                if assignment._assignment.state == 2:
                    assignment.show()
                else:
                    assignment.hide()
        self.assignment_pivot.insertItem(
            1,
            "YJWG",
            "已提交未批改",
            _assignment_yjwg_list
        )

        def _assignment_ypg_list():
            self.assignment_scrollArea.verticalScrollBar().setValue(0)
            self.assignment_list.empty.hide()
            self.assignment_list.empty_text.hide()
            for assignment in self.assignment_list.assignments:
                if assignment._assignment.state == 3:
                    assignment.show()
                else:
                    assignment.hide()
        self.assignment_pivot.insertItem(
            2,
            "YPG",
            "已批改",
            _assignment_ypg_list
        )
        self.assignment_pivot.setCurrentItem("WJ")

    def _initMenu(self):
        self.mainWidget.setCurrentIndex(0)
        self.menu.addItem(
            "Notice",
            FluentIcon("Message"),
            "课程公告",
            self._showNotice
        )
        self.menu.addItem(
            "Homework",
            FluentIcon("Calendar"),
            "课程作业",
            self._showAssignment
        )
        self.menu.addItem(
            "File",
            FluentIcon("Document"),
            "课程文件",
            self._showFile
        )
        self.menu.addItem(
            "Course",
            FluentIcon("BookShelf"),
            "课程列表",
            self._showCourse
        )
        self.menu.addItem(
            "Settings",
            FluentIcon("Setting"),
            "设置",
            lambda: self.mainWidget.setCurrentIndex(7)
        )
        # self.menu.addItem(
        #     "About",
        #     FluentIcon("Info"),
        #     "关于"
        # )
        self.menu.setCurrentItem("Notice")

    def _initSettings(self):
        self.setting_page.brightness.checkedChanged.connect(self._changeTheme)
        self.setting_page.logout.clicked.connect(self._logout)
        self.setting_page.insertSemester(self.student.semesters)
        self.setting_page.semesterChanged.connect(self._changeSemester)
        self.setting_page.insertVersionInfo(self.version)
        self.setting_page.download_new_version.connect(lambda filename, path: self.downloadSignal.emit(filename, path))
        self.setting_page.download_progress.connect(lambda filename, speed, current, total: self.downloadChanged.emit(filename, speed, current, total))

    def _changeSemester(self, semester: str):
        waitRing = StateToolTip("正在切换...", "请耐心等待", parent=self)
        # 移动到父窗口中间
        waitRing.move(
            self.width() // 2 - waitRing.width() // 2,
            60
        )
        waitRing.show()
        waitRing.closeButton.hide()
        self.student.semester = semester
        self.courses = self.student.courses
        self.course_list.clear()
        self._updateAll()
        waitRing.setState(True)

    def _logout(self):
        self.logoutSignal.emit()

    def _changeTheme(self, dark: bool):
        if dark:
            self.theme = Theme.DARK
            self.mainFrame.setStyleSheet(
                "background-color: #444449; color: #ffffff;")
            self.course_notice_list.empty.setImage(
                QtGui.QImage(":/empty_night"))
            self.course_assignment_list.empty.setImage(
                QtGui.QImage(":/empty_night"))
            self.course_file_list.empty.setImage(QtGui.QImage(":/empty_night"))
            self.notice_list.empty.setImage(QtGui.QImage(":/empty_night"))
            self.assignment_list.empty.setImage(QtGui.QImage(":/empty_night"))
            self.file_list.empty.setImage(QtGui.QImage(":/empty_night"))
            self.downloadWindow._changeTheme("dark")
        else:
            self.theme = Theme.LIGHT
            self.mainFrame.setStyleSheet("")
            self.course_notice_list.empty.setImage(QtGui.QImage(":/empty"))
            self.course_assignment_list.empty.setImage(QtGui.QImage(":/empty"))
            self.course_file_list.empty.setImage(QtGui.QImage(":/empty"))
            self.notice_list.empty.setImage(QtGui.QImage(":/empty"))
            self.assignment_list.empty.setImage(QtGui.QImage(":/empty"))
            self.file_list.empty.setImage(QtGui.QImage(":/empty"))
            self.downloadWindow._changeTheme("light")
        setTheme(self.theme)

    def maximizeWindow(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def minimizeWindow(self):
        self.setMinimumSize(0, 0)

        if self.showDirection == "left":
            self.animition_1.setEndValue(
                QtCore.QRect(self.pos(), QtCore.QSize(5, 5)))
        else:
            self.animition_1.setEndValue(QtCore.QRect(
                QtCore.QPoint(self.pos().x() + self.width() -
                              5, self.pos().y()),
                QtCore.QSize(5, 5)
            ))

        self.animition_1.start()

        self.animition_2.setEndValue(0)
        self.animition_2.start()

    def _showNormal(self, pos: QtCore.QPoint):
        screen_center = QtWidgets.QApplication.desktop().screenGeometry().center()

        self.move(pos)
        self.show()

        if pos.x() > screen_center.x():
            self.showDirection = "right"
            endRect = QtCore.QRect(pos.x() - 950, pos.y(), 950, 650)
        else:
            self.showDirection = "left"
            endRect = QtCore.QRect(pos.x(), pos.y(), 950, 650)

        self.animition_3.setEndValue(endRect)
        self.animition_3.start()

        self.animition_4.setEndValue(1)
        self.animition_4.start()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.downloadWindow.isVisible():
                if not self.downloadWindow.geometry().contains(event.pos()):
                    self.download_button.setChecked(False)
                    self.downloadWindow.hide()
            self.dragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    student = Student()
    ui = MainWindow(student)
    ui.show()
    sys.exit(app.exec_())
