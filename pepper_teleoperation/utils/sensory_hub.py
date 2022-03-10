# -*- coding: utf-8 -*-
'''
Copyright October 2019 Roberto Menicatti & Università degli Studi di Genova & Bui Ha Duong

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

***

Author:      Roberto Menicatti (1), Bui Ha Duong (2)
Email:       (1) roberto.menicatti@dibris.unige.it (2) bhduong@jaist.ac.jp
Affiliation: (1) Laboratorium, DIBRIS, University of Genova, Italy
             (2) Robotics Laboratory, Japan Advanced Institute of Science and Technology, Japan
Project:     CARESSES (http://caressesrobot.org/en/)
'''

from threading import Thread
import time
import numpy
import math
import os
import json
import logging
# import cv2

log_dud = logging.getLogger('DetectUserDepth')


## Compute distance between Pepper and the user
class DetectUserDepth(Thread):

    user_position = [0, 0, 0]
    user_id = None
    timeout = 20

    # Flag to use face recognition or not
    useFaceReco = True
    userApproached = False

    def __init__(self, session, output_handler, useFaceReco):
        Thread.__init__(self)

        self.id = "Sensory Hub - User Detection Depth"
        self.alive = True

        self.output_handler = output_handler
        self.useFaceReco = useFaceReco
        DetectUserDepth.useFaceReco = useFaceReco

        self.people_perception = session.service("ALPeoplePerception")
        self.sFaceDet = session.service("ALFaceDetection")
        self.sMemory = session.service("ALMemory")
        self.sSpeech = session.service("ALTextToSpeech")

        self.people_perception.setMaximumDetectionRange(3.5)
        self.people_perception.setTimeBeforePersonDisappears(DetectUserDepth.timeout)
        self.people_perception.setTimeBeforeVisiblePersonDisappears(DetectUserDepth.timeout)
        self.people_perception.setFastModeEnabled(False)

        self.subscriber = self.sMemory.subscriber("PeoplePerception/PeopleDetected")
        self.subscriber_a = self.sMemory.subscriber("PeoplePerception/JustArrived")
        self.subscriber_l = self.sMemory.subscriber("PeoplePerception/JustLeft")
        self.subscriber_list = self.sMemory.subscriber("PeoplePerception/PeopleList")

        self.perceived_people_list = []

        # self.subscriber.signal.connect(self.on_human_detected)
        self.subscriber_a.signal.connect(self.on_human_arrived)
        self.subscriber_l.signal.connect(self.on_human_left)
        self.subscriber_list.signal.connect(self.on_people_list_updated)

        if self.useFaceReco:
            self.subscriber_f = self.sMemory.subscriber("FaceDetected")
            self.subscriber_f.signal.connect(self.on_face_detected)
            self.sFaceDet.subscribe("DetectUserDepth")
            self.sFaceDet.setRecognitionConfidenceThreshold(0.7)

            self.perceived_people_list = []
            self.detected_faces = []

            self._loadKnownPeopleList()

    def on_human_arrived(self, value):
        if not self.useFaceReco:
            self.notifyIfUserIsFar(False)

    def on_human_left(self, value):
        if not self.useFaceReco:
            self.notifyIfUserIsFar(True)

    def on_people_list_updated(self, people_list):
        self.perceived_people_list = people_list

    def on_face_detected(self, value):
        if (len(value) > 0):
            if len(value[1]) > 0:
                self.detected_faces = value[1][:-1]
                for person in Person.list:
                    for index, face in enumerate(value[1][:-1]):
                        face_label = value[1][index][1][2]
                        if face_label == person.naoqi_face_label:
                            person.face_recognized = True
                            person.not_visible_since = time.time()
                            if not person.is_present:
                                person.is_present = True
                                if person.is_user:
                                    self.notifyIfUserIsFar(False)
                            break
                        else:
                            person.face_recognized = False
        else:
            self.detected_faces = []
            for person in Person.list:
                person.face_recognized = False

    def run(self):
        while(self.alive):
            time.sleep(0.5)
            if len(self.perceived_people_list) >= 1:
                if not self.perceived_people_list[0] == DetectUserDepth.user_id:
                    DetectUserDepth.user_id = self.perceived_people_list[0] ## We assume that the first person detected is the user. If someone else joins the user, he's added to the list, so he's not at index 0.
            if not len(self.sMemory.getDataList(str(DetectUserDepth.user_id))) == 0:
                try:
                    DetectUserDepth.user_position = self.sMemory.getData("PeoplePerception/Person/" + str(DetectUserDepth.user_id) + "/PositionInTorsoFrame")
                except:
                    DetectUserDepth.user_position = [None, None, None]
            else:
                DetectUserDepth.user_position = [None, None, None]

            if self.useFaceReco:
                for p in Person.list:
                    ## Uncomment the following line for debug
                    # print p
                    if p.is_present:
                        if time.time() - p.not_visible_since > DetectUserDepth.timeout:
                            p.is_present = False
                            if p.is_user:
                                self.notifyIfUserIsFar(True)
                ## Uncomment the following three lines for debug
                # self.printPersonSituation()
                # print "======================================"
                # time.sleep(1)

        log_dud.info("%s terminated correctly." % self.id)

    def printPersonSituation(self):
        print("----------------------------")
        print ("People detected: " + str(len(self.perceived_people_list)))
        print ("Faces detected: " + str(len(self.detected_faces)))
        known_present_names = []
        for p in Person.getPresentKnownPersons():
            known_present_names.append(p.name)
        print ("Known people: " + str(len(Person.getPresentKnownPersons())))
        print (known_present_names)
        if len(self.perceived_people_list) >= len(Person.getPresentKnownPersons()):
            unknown = len(self.perceived_people_list) - len(Person.getPresentKnownPersons())
        else:
            unknown = 0
        print ("Unknown people: " + str(unknown))

    # @staticmethod
    # def isUserApproached():
    #     if caressestools.Settings.interactionNode == "":
    #         #return DetectUserDepth.userApproached
    #         return True
    #     else:
    #         return True

    def notifyIfUserIsFar(self, is_user_far):
        DetectUserDepth.userApproached=not is_user_far
        approached = str(not is_user_far).lower()
        message_D6_1 = "[approached-user:%s]" % approached
        #self.output_handler.writeSupplyMessage("publish", "D6.1", message_D6_1)
        log_dud.debug("Sending to CSPEM the state: %s" % message_D6_1)


    def _loadKnownPeopleList(self):
        directory = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(directory, "knownPeopleList.json")
        try:
            with open(file_path) as known_people_file:
                known_people_dict = json.load(known_people_file)
            for p_id in known_people_dict.keys():
                p = known_people_dict[p_id]
                Person(p["name"].encode('utf-8'), p["family-name"].encode('utf-8'), p_id, p["naoqi-face-label"].encode('utf-8'))
        except Exception as e:
            print (e)
            log_dud.error("File 'knownPeopleList.json' not found at %s" % file_path + ". Ignoring face recognition.")

    @staticmethod
    def getUserPosition():
        user_pos = DetectUserDepth.user_position
        DetectUserDepth.user_position = [0, 0, 0]
        return user_pos

    @staticmethod
    def isUsingFaceRecognition():
        return DetectUserDepth.useFaceReco

    def stop(self):
        if self.useFaceReco:
            self.sFaceDet.unsubscribe("DetectUserDepth")
        self.alive = False


## Define a Person object to keep track of recognized face in the environment
class Person():

    list = []

    def __str__(self):
        pars = self.name, str(self.face_recognized) + ",", str(self.is_present) + ",", str(time.time() - self.not_visible_since)
        p_str = '{0:{width0}} - Face recognized: {1:{width1_2}} Present: {2:{width1_2}} Not seen for {3:{width3}} s.'.format(*pars, width0=10, width1_2=6, width3=15)
        return p_str

    def __init__(self, name, family_name, id, face_label):
        self.name = name
        self.family_name = family_name
        self.id = id
        self.naoqi_face_label = face_label
        self.people_perception_id = None
        self.face_recognized = False
        self.not_visible_since = time.time()

        self.is_present = False
        self.is_user = self.naoqi_face_label == "user"

        Person.list.append(self)

    @staticmethod
    def getPresentKnownPersons():
        present_known_list = []
        for p in Person.list:
            if p.is_present == True:
                present_known_list.append(p)

        return present_known_list

    @staticmethod
    def isUserPresent():
        known_people_present = Person.getPresentKnownPersons()
        for p in known_people_present:
            if p.is_user:
                return True
        return False