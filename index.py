import pandas as pd

from sys import argv
from pandas import set_option
from taiwan_stock import crawler
from os.path import abspath, dirname
from io import StringIO

from PySide2.QtWidgets import QApplication, QMainWindow, QButtonGroup, QFileDialog, QTableWidgetItem, QVBoxLayout, QCheckBox, QHeaderView, QDialog, QLabel
from PySide2.QtCore import QFile, QThread, Signal, Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QIcon, QFont

from qt_material import apply_stylesheet

# Global Variable
VERSION = 'v0.0.1'
ROOT_PATH = abspath(dirname(__file__))
GUI_PATH = ROOT_PATH + '/ui/app.ui'
ICON_PATH = ROOT_PATH + '/image/app.png'
STOCK_LIST_PATH = ROOT_PATH + '/output/股票列表/stockList.csv'
GET_STOCK_LIST_THREAD = 1

# Enable the dataframe to be aligned when outputting Chinese characters
set_option('display.unicode.ambiguous_as_wide', True)
set_option('display.unicode.east_asian_width', True)

class CrawlerThread(QThread):
    def __init__(self, dialog, task):
        super(CrawlerThread, self).__init__()
        self.dialog = dialog
        self.task = task

    def run(self):
        if self.task == GET_STOCK_LIST_THREAD:
            crawler.getStockList()
        self.dialog.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.init_UI() # initialize UI window
        self.init_stockListPage() # initialize stock list page

    def init_UI(self):
        # Load UI file
        qfile = QFile(GUI_PATH)
        qfile.open(QFile.ReadOnly)
        self.widget = QUiLoader().load(qfile)
        self.setCentralWidget(self.widget)
        qfile.close()

        # Pre-set UI font size
        custom_stylesheet = """
            * {
                font-size: 25px;
            }
        """
        self.widget.setStyleSheet(custom_stylesheet)

        self.setWindowTitle('Taiwan Stock Analyzer ' + VERSION + ' (beta)') # set window title name
        self.setWindowIcon(QIcon(ICON_PATH)) # set window icon
        self.resize(1920, 1080) # set window size
    
    def init_stockListPage(self):
        self.data_frame = pd.read_csv(STOCK_LIST_PATH) # read stock list csv file

        # Create '市場別' checkBox filter
        self.markets_list = self.data_frame['市場別'].unique().tolist()
        self.widget.group_box_layout = QVBoxLayout()
        self.checkBox_markets_list = []
        for item in self.markets_list:
            checkBox = QCheckBox(item)
            checkBox.setChecked(True) # default checked state
            checkBox.stateChanged.connect(lambda: self._stockListFilter(self.data_frame))
            self.checkBox_markets_list.append(checkBox)
            self.widget.group_box_layout.addWidget(checkBox)
        self.widget.groupBox_markets.setLayout(self.widget.group_box_layout)

        # Create '產業別' checkBox filter
        self.industries_list = self.data_frame['產業別'].unique().tolist()
        self.widget.group_box_layout = QVBoxLayout()
        self.checkBox_industries_list = []
        for item in self.industries_list:
            checkBox = QCheckBox(item)
            checkBox.setChecked(True) # default checked state
            checkBox.stateChanged.connect(lambda: self._stockListFilter(self.data_frame))
            self.checkBox_industries_list.append(checkBox)
            self.widget.group_box_layout.addWidget(checkBox)
        self.widget.groupBox_industries.setLayout(self.widget.group_box_layout)

        # Create '類型' checkBox filter
        self.types_list = self.data_frame['類型'].unique().tolist()
        self.widget.group_box_layout = QVBoxLayout()
        self.checkBox_types_list = []
        for item in self.types_list:
            checkBox = QCheckBox(item)
            checkBox.setChecked(True) # default checked state
            checkBox.stateChanged.connect(lambda: self._stockListFilter(self.data_frame))
            self.checkBox_types_list.append(checkBox)
            self.widget.group_box_layout.addWidget(checkBox)
        self.widget.groupBox_types.setLayout(self.widget.group_box_layout)

        self.widget.lineEdit_search.textChanged.connect(lambda: self._stockListFilter(self.data_frame)) # set lineEdit textChanged trigger

        self.widget.tableWidget_stockList.setColumnCount(len(self.data_frame.columns)) # set table column count
        self.widget.tableWidget_stockList.setHorizontalHeaderLabels(self.data_frame.columns) # set table header labels
        self._stockListFilter(self.data_frame) # filter and show stock list table

        self.widget.pushButton_updateStockList.clicked.connect(self._updateStockList)
    
    def _updateStockList(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Update Stock List")
        dialog.resize(600, 200)
        dialog.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        dialog.setStyleSheet("background-color: lightblue")

        # Set font size
        custom_stylesheet = """
            * {
                font-size: 25px;
            }
        """
        dialog.setStyleSheet(custom_stylesheet)
        label = QLabel("Crawling the Latest Taiwan Stock List......", dialog)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("background-color: lightblue")

        layout = QVBoxLayout(dialog)
        layout.addWidget(label)

        thread_getStockList = CrawlerThread(dialog, GET_STOCK_LIST_THREAD)
        thread_getStockList.start()

        dialog.exec_()

        self.data_frame = pd.read_csv(STOCK_LIST_PATH) # read stock list csv file
        self._stockListFilter(self.data_frame) # filter and show stock list table

    def _stockListFilter(self, df_filtered):
        for checkBox in self.checkBox_markets_list:
            if not checkBox.isChecked():
                condition = df_filtered['市場別'] == checkBox.text()
                df_filtered = df_filtered[~condition]
        for checkBox in self.checkBox_industries_list:
            if not checkBox.isChecked():
                condition = df_filtered['產業別'] == checkBox.text()
                df_filtered = df_filtered[~condition]
        for checkBox in self.checkBox_types_list:
            if not checkBox.isChecked():
                condition = df_filtered['類型'] == checkBox.text()
                df_filtered = df_filtered[~condition]

        df_filtered = df_filtered[df_filtered.drop(columns='ISIN Code').apply(lambda row: row.astype(str).str.contains(self.widget.lineEdit_search.text()).any(), axis=1)] # lineEdit_search search stock list

        self.widget.tableWidget_stockList.setRowCount(len(df_filtered))
        for i, row in enumerate(df_filtered.itertuples()):
            row = list(row)[1:] # remove the index column
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.widget.tableWidget_stockList.setItem(i, j, item)
        header = self.widget.tableWidget_stockList.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch) # table column width adaptive

