#!/usr/bin/env python3
import sys

from PySide6.QtCore import QSize, Qt # , QRunnable, QThreadPool, Slot
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
import socket
import ssl
import time
from multiprocessing.pool import ThreadPool

def elog(s, *args, **kwargs):
	print(s, *args, **kwargs, file=sys.stderr)

class History():

	def __init__(self, tab_name, address, tls_enable, request_body, response_body, time):
		self.tab_name = tab_name
		self.address = address
		self.tls_enable = tls_enable
		self.request_body = request_body
		self.response_body = response_body
		self.time = time


class ReplayerWidget(QWidget):

	def send_request(self):
		lstart = time.time()
		elog("request worker start:",lstart)
		encoding = 'utf-8'
		
		timeout = 10
		tls = self.tls_checkbox.checkState() == Qt.Checked
		req_body = self.request_input.toPlainText()
		host_port = self.address_input.text()
		response = b''
		chunksize = 10240
		port = None
		# hostname = socket.getfqdn(host)
		if not req_body.endswith("\r\n"):
			req_body += "\r\n"
		try:
			port = int(host_port.split(":")[-1])
		except Exception as e:
			elog("Bad host/port error:",e)
			return None
		host = host_port.rstrip(f":{port}")

		if tls == True: # if QCheckBox is Qt.Checked
			try:
				# context = ssl.create_default_context() 
				# context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
				# context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_3) 
				context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
				context.minimum_version = ssl.TLSVersion.TLSv1_2
				context.maximum_version = ssl.TLSVersion.TLSv1_3
				context.check_hostname = False
				context.verify_mode = ssl.CERT_NONE # TODO cert checking an option
				socket.setdefaulttimeout(timeout)
				ssock = context.wrap_socket(socket.socket())
				
				
				ssock.connect((host, port))
				
				elog("sending request body:", req_body)
				ssock.sendall(req_body.encode(encoding))
				while True:
					rdata = ssock.recv(chunksize)
					response += rdata
					elog(f"Received {len(rdata)} bytes")
					if len(rdata) < 1:
						break
				ssock.close()
				
			except socket.timeout as e:
				elog("socket timeout:",e)
			except socket.error as e:
				elog("socket error:",e)
			except ssl.SSLError as e:
				elog("SSL error:",e)
		else:
			sock = socket.socket()
			sock.connect((host, port))
			sock.sendall(req_body.encode(encoding))
			while True:
				rdata = sock.recv(chunksize)
				response += rdata
				elog(f"Received {len(rdata)} bytes")
				if len(rdata) < 1:
					break
			sock.close()



		
		elog("request worker done:",time.time()-lstart)
		return response

	def run_send_request(self):
		decode_encoding = 'utf-8'
		self.send_button.setEnabled(False)
		
		async_result = self.thread_pool.apply_async(self.send_request) # ,('foo','bar')) (arguments can be passed)
		# TODO better threading
		response_data = async_result.get() 
		self.response_input.setPlainText(response_data.decode(decode_encoding, 'ignore'))
		self.send_button.setEnabled(True)

	def __init__(self):
		super().__init__()
		self.replayer_tab_layout = QVBoxLayout(self)

		self.thread_pool = ThreadPool(processes=2)

		self.address_label = QLabel()
		self.address_label.setText("host:port")

		self.tls_label = QLabel("TLS")
		self.tls_checkbox = QCheckBox()
		self.address_input = QLineEdit()


		self.send_button = QPushButton()
		self.send_button.setText("send")
		self.send_button.clicked.connect(self.run_send_request)

		self.request_input = QTextEdit()
		self.response_input = QTextEdit(readOnly=True)

		self.vbox_layout = QVBoxLayout()
		self.replayer_tab_layout.addWidget(self.address_label)
		self.replayer_tab_layout.addWidget(self.address_input)

		hbox1 = QHBoxLayout()
		hbox1.addWidget(self.tls_label)
		hbox1.addWidget(self.tls_checkbox)
		hbox1.addWidget(self.send_button)
		hbox1.addStretch()


		
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
