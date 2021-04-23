#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Whole Body Motion - Multiple Effectors control """

import qi
import argparse
import sys
import almath
import motion


def main(session):
    """
        Example of a whole body multiple effectors control "LArm", "RArm" and "Torso"
        Warning: Needs a PoseInit before executing
                 Whole body balancer must be inactivated at the end of the script.
    """
    # Get the services ALMotion & ALRobotPosture.

    motion_service = session.service("ALMotion")
    posture_service = session.service("ALRobotPosture")

    # Wake up robot
    motion_service.wakeUp()

    # Send robot to Stand Init
    posture_service.goToPosture("StandInit", 0.5)

    # end go to Stand Init, begin initialize whole body

    # Enable Whole Body Balancer
    isEnabled  = True
    motion_service.wbEnable(isEnabled)

    # Legs are constrained fixed
    stateName  = "Fixed"
    supportLeg = "Legs"
    motion_service.wbFootState(stateName, supportLeg)

    # Constraint Balance Motion
    isEnable   = True
    supportLeg = "Legs"
    motion_service.wbEnableBalanceConstraint(isEnable, supportLeg)

    # end initialize whole body, define arms motions

    useSensorValues = False

    # Arms motion
    effectorList = ["LArm", "RArm"]

    frame        = motion.FRAME_ROBOT

    # pathLArm
    pathLArm = []
    currentTf = motion_service.getTransform("LArm", frame, useSensorValues)
    # 1
    target1Tf  = almath.Transform(currentTf)
    target1Tf.r2_c4 += 0.08 # y
    target1Tf.r3_c4 += 0.14 # z

    # 2
    target2Tf  = almath.Transform(currentTf)
    target2Tf.r2_c4 -= 0.05 # y
    target2Tf.r3_c4 -= 0.07 # z

    pathLArm.append(list(target1Tf.toVector()))
    pathLArm.append(list(target2Tf.toVector()))
    pathLArm.append(list(target1Tf.toVector()))
    pathLArm.append(list(target2Tf.toVector()))
    pathLArm.append(list(target1Tf.toVector()))

    # pathRArm
    pathRArm = []
    currentTf = motion_service.getTransform("RArm", frame, useSensorValues)
    # 1
    target1Tf  = almath.Transform(currentTf)
    target1Tf.r2_c4 += 0.05 # y
    target1Tf.r3_c4 -= 0.07 # z

    # 2
    target2Tf  = almath.Transform(currentTf)
    target2Tf.r2_c4 -= 0.08 # y
    target2Tf.r3_c4 += 0.14 # z

    pathRArm.append(list(target1Tf.toVector()))
    pathRArm.append(list(target2Tf.toVector()))
    pathRArm.append(list(target1Tf.toVector()))
    pathRArm.append(list(target2Tf.toVector()))
    pathRArm.append(list(target1Tf.toVector()))
    pathRArm.append(list(target2Tf.toVector()))

    pathList = [pathLArm, pathRArm]

    axisMaskList = [almath.AXIS_MASK_VEL, # for "LArm"
                    almath.AXIS_MASK_VEL] # for "RArm"

    coef       = 1.5
    timesList  = [ [coef*(i+1) for i in range(5)],  # for "LArm" in seconds
                   [coef*(i+1) for i in range(6)] ] # for "RArm" in seconds

    # called cartesian interpolation
    motion_service.transformInterpolations(effectorList, frame, pathList, axisMaskList, timesList)

    # end define arms motions, define torso motion

    # Torso Motion
    effectorList = ["Torso", "LArm", "RArm"]

    dy = 0.06
    dz = 0.06

    # pathTorso
    currentTf = motion_service.getTransform("Torso", frame, useSensorValues)
    # 1
    target1Tf  = almath.Transform(currentTf)
    target1Tf.r2_c4 += dy
    target1Tf.r3_c4 -= dz

    # 2
    target2Tf  = almath.Transform(currentTf)
    target2Tf.r2_c4 -= dy
    target2Tf.r3_c4 -= dz

    pathTorso = []
    for i in range(3):
        pathTorso.append(list(target1Tf.toVector()))
        pathTorso.append(currentTf)
        pathTorso.append(list(target2Tf.toVector()))
        pathTorso.append(currentTf)

    pathLArm = [motion_service.getTransform("LArm", frame, useSensorValues)]
    pathRArm = [motion_service.getTransform("RArm", frame, useSensorValues)]

    pathList = [pathTorso, pathLArm, pathRArm]

    axisMaskList = [almath.AXIS_MASK_ALL, # for "Torso"
                    almath.AXIS_MASK_VEL, # for "LArm"
                    almath.AXIS_MASK_VEL] # for "RArm"

    coef       = 0.5
    timesList  = [
                  [coef*(i+1) for i in range(12)], # for "Torso" in seconds
                  [coef*12],                       # for "LArm" in seconds
                  [coef*12]                        # for "RArm" in seconds
                 ]

    motion_service.transformInterpolations(
        effectorList, frame, pathList, axisMaskList, timesList)

    # end define torso motion, disable whole body

    # Deactivate whole body
    isEnabled    = False
    motion_service.wbEnable(isEnabled)

    # Send robot to Pose Init
    posture_service.goToPosture("StandInit", 0.3)

    # Go to rest position
    motion_service.rest()

    # end script


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)