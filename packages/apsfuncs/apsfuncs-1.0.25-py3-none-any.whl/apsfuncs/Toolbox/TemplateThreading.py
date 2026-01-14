from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer

from apsfuncs.Toolbox.AutoUpdating import handle_auto_update
from apsfuncs.Toolbox.GlobalTools import BlackBoard

# Thread to handle updating search
class UpdateThreadWorker(QObject):
    update_check_complete = pyqtSignal(list)

    # Init
    def __init__(self):
        super().__init__()

        # Set up class reference to global black board
        self.bb = BlackBoard.instance()

    @pyqtSlot()
    def run(self):
        try:
            update_available, current_version, latest_version, latest_version_url, updater_name, prog_name = handle_auto_update()
            self.update_check_complete.emit([update_available, current_version, latest_version, latest_version_url, updater_name, prog_name])

        except Exception as e:
            # Catch any exception not handled by teh exception hook and put it into the log
            self.bb.logger.exception('Auto update failed: {}'.format(e))
            self.bb.logger.info("Auto update failed")
            self.update_check_complete.emit([False, "vX.X.X", "", "", "", ""])

# Thread to handle updating search
class LoadingThread(QObject):
    loading_tick = pyqtSignal()
    timeout = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, timeout_dur):
        super().__init__()
        self.timeout_dur = timeout_dur
        self.spent_time = 0

    @pyqtSlot()
    def run(self):
        self.timer = QTimer()
        self.timer.setInterval(250)
        self.timer.timeout.connect(self.check_tick)
        self.timer.start()

    # Method to track timout
    def check_tick(self):
        self.loading_tick.emit()
        self.spent_time += 0.25
        if self.spent_time > self.timeout_dur:
            self.timeout.emit()

    @pyqtSlot()
    def stop(self):
        self.timer.stop()
        self.finished.emit()