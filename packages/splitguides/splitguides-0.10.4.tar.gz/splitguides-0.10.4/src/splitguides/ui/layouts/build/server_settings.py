# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'server_settings.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFormLayout, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QToolButton, QWidget)

class Ui_ServerSettings(object):
    def setupUi(self, ServerSettings):
        if not ServerSettings.objectName():
            ServerSettings.setObjectName(u"ServerSettings")
        ServerSettings.resize(400, 535)
        self.gridLayout = QGridLayout(ServerSettings)
        self.gridLayout.setObjectName(u"gridLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(5, 5, 5, 5)
        self.hostname_label = QLabel(ServerSettings)
        self.hostname_label.setObjectName(u"hostname_label")
        font = QFont()
        font.setPointSize(10)
        self.hostname_label.setFont(font)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.hostname_label)

        self.hostname_edit = QLineEdit(ServerSettings)
        self.hostname_edit.setObjectName(u"hostname_edit")
        self.hostname_edit.setFont(font)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.hostname_edit)

        self.port_label = QLabel(ServerSettings)
        self.port_label.setObjectName(u"port_label")
        self.port_label.setFont(font)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.port_label)

        self.port_edit = QLineEdit(ServerSettings)
        self.port_edit.setObjectName(u"port_edit")
        self.port_edit.setFont(font)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.port_edit)

        self.divider_1 = QFrame(ServerSettings)
        self.divider_1.setObjectName(u"divider_1")
        self.divider_1.setFrameShape(QFrame.Shape.HLine)
        self.divider_1.setFrameShadow(QFrame.Shadow.Sunken)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.divider_1)

        self.previous_label = QLabel(ServerSettings)
        self.previous_label.setObjectName(u"previous_label")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.previous_label)

        self.previous_edit = QLineEdit(ServerSettings)
        self.previous_edit.setObjectName(u"previous_edit")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.previous_edit)

        self.advance_label = QLabel(ServerSettings)
        self.advance_label.setObjectName(u"advance_label")
        self.advance_label.setFont(font)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.advance_label)

        self.advance_edit = QLineEdit(ServerSettings)
        self.advance_edit.setObjectName(u"advance_edit")
        self.advance_edit.setFont(font)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.advance_edit)

        self.separator_label = QLabel(ServerSettings)
        self.separator_label.setObjectName(u"separator_label")
        self.separator_label.setFont(font)

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.separator_label)

        self.separator_edit = QLineEdit(ServerSettings)
        self.separator_edit.setObjectName(u"separator_edit")
        self.separator_edit.setFont(font)

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.separator_edit)

        self.divider_2 = QFrame(ServerSettings)
        self.divider_2.setObjectName(u"divider_2")
        self.divider_2.setFrameShape(QFrame.Shape.HLine)
        self.divider_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.formLayout.setWidget(6, QFormLayout.ItemRole.SpanningRole, self.divider_2)

        self.fontsize_label = QLabel(ServerSettings)
        self.fontsize_label.setObjectName(u"fontsize_label")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.LabelRole, self.fontsize_label)

        self.fontsize_edit = QLineEdit(ServerSettings)
        self.fontsize_edit.setObjectName(u"fontsize_edit")

        self.formLayout.setWidget(7, QFormLayout.ItemRole.FieldRole, self.fontsize_edit)

        self.textcolor_label = QLabel(ServerSettings)
        self.textcolor_label.setObjectName(u"textcolor_label")

        self.formLayout.setWidget(8, QFormLayout.ItemRole.LabelRole, self.textcolor_label)

        self.textcolor_layout = QHBoxLayout()
        self.textcolor_layout.setObjectName(u"textcolor_layout")
        self.textcolor_edit = QLineEdit(ServerSettings)
        self.textcolor_edit.setObjectName(u"textcolor_edit")

        self.textcolor_layout.addWidget(self.textcolor_edit)

        self.textcolor_button = QPushButton(ServerSettings)
        self.textcolor_button.setObjectName(u"textcolor_button")

        self.textcolor_layout.addWidget(self.textcolor_button)


        self.formLayout.setLayout(8, QFormLayout.ItemRole.FieldRole, self.textcolor_layout)

        self.bgcolor_label = QLabel(ServerSettings)
        self.bgcolor_label.setObjectName(u"bgcolor_label")

        self.formLayout.setWidget(9, QFormLayout.ItemRole.LabelRole, self.bgcolor_label)

        self.bgcolor_layout = QHBoxLayout()
        self.bgcolor_layout.setObjectName(u"bgcolor_layout")
        self.bgcolor_edit = QLineEdit(ServerSettings)
        self.bgcolor_edit.setObjectName(u"bgcolor_edit")

        self.bgcolor_layout.addWidget(self.bgcolor_edit)

        self.bgcolor_button = QPushButton(ServerSettings)
        self.bgcolor_button.setObjectName(u"bgcolor_button")

        self.bgcolor_layout.addWidget(self.bgcolor_button)


        self.formLayout.setLayout(9, QFormLayout.ItemRole.FieldRole, self.bgcolor_layout)

        self.divider_3 = QFrame(ServerSettings)
        self.divider_3.setObjectName(u"divider_3")
        self.divider_3.setFrameShape(QFrame.Shape.HLine)
        self.divider_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.formLayout.setWidget(10, QFormLayout.ItemRole.SpanningRole, self.divider_3)

        self.htmltemplate_label = QLabel(ServerSettings)
        self.htmltemplate_label.setObjectName(u"htmltemplate_label")

        self.formLayout.setWidget(11, QFormLayout.ItemRole.LabelRole, self.htmltemplate_label)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.htmltemplate_edit = QLineEdit(ServerSettings)
        self.htmltemplate_edit.setObjectName(u"htmltemplate_edit")
        self.htmltemplate_edit.setEnabled(False)

        self.horizontalLayout.addWidget(self.htmltemplate_edit)

        self.htmltemplate_button = QToolButton(ServerSettings)
        self.htmltemplate_button.setObjectName(u"htmltemplate_button")

        self.horizontalLayout.addWidget(self.htmltemplate_button)


        self.formLayout.setLayout(11, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)

        self.css_label = QLabel(ServerSettings)
        self.css_label.setObjectName(u"css_label")

        self.formLayout.setWidget(12, QFormLayout.ItemRole.LabelRole, self.css_label)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.css_edit = QLineEdit(ServerSettings)
        self.css_edit.setObjectName(u"css_edit")
        self.css_edit.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.css_edit)

        self.css_button = QToolButton(ServerSettings)
        self.css_button.setObjectName(u"css_button")

        self.horizontalLayout_2.addWidget(self.css_button)


        self.formLayout.setLayout(12, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_2)

        self.divider_4 = QFrame(ServerSettings)
        self.divider_4.setObjectName(u"divider_4")
        self.divider_4.setFrameShape(QFrame.Shape.HLine)
        self.divider_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.formLayout.setWidget(13, QFormLayout.ItemRole.SpanningRole, self.divider_4)

        self.nextsplitkey_label = QLabel(ServerSettings)
        self.nextsplitkey_label.setObjectName(u"nextsplitkey_label")

        self.formLayout.setWidget(14, QFormLayout.ItemRole.LabelRole, self.nextsplitkey_label)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.nextsplitkey_edit = QLineEdit(ServerSettings)
        self.nextsplitkey_edit.setObjectName(u"nextsplitkey_edit")
        self.nextsplitkey_edit.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.nextsplitkey_edit)

        self.nextsplitkey_button = QPushButton(ServerSettings)
        self.nextsplitkey_button.setObjectName(u"nextsplitkey_button")

        self.horizontalLayout_3.addWidget(self.nextsplitkey_button)


        self.formLayout.setLayout(14, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_3)

        self.previoussplitkey_label = QLabel(ServerSettings)
        self.previoussplitkey_label.setObjectName(u"previoussplitkey_label")

        self.formLayout.setWidget(15, QFormLayout.ItemRole.LabelRole, self.previoussplitkey_label)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.previoussplitkey_edit = QLineEdit(ServerSettings)
        self.previoussplitkey_edit.setObjectName(u"previoussplitkey_edit")
        self.previoussplitkey_edit.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.previoussplitkey_edit)

        self.previoussplitkey_button = QPushButton(ServerSettings)
        self.previoussplitkey_button.setObjectName(u"previoussplitkey_button")

        self.horizontalLayout_4.addWidget(self.previoussplitkey_button)


        self.formLayout.setLayout(15, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_4)

        self.noteserverhost_label = QLabel(ServerSettings)
        self.noteserverhost_label.setObjectName(u"noteserverhost_label")

        self.formLayout.setWidget(17, QFormLayout.ItemRole.LabelRole, self.noteserverhost_label)

        self.noteserverhost_edit = QLineEdit(ServerSettings)
        self.noteserverhost_edit.setObjectName(u"noteserverhost_edit")

        self.formLayout.setWidget(17, QFormLayout.ItemRole.FieldRole, self.noteserverhost_edit)

        self.noteserverport_label = QLabel(ServerSettings)
        self.noteserverport_label.setObjectName(u"noteserverport_label")

        self.formLayout.setWidget(18, QFormLayout.ItemRole.LabelRole, self.noteserverport_label)

        self.noteserverport_edit = QLineEdit(ServerSettings)
        self.noteserverport_edit.setObjectName(u"noteserverport_edit")

        self.formLayout.setWidget(18, QFormLayout.ItemRole.FieldRole, self.noteserverport_edit)

        self.divider_5 = QFrame(ServerSettings)
        self.divider_5.setObjectName(u"divider_5")
        self.divider_5.setFrameShape(QFrame.Shape.HLine)
        self.divider_5.setFrameShadow(QFrame.Shadow.Sunken)

        self.formLayout.setWidget(16, QFormLayout.ItemRole.SpanningRole, self.divider_5)


        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)

        self.confirm_cancel_box = QDialogButtonBox(ServerSettings)
        self.confirm_cancel_box.setObjectName(u"confirm_cancel_box")
        self.confirm_cancel_box.setFont(font)
        self.confirm_cancel_box.setOrientation(Qt.Horizontal)
        self.confirm_cancel_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.confirm_cancel_box, 1, 0, 1, 1)

        QWidget.setTabOrder(self.hostname_edit, self.port_edit)
        QWidget.setTabOrder(self.port_edit, self.previous_edit)
        QWidget.setTabOrder(self.previous_edit, self.advance_edit)
        QWidget.setTabOrder(self.advance_edit, self.separator_edit)
        QWidget.setTabOrder(self.separator_edit, self.fontsize_edit)
        QWidget.setTabOrder(self.fontsize_edit, self.textcolor_edit)
        QWidget.setTabOrder(self.textcolor_edit, self.textcolor_button)
        QWidget.setTabOrder(self.textcolor_button, self.bgcolor_edit)
        QWidget.setTabOrder(self.bgcolor_edit, self.bgcolor_button)
        QWidget.setTabOrder(self.bgcolor_button, self.htmltemplate_edit)
        QWidget.setTabOrder(self.htmltemplate_edit, self.htmltemplate_button)
        QWidget.setTabOrder(self.htmltemplate_button, self.css_edit)
        QWidget.setTabOrder(self.css_edit, self.css_button)
        QWidget.setTabOrder(self.css_button, self.nextsplitkey_edit)
        QWidget.setTabOrder(self.nextsplitkey_edit, self.nextsplitkey_button)
        QWidget.setTabOrder(self.nextsplitkey_button, self.previoussplitkey_edit)
        QWidget.setTabOrder(self.previoussplitkey_edit, self.previoussplitkey_button)
        QWidget.setTabOrder(self.previoussplitkey_button, self.noteserverhost_edit)
        QWidget.setTabOrder(self.noteserverhost_edit, self.noteserverport_edit)

        self.retranslateUi(ServerSettings)

        QMetaObject.connectSlotsByName(ServerSettings)
    # setupUi

    def retranslateUi(self, ServerSettings):
        ServerSettings.setWindowTitle(QCoreApplication.translate("ServerSettings", u"SplitGuides Server Settings", None))
        self.hostname_label.setText(QCoreApplication.translate("ServerSettings", u"Livesplit Server Hostname:", None))
        self.hostname_edit.setText(QCoreApplication.translate("ServerSettings", u"localhost", None))
        self.port_label.setText(QCoreApplication.translate("ServerSettings", u"Livesplit Server Port:", None))
        self.port_edit.setText(QCoreApplication.translate("ServerSettings", u"16834", None))
        self.previous_label.setText(QCoreApplication.translate("ServerSettings", u"Show Previous Splits:", None))
        self.previous_edit.setText(QCoreApplication.translate("ServerSettings", u"0", None))
        self.advance_label.setText(QCoreApplication.translate("ServerSettings", u"Show Next Splits:", None))
        self.advance_edit.setText(QCoreApplication.translate("ServerSettings", u"2", None))
        self.separator_label.setText(QCoreApplication.translate("ServerSettings", u"Split Separator:", None))
