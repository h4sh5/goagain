#!/usr/bin/env python3
import sys

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
	QApplication,
	QLabel,
	QLineEdit,
	QTextEdit,
	QMainWindow,
	QVBoxLayout,
	QHBoxLayout,
	QWidget,
	QCheckBox,
	QPushButton,
	QGridLayout,
	QTabWidget,
)

class ReplayerWidget(QWidget):
	def __init__(self):
		super().__init__()
		self.replayer_tab_layout = QVBoxLayout(self)

		self.address_label = QLabel()
		self.address_label.setText("URL or host:port")

		self.tls_label = QLabel("TLS")
		self.tls_checkbox = QCheckBox()
		self.address_input = QLineEdit()


		self.send_button = QPushButton()
		self.send_button.setText("send")

		self.request_input = QTextEdit()
		self.response_input = QTextEdit(readOnly=True)

		self.vbox_layout = QVBoxLayout()
		self.replayer_tab_layout.addWidget(self.address_label)
		self.replayer_tab_layout.addWidget(self.address_input)

		hbox1 = QHBoxLayout()
		hbox1.addStretch()
		hbox1.addWidget(self.tls_label)
		hbox1.addWidget(self.tls_checkbox)
		hbox1.addWidget(self.send_button)


		
		self.replayer_tab_layout.addLayout(hbox1)

		self.side_by_side_pane = QHBoxLayout()
		self.side_by_side_pane.addWidget(self.request_input)
		self.side_by_side_pane.addWidget(self.response_input)
		self.replayer_tab_layout.addLayout(self.side_by_side_pane)

class AddTabWidget(QWidget):
	def __init__(self):
		super().__init__()

class MainWindow(QMainWindow):

	def _add_replayer_tab(self):
		# if the + tab is changed, add a new tab
		if self.replayer_tabwidget.tabText(self.replayer_tabwidget.currentIndex()) == '+':
			newIndex = self.replayer_tabwidget.count()-1
			self.replayer_tabwidget.insertTab(newIndex, ReplayerWidget(), str(self.replayer_tabwidget.count()))
			self.replayer_tabwidget.setCurrentIndex(newIndex)


	def __init__(self):
		super().__init__()


		self.setWindowTitle("GoAgain!")
		# self.main_layout = QGridLayout(self)
		self.main_tab_widget = QTabWidget()

		# replayer page
		replayer_page = QWidget(self)
		# replayers also contain tabs
		self.replayer_tabwidget = QTabWidget()
		self.replayer_tabs_grid_layout = QGridLayout()
		self.replayer_tabs_grid_layout.addWidget(self.replayer_tabwidget)
		self.tab1 = ReplayerWidget()
		self.tab2 = ReplayerWidget()
		self.replayer_tabwidget.addTab(self.tab1,'1')
		self.replayer_tabwidget.addTab(self.tab2,'2')
		new_tab_widget = AddTabWidget()
		# new_tab_widget.setParent()
		self.replayer_tabwidget.addTab(new_tab_widget,'+')
		self.replayer_tabwidget.currentChanged.connect(self._add_replayer_tab) 
		replayer_page.setLayout(self.replayer_tabs_grid_layout)


		# about page
		about_page = QWidget(self)
		about_page_layout = QVBoxLayout()
		about_label = QLabel()
		about_label.setText("GoAgain! is Free and Open Source Software.")
		about_page_layout.addWidget(about_label)
		about_page_layout.addStretch()
		about_page.setLayout(about_page_layout)

		self.main_tab_widget.addTab(replayer_page, 'Replayer')
		self.main_tab_widget.addTab(about_page, 'About')


		# self.replayer_tabwidget.movePlusButton()

		# container = QWidget()
		self.setCentralWidget(self.main_tab_widget)

app = QApplication(sys.argv)

window = MainWindow()
window.resize(800,700)
window.show()


app.exec()
