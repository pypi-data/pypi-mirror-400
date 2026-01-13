#  simple_carla/tests/carla.py
#
#  Copyright 2024 Leon Dionne <ldionne@dridesign.sh.cn>
#
import logging
from time import sleep
from simple_carla import Carla, Plugin, EngineInitFailure


class TestApp:

	def __init__(self, meter_class = 'EBUMeter'):
		super().__init__()
		self.ready = False
		carla = Carla('carla_test')
		carla.on_engine_started(self.carla_started)
		carla.on_engine_stopped(self.carla_stopped)
		carla.engine_init()

	def carla_started(self, *_):
		logging.debug('======= Engine started ======== ')
		self.meter = EBUMeter()
		self.meter.on_ready(self.meter_ready)
		self.meter.add_to_carla()

	def carla_stopped(self):
		logging.debug('======= Engine stopped ========')

	def meter_ready(self):
		logging.debug('TestApp meter_ready ')
		self.ready = True

	def wait_ready(self):
		watchdog = 0
		while not self.ready:
			watchdog += 1
			if watchdog > 3:
				logging.debug('Tired of waiting')
				break
			else:
				logging.debug('TestApp waiting for meter_ready_event ...')
				sleep(0.4)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.shutdown()

	def shutdown(self):
		logging.debug('TestApp.shutdown');
		Carla.instance.delete()



class EBUMeter(Plugin):

	plugin_def = {
		'name': 'EBU Meter (Mono)',
		'build': 2,
		'type': 4,
		'filename': 'meters.lv2',
		'label': 'http://gareus.org/oss/lv2/meters#EBUmono',
		'uniqueId': 0
	}

	def finalize_init(self):
		self.parameters[0].value = -6.0

	def value(self):
		return self.parameters[1].get_internal_value()



if __name__ == "__main__":
	logging.basicConfig(
		level = logging.DEBUG,
		format = "[%(filename)24s:%(lineno)-4d] %(message)s"
	)
	try:
		with TestApp() as tester:
			tester.wait_ready()
		logging.debug('Done')
	except EngineInitFailure as e:
		logging.error('%s: %s', e.args[0], e.args[1])


#  end simple_carla/tests/carla.py
