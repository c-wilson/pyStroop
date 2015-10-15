__author__ = 'chris'

from PyQt4 import QtCore, QtGui
import time
import logging
import random


NTRIALS = 30  # number of words to display for the experiment.
COLORS = ('blue',
          'green',
          'orange',
          'red',
          'purple')


class Strooper(QtGui.QMainWindow):
    def __init__(self):
        super(Strooper, self).__init__()
        self.setWindowTitle('pyStrooper')

        self.expt_selector_widget = SelectorDialog(self)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        bar = self.menuBar()
        bar.setNativeMenuBar(False)
        filemenu = bar.addMenu('&File')
        select_experiment_action = QtGui.QAction('Start new experiment...', self)
        select_experiment_action.triggered.connect(self._select_expt)
        filemenu.addAction(select_experiment_action)
        exitAction = QtGui.QAction("&Quit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("Quit program.")
        exitAction.triggered.connect(QtGui.qApp.quit)
        filemenu.addAction(exitAction)
        assert isinstance(bar, QtGui.QMenuBar)

        cwidget = QtGui.QWidget()
        clayout = QtGui.QHBoxLayout(cwidget)
        self.txt = QtGui.QLabel('STROOP')
        clayout.addWidget(self.txt)
        self.setCentralWidget(cwidget)
        cwidget.setStyleSheet('background-color: white; font-size: 200px')

    QtCore.pyqtSlot(QtGui.QAbstractButton)
    def _select_expt(self, button=None):
        self.expt_selector_widget.show()
        return

    def show(self):
        super(Strooper, self).show()
        self.expt_selector_widget.show()
        return

    def start_run(self, runtype):
        runtype = str(runtype)
        self.experiment = experiment_types[runtype](self)

    def exp_complete(self, exp_runtime):
        self.resultDialog = QtGui.QMessageBox()
        self.resultDialog.setText('Experiment complete!')
        self.resultDialog.setInformativeText('This experiment run time was:\n\n{0:0.4f} seconds'.format(exp_runtime))
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

    @QtCore.pyqtSlot()
    def _set_exp_params(self):
        pass
        # self.trial




class SelectorDialog(QtGui.QDialog):
    def __init__(self, parent):
        super(SelectorDialog, self).__init__()
        assert isinstance(parent, Strooper)
        self.setModal(True)
        self.par = parent

        self.setWindowTitle('Start experiment')
        layout = QtGui.QVBoxLayout(self)
        label = QtGui.QLabel('Select experiment type:')
        layout.addWidget(label)
        buttons = QtGui.QButtonGroup(self)
        buttons.buttonClicked[QtGui.QAbstractButton].connect(self.button_clicked)

        try:   # this is for backward compatibility w/ Python 2.
            exp_items = experiment_types.items()
        except AttributeError:
            exp_items = experiment_types.iteritems()
        for k, v in exp_items:
            button = QtGui.QPushButton(k)  # k is the label
            buttons.addButton(button)
            button.setToolTip(v.tooltip)
            layout.addWidget(button)

        tn_layout = QtGui.QHBoxLayout()
        tn_disc = QtGui.QLabel('Number of trials:')
        tn_layout.addWidget(tn_disc)
        tn_sel = QtGui.QSpinBox()
        tn_layout.addWidget(tn_sel)
        tn_sel.setRange(1, 200)
        tn_sel.setValue(NTRIALS)
        tn_sel.valueChanged[int].connect(self._ntrials_changed)
        layout.addLayout(tn_layout)

        flags = self.windowFlags()  # TODO: this is broken
        flags = flags | ~QtCore.Qt.WindowCloseButtonHint  # trying to disable close button.
        self.setWindowFlags(flags)


    @QtCore.pyqtSlot(int)
    def _ntrials_changed(self, val):
        global NTRIALS
        NTRIALS = val


    @QtCore.pyqtSlot(QtGui.QAbstractButton)
    def button_clicked(self, button):
        label = button.text()
        self.par.start_run(label)
        self.hide()


class Experiment(QtCore.QObject):
    instructions = 'REPLACE ME'
    tooltip = 'REPLACE THIS WITH A DISCRIPTION!'

    def __init__(self, parent):
        self.current_txt = ''
        self.current_cstr = ''
        super(Experiment, self).__init__()
        self.par = parent
        self.counter = 0
        self.starttime = time.time()
        self.instructionDialog = QtGui.QMessageBox()
        self.instructionDialog.setModal(True)
        self.instructionDialog.setText(self.instructions)
        self.instructionDialog.buttonClicked.connect(self.start)
        self.instructionDialog.show()


    def start(self, _):
        self.starttime = time.time()
        self.set_next()
        return

    def generate_next(self):
        return None, None

    def set_next(self):
        if self.counter < NTRIALS:
            self.counter += 1
            txt, colorstr = self.generate_next()
            self.current_txt = txt
            self.current_cstr = colorstr
            self.par.set_txt(txt, colorstr)

        else:
            exp_time = time.time() - self.starttime
            self.par.exp_complete(exp_time)
        return


class MismatchColorTest(Experiment):
    instructions = """
    In this experiment, name the color of the text. (Don't read the word!)

    The words will not match the colors that they are drawn in.

    Press Spacebar after you say the color correctly.
    """

    tooltip = 'The hard one: text cue and ink color are NOT the same (usually)'

    def generate_next(self):
        txt = self.current_txt
        cstr = self.current_cstr
        while txt == self.current_txt or cstr == self.current_cstr or txt == cstr:
            txt = random.choice(COLORS)
            cstr = random.choice(COLORS)
        return txt, cstr


class ColorOnlyTest(Experiment):
    instructions = '''In this experiment, name the color of the text.

    press spacebar after you name the color of the text correctly.'''
    tooltip = 'Tests how quickly you can name colors alone with no text cue.'

    def generate_next(self):
        txt = 'stroop'
        colstr = self.current_cstr
        while colstr == self.current_cstr:
            colstr = random.choice(COLORS)
        return txt, colstr


class NoColorTest(Experiment):
    instructions = '''
    In this experiment, you are testing how quickly you can read the words alone with no color.

    Press Spacebar after you read the word correctly.'''
    tooltip = 'Tests how quickly you can read with no color cue.'
    def generate_next(self):
        txt = self.current_txt
        while txt == self.current_txt:
            txt = random.choice(COLORS)
        return txt, 'black'


class MatchColorTest(Experiment):
    instructions = """
    In this experiment, say aloud the color of the text displayed.

    The words will match the colors they are draw in.

    Press Spacebar after you say the word correctly.
    """

    tooltip = 'Tests how quickly you can name colors when the text and ink are the same.'
    def generate_next(self):
        txt = self.current_txt
        while txt == self.current_txt:
            txt = random.choice(COLORS)
        return [txt] * 2

experiment_types = {"Mismatch test": MismatchColorTest,
                    "Match test": MatchColorTest,
                    "Color-only test": ColorOnlyTest,
                    "No color read test": NoColorTest}

class InstructionDialog(QtGui.QMessageBox):
    def __init__(self, string):
        super(InstructionDialog, self).__init__()
        self.setInformativeText(string)
        # self.setStandardButtons(QtGui.QMessageBox.Ok)


        
def main(config_path=''):
    import sys
    app = QtGui.QApplication(sys.argv)
    w = Strooper()
    w.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    LOGGING_LEVEL = logging.DEBUG
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)expt_selector_widget %(levelname)-8s %(message)expt_selector_widget')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(LOGGING_LEVEL)

    main()
