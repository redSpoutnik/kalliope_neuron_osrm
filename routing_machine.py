# coding: utf-8
import logging
import osrm

from kalliope.core.NeuronModule import NeuronModule, MissingParameterException, InvalidParameterException
from urllib2 import HTTPError

logging.basicConfig()
logger = logging.getLogger("kalliope")


class Routing_machine(NeuronModule):
    def __init__(self, **kwargs):
        super(Routing_machine, self).__init__(**kwargs)
        # Configuration
        self.host = kwargs.get('host', 'router.project-osrm.org')
        self.profile = kwargs.get('profile', 'driving')
        # Parameters
        self.latitude1 = kwargs.get('latitude1', None)
        self.longitude1 = kwargs.get('longitude1', None)

        self.latitude2 = kwargs.get('latitude2', None)
        self.longitude2 = kwargs.get('longitude2', None)

        self.alternatives = kwargs.get('alternatives', False)

        self.distance = kwargs.get('distance', False)
        self.duration = kwargs.get('duration', False)
        self.summary = kwargs.get('summary', False)
        self.route = kwargs.get('route', False)
        self.raw = kwargs.get('raw', False)

        if self._is_parameters_ok():
            osrm.RequestConfig.host = self.host
            osrm.RequestConfig.profile = self.profile

            start = osrm.Point(latitude=float(self.latitude1), longitude=float(self.longitude1))
            end = osrm.Point(latitude=float(self.latitude2), longitude=float(self.longitude2))

            try:
                self.api_result = osrm.simple_route(start, end, steps=True, alternatives=self.alternatives)
                logging.debug("[OSRM] get API result")

                message = {
                    "returncode": "OK",
                    "start": str(start),
                    "end": str(end),
                    "profile": self.profile
                }

                if self.raw:
                    message['raw'] = self.api_result
                    logging.debug("[OSRM] add raw JSON to message")

                # create items (result, route) iterator and append mappers
                items_iterator = map(lambda route: {'result': {}, 'route': route}, self.api_result['routes'])
                if self.distance:
                    logging.debug("[OSRM] add distance to execution scheme")
                    items_iterator = map(self.distance_mapper, items_iterator)
                if self.duration:
                    logging.debug("[OSRM] add duration to execution scheme")
                    items_iterator = map(self.duration_mapper, items_iterator)
                if self.summary:
                    logging.debug("[OSRM] add summary to execution scheme")
                    items_iterator = map(self.route_summary_mapper, items_iterator)
                if self.route:
                    logging.debug("[OSRM] add route to execution scheme")
                    items_iterator = map(self.route_mapper, items_iterator)

                # extract results from items
                items_iterator = map(lambda item: item['result'], items_iterator)
                message['routes'] = list(items_iterator)
            except HTTPError as e:
                message = {
                    "returncode": str(e.code)
                }

            logging.debug("[OSRM] neuron return dict %s" % message)
            self.say(message)

    def _is_parameters_ok(self):
        """
        Check if received parameters are correct
        :return: True if parameters are ok
        .. raises:: InvalidParameterException, MissingParameterException
        """
        if not self.latitude1:
            raise MissingParameterException("[OSRM] latitude1 is missing")
        if not self.longitude1:
            raise MissingParameterException("[OSRM] longitude1 is missing")
        if not self.latitude2:
            raise MissingParameterException("[OSRM] latitude2 is missing")
        if not self.longitude2:
            raise MissingParameterException("[OSRM] longitude2 is missing")
        
        if self.alternatives and ((not isinstance(self.alternatives, int)) or (self.alternatives < 1)):
            raise InvalidParameterException("[OSRM] wrong alternatives value : %s" % self.alternatives)
        
        if not (self.distance or self.duration or self.summary or self.route or self.raw):
            raise MissingParameterException("[OSRM] no action specified")
        return True

    @staticmethod
    def distance_mapper(item):
        """
        Extract distance info from item's route then store it in item's result
        :param item: {'route': route_dict, 'result': result_dict}
        :return: input's item
        """
        distance = item['route']['distance']
        item['result']['distance'] = {
            "kilometers": int(distance // 1000),
            "meters": int(distance % 1000)
        }
        return item

    @staticmethod
    def duration_mapper(item):
        """
        Extract duration info from item's route then store it in item's result
        :param item: {'route': route_dict, 'result': result_dict}
        :return: input's item
        """
        seconds = item['route']['duration']
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        item['result']['duration'] = {
            'days': int(days),
            'hours': int(hours),
            'minutes': int(minutes),
            'seconds': int(seconds)
        }
        return item

    @staticmethod
    def route_summary_mapper(item):
        """
        Extract summary info from item's route then store it in item's result
        :param item: {'route': route_dict, 'result': result_dict}
        :return: input's item
        """
        item['result']['summary'] = item['route']['legs'][0]['summary']
        return item

    @staticmethod
    def route_mapper(item):
        """
        Extract route info from item's route then store it in item's result
        :param item: {'route': route_dict, 'result': result_dict}
        :return: input's item
        """
        steps = item['route']['legs'][0]['steps']
        item['result']['number_steps'] = len(steps)
        item['result']['steps'] = [{
            'name': step['name'],
            'maneuver': step['maneuver']['type'],
            'direction': step['maneuver'].get('modifier', None)
        } for step in steps]
        return item
