#!/usr/bin/env python

"""
Disable autonomous life on boot on Pepper robot.

Sometimes one can't access the website of the robot
to disable the annoying Autonomous Life on boot
(http://YOUR.ROBOT.IP.HERE/#/menu/advancedSettings), so
taken from what the website is actually doing using the
inspect tool of chrome and translating it to Python...
This script disables AutonomousLife on boot.
Also enables the web switch if it was not enabled in Japanese robots.

Run it in the robot (or modify localhost to the IP of the robot).

Author: Sammy Pfeiffer <Sammy.Pfeiffer@student.uts.edu.au>
"""

from qi import Session

s = Session()
# Copy the script to the robot, or change to the robot IP
s.connect('tcp://130.251.13.112:9559')
print("Getting ALPreferenceManager service...")
ALPreferenceManager = s.service("ALPreferenceManager")
print("Checking the type of robot we have (JP/non JP)")
print("Getting from domain 'com.aldebaran.debug' key 'DisableLifeAndDialog'")
current_state = ALPreferenceManager.getValue(
    'com.aldebaran.debug',
    'DisableLifeAndDialog')
# Japanese robots have this key, others (AFAIK) always show the switch
print("Getting from domain 'com.aldebaran.robotwebpage' key 'MenuNoSwitchLife'")
web_switch_state = ALPreferenceManager.getValue(
    'com.aldebaran.robotwebpage',
    'MenuNoSwitchLife')
if web_switch_state is not None:
    print("Looks like we have a Japanese robot")
    print("We will also enable the AutonomousLife toggle in the website")
    ALPreferenceManager.setValue(
        'com.aldebaran.robotwebpage', 'MenuNoSwitchLife', '0')
else:
    print("Looks like we have a non-Japanese robot, all good")
if current_state == '1':
    print("AutonomousLife was already disabled on boot")
elif current_state == '0':
    print("AutonomousLife was not disabled on boot")
else:
    print("Found value '" + str(current_state) +
          "' and we only expect '0' (enabled on boot) or '1' (disabled)")

print("Setting key to disabled in any case.")
ALPreferenceManager.setValue(
    'com.aldebaran.debug',
    'DisableLifeAndDialog',
    '1')