#if QT_CONFIG(tooltip)
        self.separator_edit.setToolTip(QCoreApplication.translate("ServerSettings", u"Leave blank for empty line as separator", None))
#endif // QT_CONFIG(tooltip)
        self.separator_edit.setPlaceholderText(QCoreApplication.translate("ServerSettings", u"Empty line", None))
        self.fontsize_label.setText(QCoreApplication.translate("ServerSettings", u"Font Size:", None))
        self.textcolor_label.setText(QCoreApplication.translate("ServerSettings", u"Text Colour:", None))
        self.textcolor_button.setText(QCoreApplication.translate("ServerSettings", u"Select", None))
        self.bgcolor_label.setText(QCoreApplication.translate("ServerSettings", u"Background Colour:", None))
        self.bgcolor_button.setText(QCoreApplication.translate("ServerSettings", u"Select", None))
        self.htmltemplate_label.setText(QCoreApplication.translate("ServerSettings", u"HTML Template:", None))
        self.htmltemplate_button.setText(QCoreApplication.translate("ServerSettings", u"...", None))
        self.css_label.setText(QCoreApplication.translate("ServerSettings", u"CSS:", None))
        self.css_button.setText(QCoreApplication.translate("ServerSettings", u"...", None))
        self.nextsplitkey_label.setText(QCoreApplication.translate("ServerSettings", u"Next Split Hotkey:", None))
        self.nextsplitkey_button.setText(QCoreApplication.translate("ServerSettings", u"Select", None))
        self.previoussplitkey_label.setText(QCoreApplication.translate("ServerSettings", u"Previous Split Hotkey:", None))
        self.previoussplitkey_button.setText(QCoreApplication.translate("ServerSettings", u"Select", None))
        self.noteserverhost_label.setText(QCoreApplication.translate("ServerSettings", u"Note Server Hostname:", None))
        self.noteserverport_label.setText(QCoreApplication.translate("ServerSettings", u"Note Server Port:", None))
    # retranslateUi

