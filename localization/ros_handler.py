import rospy
import numpy as np

from drive_msgs.msg import *
from std_msgs.msg import Float32
from ublox_msgs.msg import NavATT, NavPVT
from sensor_msgs.msg import Imu

from navatt_subs import NAVATT
from navpvt_subs import NAVPVT
from imu_meas_subs import IMUMEAS

from pyproj import Proj, Transformer

class ROSHandler():
    def __init__(self, map):
        rospy.init_node('localization', anonymous=False)
        self.MAP = map
        self.set_values()
        self.set_protocol()

    def set_values(self):
        self.heading_fixed = False
        self.navatt = NAVATT()
        self.navpvt = NAVPVT()
        self.imumeas = IMUMEAS()
        self.map_name = None
        self.transformer = None
        self.local_pose = [0,0]   
        self.curr_lane_id = None

    def set_protocol(self):
        rospy.Subscriber("/ublox/navatt", NavATT, self.navatt.callback)
        rospy.Subscriber("/ublox/navpvt", NavPVT, self.navpvt.callback)
        rospy.Subscriber("/ublox/imu_meas", Imu, self.imumeas.callback)
        rospy.Subscriber('/SystemStatus', SystemStatus, self.system_status_cb)
        rospy.Subscriber('/LaneData', LaneData, self.lanedata_cb)
        self.fix_heading_pub = rospy.Publisher('/localization/heading', Float32, queue_size=1)
       
    def system_status_cb(self, msg):
        if msg.headingSet.data == 1:
            self.heading_fixed = True 
        else:
            self.heading_fixed = False

    def lanedata_cb(self, msg):
        self.curr_lane_id = str(msg.currentLane.id.data)

    def publish(self, heading):
        self.fix_heading_pub.publish(Float32(heading))