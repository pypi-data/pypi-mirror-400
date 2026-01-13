#  simple_carla/tests/qt_carla.py
#
#  Copyright 2024 Leon Dionne <ldionne@dridesign.sh.cn>
#
import logging
from qt_extras import DevilBox
from PyQt5.QtCore import Qt, QCoreApplication, QObject, pyqtSignal, pyqtSlot, QTimer
from simple_carla import Plugin, PatchbayPort, EngineInitFailure
from simple_carla.qt import CarlaQt, QtPlugin


APPLICATION_NAME = 'qt_carla'


class TestApp(QCoreApplication):

	def __init__(self):
		super().__init__([])
		logging.debug('run')
		carla = CarlaQt('carla_test')
		for src, tgt in [
			(carla.sig_engine_started, self.slot_engine_started),
			(carla.sig_engine_stopped, self.slot_engine_stopped)
		]: src.connect(tgt, type = Qt.QueuedConnection)
		try:
			carla.engine_init()
		except EngineInitFailure as e:
			logging.error('%s: %s', e.args[0], e.args[1])
			QTimer.singleShot(0, self.quit)	# Event loop hasn't started yet.

	@pyqtSlot(int, int, int, int, float, str)
	def slot_engine_started(self, *_):
		logging.debug('======= Engine started ======== ')
		self.meter = EBUMeter()
		self.meter.sig_ready.connect(self.meter_ready)
		self.meter.sig_connection_change.connect(self.meter_connect)
		self.meter.add_to_carla()

	@pyqtSlot()
	def slot_engine_stopped(self):
		logging.debug('======= Engine stopped ========')

	@pyqtSlot(Plugin)
	def meter_ready(self, plugin):
		logging.debug('Received sig_ready from %s', plugin)
		for out_port, in_port in zip(plugin.audio_outs(), CarlaQt.instance.system_audio_in_ports()):
			out_port.connect_to(in_port)

	@pyqtSlot(PatchbayPort, PatchbayPort, bool)
	def meter_connect(self, self_port, other_port, state):
		logging.debug('Received sig_connection_change: %s to %s: %s', self_port, other_port, state)
		CarlaQt.instance.delete()
		self.quit()


class EBUMeter(QtPlugin):

	plugin_def = {
		'name': 'EBU Meter (Mono)',
		'build': 2,
		'type': 4,
		'filename': 'meters.lv2',
		'label': 'http://gareus.org/oss/lv2/meters#EBUmono',
		'uniqueId': 0
	}

	def ready(self):
		"""
		Called after post_embed_init() and all ports ready
		"""
		self.parameters[0].value = -6.0
		super().ready()

	def value(self):
		return self.parameters[1].get_internal_value()



if __name__ == "__main__":
	logging.basicConfig(
		level = logging.DEBUG,
		format = "[%(filename)24s:%(lineno)-4d] %(message)s"
	)
	app = TestApp()
	app.exec()


#  end simple_carla/tests/qt_carla.py
