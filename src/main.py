__author__ = 'chris'

from PyQt4 import QtCore, QtGui
import time
import logging
import random

COLORS = ('blue',
          'green',
          'orange',
          'red',
          'purple')


class Strooper(QtGui.QMainWindow):

    def __init__(self):
        super(Strooper, self).__init__()
        self.setWindowTitle('Stroop test!')

        self.s = SelectorDialog(self)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        bar = self.menuBar()
        filemenu = bar.addMenu('&File')
        select_experiment_action = QtGui.QAction('Start new experiment...', self)
        select_experiment_action.triggered.connect(self._select_expt)
        filemenu.addAction(select_experiment_action)
        self.txt = QtGui.QLabel('STROOP')
        cwidget = QtGui.QWidget()
        clayout = QtGui.QHBoxLayout(cwidget)
        clayout.addWidget(self.txt)
        self.setCentralWidget(cwidget)
        cwidget.setStyleSheet('background-color: white; font-size: 200px')

    QtCore.pyqtSlot(QtGui.QAbstractButton)
    def _select_expt(self, button=None):
        """
        :return:
        """
        self.s.show()

    def show(self):
        super(Strooper, self).show()
        self.s.show()

    def start_run(self, runtype):
        runtype = str(runtype)
        self.experiment = experiment_types[runtype](self)
        self.experiment.start()

    def exp_complete(self, exp_runtime):
        self.resultDialog = QtGui.QMessageBox()
        self.resultDialog.setText('Experiment complete!')
        self.resultDialog.setInformativeText('This experiment run '
                                             'time was:\n\n{0:0.4f} seconds'.format(exp_runtime))
        self.resultDialog.show()
        self.resultDialog.setModal(True)
        self.resultDialog.buttonClicked.connect(self._select_expt)

        return


    def set_txt(self, txt, cstr):
        self.txt.setText(txt)
        self.txt.setStyleSheet('color: {0}'.format(cstr))
        return

    @QtCore.pyqtSlot(QtGui.QKeyEvent)
    def keyPressEvent(self, event):
        assert isinstance(event, QtGui.QKeyEvent)
        if event.key() == 32:  # spacebar
            self.experiment.set_next()
        else:
            super(Strooper, self).keyPressEvent(event)
        return




class SelectorDialog(QtGui.QDialog):
    def __init__(self, parent):
        super(SelectorDialog, self).__init__()
        assert isinstance(parent, Strooper)
        self.setModal(True)
        self.par = parent

        self.setWindowTitle('Select experiment type')
        layout = QtGui.QVBoxLayout(self)
        buttons = QtGui.QButtonGroup(self)
        buttons.buttonClicked[QtGui.QAbstractButton].connect(self.button_clicked)
        for l in experiment_types.keys():
            button = QtGui.QPushButton(l)
            buttons.addButton(button)
            layout.addWidget(button)

    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def button_clicked(self, button):
        label = button.text()
        self.par.start_run(label)
        self.hide()


class Experiment(QtCore.QObject):
    instructions = 'REPLACE ME'
    def __init__(self, parent):
        self.current_txt = ''
        self.current_cstr = ''
        super(Experiment, self).__init__()
        self.par = parent
        print self.instructions
        self.counter = 0
        self.ntrials = 25
        self.starttime = time.time()

    def start(self):

        pass

    def generate_next(self):
        return None, None

    def set_next(self):
        if self.counter < self.ntrials:
            self.counter += 1
            txt, colorstr = self.generate_next()
            self.par.set_txt(txt, colorstr)
        else:
            print time.time() - self.starttime
            exp_time = time.time() - self.starttime
            self.par.exp_complete(exp_time)
        return


class MismatchColorTest(Experiment):
    instructions = """
    In this experiment, name the color of the text. (Don't read the word!)
    """

    def generate_next(self):
        txt = self.current_txt
        cstr = self.current_cstr
        while txt == self.current_txt and cstr == self.current_cstr:
            txt = random.choice(COLORS)
            cstr = random.choice(COLORS)
        self.current_txt = txt
        self.current_cstr = cstr
        return txt, cstr



class MismatchReadTest(Experiment):
    instructions = """
    In this experiment, read aloud the text of the color.
    """

    def generate_next(self):
        txt = self.current_txt
        cstr = self.current_cstr
        while txt == self.current_txt and cstr == self.current_cstr:
            txt = random.choice(COLORS)
            cstr = random.choice(COLORS)
        self.current_txt = txt
        self.current_cstr = cstr
        return txt, cstr


class MatchReadTest(Experiment):
    instructions = """
    In this experiment, name the color of the text displayed.
    """
    def generate_next(self):
        txt = self.current_txt
        while txt == self.current_txt:
            txt = random.choice(COLORS)
        self.current_txt = txt
        return [txt] * 2


class MatchColorTest(Experiment):
    instructions = """
    In this experiment, name the color of the text displayed
    """
    def generate_next(self):
        txt = self.current_txt
        while txt == self.current_txt:
            txt = random.choice(COLORS)
        self.current_txt = txt
        return [txt] * 2

experiment_types = {"1. Mismatch test": MismatchColorTest,
                    "2. Match test": MatchColorTest,
                     }

class InstructionDialog(QtGui.QMessageBox):
    def __init__(self, string):
        super(InstructionDialog, self).__init__()
        self.setText(string)
        self.setStandardButtons(QtGui.QMessageBox.Ok)

        
def main(config_path=''):
    import sys
    app = QtGui.QApplication(sys.argv)
    w = Strooper()
    # w.showFullScreen()
    w.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    LOGGING_LEVEL = logging.DEBUG
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(LOGGING_LEVEL)

    main()
