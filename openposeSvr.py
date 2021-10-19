import logging
import random
import tornado.ioloop
import json

from webthing import Value
from webthing import Thing
from webthing import WebThingServer
from webthing.property import Property
from webthing.server import SingleThing

from elasticsearch import Elasticsearch

class make_openpose_thing(Thing):
    def __init__(self):
        Thing.__init__(
            self,
            'urn:dev:ops:openpose1234',
            'People number',
            ['MultiLevelSensor'],
            'how many people are detected'
        )

        self.peopleNumber = Value(0)
        self.add_property(
            Property(
                self,
                'amount',
                self.peopleNumber,
                metadata={
                    '@type': 'NumberProperty',
                    'title': 'peopleNumber',
                    'type': 'integer',
                    'description': 'The current people number',
                    'readOnly': True,
                }
            )
        )
        
        logging.debug('starting the people number update looping task')  # not webThing library
        self.timer = tornado.ioloop.PeriodicCallback(
            self.updata_people_number,
            3000.0
        )  # updata_people_number for every 3000.0 milliseconds
        self.timer.start()
 
    def updata_people_number(self):
        new_people_number = self.readJsonFromOpenpose()
        logging.debug('setting new people number')
        # notify if value is not last value, and set new value
        self.peopleNumber.notify_of_external_update(new_people_number) 
        print('now is:', self.peopleNumber.get())

    @staticmethod 
    def readJsonFromOpenpose():
        # now for test, will read file in reaal use
        number = 0
        # number = random.randint(0,50)
        with open("people_Data/000000000001.json","r") as peopleFile:
            peopleJson = json.load(peopleFile)
            peopleDataList = peopleJson["people"]
            if peopleDataList: # if peopleNum list is not empty
                number = len(peopleDataList)
        return number

    def stop_update_people_number(self):
        # if the program is stopped by keyboard (ctrl+C), should close timer thread
        self.timer.stop()

def run_server():
    # make openpose object
    things1 = make_openpose_thing()
    
    # create object for webthing server(not using thread) 
    server = WebThingServer(SingleThing(things1),port=6666)
    '''
    # If adding more than one thing, use MultipleThings() with a name.
    # In the single thing case, the thing's name will be broadcast.
    server = WebThingServer(MultipleThings([temperature, openpose, sensor],
                                           'LightAndTempDevice'),
                            port=8888)
    '''
    try:
        logging.info('start openpose server')
        # thread1.start()
        server.start()
    except KeyboardInterrupt: # usually stop by keyboard(ctrl+c)
        logging.debug('stop update people number')
        things1.stop_update_people_number()
        logging.debug('stop openpose server')
        server.stop()
        logging.debug('done')


if __name__ == '__main__':
    
    # show program running info at first time
    logging.basicConfig(
        level=10,
        format="%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
    )
    run_server() # run all Opp2Webthings Opp2Elasticsearch
