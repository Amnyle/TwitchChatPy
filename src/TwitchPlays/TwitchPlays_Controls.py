from TwitchPlays_KeyCodes import *
import time

avancer = "avancer"
avancer_legerement = "avant"
reculer = "reculer"
reculer_legerement = "recul"
sauter = "sauter"
avancer_et_sauter = "savancer"
reculer_et_sauter = None
sprinter_en_avant = None
sprinter_en_arriere = None


def platofrmer_controls_2d(msg):

    if msg.lower() == avancer: 
        HoldAndReleaseKey(RIGHT_ARROW, 2)

    if msg.lower() == avancer_legerement: 
        HoldAndReleaseKey(RIGHT_ARROW, 1)

    if msg.lower() == reculer:
        HoldAndReleaseKey(LEFT_ARROW, 2)

    if msg.lower() == reculer_legerement:
        HoldAndReleaseKey(LEFT_ARROW, 1)

    if msg.lower() == sauter:
        HoldAndReleaseKey(SPACE, 2)

    if msg.lower() == avancer_et_sauter:
        HoldAndReleaseKey(RIGHT_ARROW, 2)
        HoldAndReleaseKey(SPACE, 2)
        HoldAndReleaseKey(LEFT_SHIFT, 2)

    if msg.lower() == reculer_et_sauter:
        HoldAndReleaseMultipleKeys([LEFT_ARROW, SPACE, LEFT_SHIFT], 2)
      

    if msg.lower() == sprinter_en_avant:
        HoldAndReleaseKey(RIGHT_ARROW, 2)
        HoldAndReleaseKey(LEFT_SHIFT, 2)

    if msg.lower() == sprinter_en_arriere:
        HoldAndReleaseKey(LEFT_ARROW, 2)
        HoldAndReleaseKey(LEFT_SHIFT, 2)