if __name__ == '__main__':
    # -----------------------------------------------------------
    # crawler.getAllStockHistories() 使用教學
    # -----------------------------------------------------------
    # 根據 crawler.getStockList 回傳的 dataframe 來抓取個股歷史紀錄
    # -----------------------------------------------------------
    # 市場別 (markets) 共有 2 種：
    #   1. '上市'
    #   2. '上櫃'
    # -----------------------------------------------------------
    # 個股類型 (types) 共有 7 種：
    #   1. '股票'
    #   2. '臺灣存託憑證(TDR)'
    #   3. 'ETF'
    #   4. 'ETN'
    #   5. '特別股'
    #   6. '受益證券-不動產投資信託'
    #   7. '受益證券-資產基礎證券'
    # -----------------------------------------------------------
    # markets = ['上市', '上櫃']
    # types = ['股票', '臺灣存託憑證(TDR)', 'ETF', 'ETN', '特別股', '受益證券-不動產投資信託', '受益證券-資產基礎證券']
    # crawler.getAllStockHistories(markets, types) # 根據指定的市場別(markets)和股票類型(types)來抓取其所有個股之歷史股價(從 2017-02-06 開始)，並儲存至 /output/歷史股價/

    # crawler.getRealTime(sid=['^TWII', '5351', '3037']) # 抓取指定個股的即時價格

    # markets = ['上市']
    # types = ['股票']
    # crawler.getAllStockHistories(markets, types)

    app = QApplication(argv)
    widget = MainWindow()

    apply_stylesheet(app, theme='light_cyan_500.xml', invert_secondary=True)
    widget.show()

    app.exec_()