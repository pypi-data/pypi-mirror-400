# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'search_translation_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog, QFormLayout,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTableWidget,
    QTableWidgetItem, QWidget)

class Ui_SearchTranslationDialog(object):
    def setupUi(self, SearchTranslationDialog):
        if not SearchTranslationDialog.objectName():
            SearchTranslationDialog.setObjectName(u"SearchTranslationDialog")
        SearchTranslationDialog.resize(498, 444)
        self.gridLayout_2 = QGridLayout(SearchTranslationDialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self._3 = QHBoxLayout()
        self._3.setObjectName(u"_3")
        self.pickButton = QPushButton(SearchTranslationDialog)
        self.pickButton.setObjectName(u"pickButton")

        self._3.addWidget(self.pickButton)

        self.addButton = QPushButton(SearchTranslationDialog)
        self.addButton.setObjectName(u"addButton")

        self._3.addWidget(self.addButton)

        self.editButton = QPushButton(SearchTranslationDialog)
        self.editButton.setObjectName(u"editButton")

        self._3.addWidget(self.editButton)

        self.deleteButton = QPushButton(SearchTranslationDialog)
        self.deleteButton.setObjectName(u"deleteButton")

        self._3.addWidget(self.deleteButton)


        self.gridLayout_2.addLayout(self._3, 3, 0, 1, 1)

        self.matches = QTableWidget(SearchTranslationDialog)
        if (self.matches.columnCount() < 3):
            self.matches.setColumnCount(3)
        __qtablewidgetitem = QTableWidgetItem()
        self.matches.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.matches.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.matches.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        self.matches.setObjectName(u"matches")
        self.matches.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.matches.setTabKeyNavigation(False)
        self.matches.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.matches.horizontalHeader().setStretchLastSection(True)

        self.gridLayout_2.addWidget(self.matches, 2, 0, 1, 1)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.outputLabel = QLabel(SearchTranslationDialog)
        self.outputLabel.setObjectName(u"outputLabel")
        self.outputLabel.setTextFormat(Qt.AutoText)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.outputLabel)

        self.output = QLineEdit(SearchTranslationDialog)
        self.output.setObjectName(u"output")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.output)

        self.descriptionLabel = QLabel(SearchTranslationDialog)
        self.descriptionLabel.setObjectName(u"descriptionLabel")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.descriptionLabel)

        self.description = QLineEdit(SearchTranslationDialog)
        self.description.setObjectName(u"description")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.description)

        self.briefLabel = QLabel(SearchTranslationDialog)
        self.briefLabel.setObjectName(u"briefLabel")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.briefLabel)

        self.brief = QLineEdit(SearchTranslationDialog)
        self.brief.setObjectName(u"brief")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.brief)


        self.gridLayout_2.addLayout(self.formLayout, 0, 0, 1, 1)

        self.briefConflictLabel = QLabel(SearchTranslationDialog)
        self.briefConflictLabel.setObjectName(u"briefConflictLabel")
        self.briefConflictLabel.setMinimumSize(QSize(0, 40))
        self.briefConflictLabel.setTextFormat(Qt.RichText)

        self.gridLayout_2.addWidget(self.briefConflictLabel, 1, 0, 1, 1)

#if QT_CONFIG(shortcut)
        self.outputLabel.setBuddy(self.output)
        self.descriptionLabel.setBuddy(self.description)
        self.briefLabel.setBuddy(self.brief)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.description, self.brief)
        QWidget.setTabOrder(self.brief, self.output)
        QWidget.setTabOrder(self.output, self.matches)
        QWidget.setTabOrder(self.matches, self.pickButton)
        QWidget.setTabOrder(self.pickButton, self.addButton)
        QWidget.setTabOrder(self.addButton, self.editButton)
        QWidget.setTabOrder(self.editButton, self.deleteButton)

        self.retranslateUi(SearchTranslationDialog)

        QMetaObject.connectSlotsByName(SearchTranslationDialog)
    # setupUi

    def retranslateUi(self, SearchTranslationDialog):
        SearchTranslationDialog.setWindowTitle(QCoreApplication.translate("SearchTranslationDialog", u"Search Translation", None))
        self.pickButton.setText(QCoreApplication.translate("SearchTranslationDialog", u"&Pick", None))
#if QT_CONFIG(tooltip)
        self.addButton.setToolTip(QCoreApplication.translate("SearchTranslationDialog", u"Fill values in the 3 text boxes, then click this button.", None))
#endif // QT_CONFIG(tooltip)
        self.addButton.setText(QCoreApplication.translate("SearchTranslationDialog", u"&Add", None))
#if QT_CONFIG(tooltip)
        self.editButton.setToolTip(QCoreApplication.translate("SearchTranslationDialog", u"Move the content of the currently selected row to the text boxes.", None))
#endif // QT_CONFIG(tooltip)
        self.editButton.setText(QCoreApplication.translate("SearchTranslationDialog", u"&Edit", None))
#if QT_CONFIG(tooltip)
        self.deleteButton.setToolTip(QCoreApplication.translate("SearchTranslationDialog", u"Delete the currently selected row.", None))
#endif // QT_CONFIG(tooltip)
        self.deleteButton.setText(QCoreApplication.translate("SearchTranslationDialog", u"&Delete", None))
        ___qtablewidgetitem = self.matches.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("SearchTranslationDialog", u"Output", None));
        ___qtablewidgetitem1 = self.matches.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("SearchTranslationDialog", u"Description", None));
        ___qtablewidgetitem2 = self.matches.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("SearchTranslationDialog", u"Brief", None));
        self.outputLabel.setText(QCoreApplication.translate("SearchTranslationDialog", u"&Output:", None))
        self.descriptionLabel.setText(QCoreApplication.translate("SearchTranslationDialog", u"Des&cription:", None))
        self.briefLabel.setText(QCoreApplication.translate("SearchTranslationDialog", u"&Brief:", None))
    # retranslateUi

