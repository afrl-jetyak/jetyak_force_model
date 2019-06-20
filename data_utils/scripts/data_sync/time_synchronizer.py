#!/usr/bin/env python

"""Topic synchronizer.

This module time synchronize a set of messages in arbitrary topics given
as input in ROS.

Example:
    Example to run

        $ python time_synchronize.py

Todo:
    * Make it general for arbitrary topics.

"""

import os

from numpy import genfromtxt

import gpxpy
import gpxpy.gpx

import rospy
from message_filters import ApproximateTimeSynchronizer, Subscriber
from sensor_msgs.msg import NavSatFix
from sensor_msgs.msg import Range
from wind_sensor.msg import Wind
from current_sensor.msg import WaterCurrent
from std_msgs.msg import Float64
from data_utils.msg import hdg_wrapper_msg
from geometry_msgs.msg import TwistStamped

class Syncer(object):
    """Object to initialize the logging and do the synchronization.

    Attributes:
        logfile_path (str): filenames where logs are saved.
    """

    def __init__(self, logfile_path, gpx_path="", starting_location=()):
        """Constructor of Syncer class to write log files from bags.

        Args:
            logfile_path (str): path to the file where log is saved.
        """

        # Names of files where to save logs.
        #print logfile_path
        self.logfile_path = logfile_path
        self.seq_id = 0
        if 'gpx' in gpx_path:
            gpx_file = open(gpx_path, 'r')
            self.gpx = gpxpy.parse(gpx_file)
            self.current_point = 0
            threshold = 0.00002
            for p in self.gpx.tracks[0].segments[0].points:
                if abs(p.latitude-starting_location[0]) < threshold and abs(p.longitude-starting_location[1]) < threshold:
                    print "found", self.current_point
                    break
                self.current_point += 1
        elif 'csv' in gpx_path:
            self.csv_data = genfromtxt(gpx_path, delimiter=',')
            self.current_point = 0
        else:
            self.gpx = None
            self.csv = None



    def sync_gps_with_sonar_compass_gpsvelocity_wind_current(self, gps, gps_vel, compass_hdg, wind_raw, current_raw, sonar):
        """Synchronizer callback.

        TODO:
            * Arbitrary number of topics.
        """
        #FIXME:NARE
        gps_timestamp = gps.header.stamp.to_sec()
        print("This was called-------1-------------")
        sonar_timestamp = sonar.header.stamp.to_sec()
        velocity_timestamp = gps_vel.header.stamp.to_sec()
        #FIXME: Nare
        print("This was called")
        with open(self.logfile_path, "a") as logfile:
            if self.gpx:
                string_to_write = ','.join([
                    str(gps_timestamp), str(self.gpx.tracks[0].segments[0].points[self.current_point].latitude), str(self.gpx.tracks[0].segments[0].points[self.current_point].longitude),
                    str(sonar_timestamp), str(sonar.range)
                ]) + '\n'
                self.current_point += 4
            elif self.csv:
                string_to_write = ','.join([
                    str(gps_timestamp), str(self.csv[self.current_point,0]), str(self.csv[self.current_point,1]),
                    str(sonar_timestamp), str(sonar.range)
                ]) + '\n'
            else:
                string_to_write = ','.join([
                    str(self.seq_id),
                    str(gps_timestamp), str(gps.latitude), str(gps.longitude),
                    str(velocity_timestamp), str(gps_vel.twist.linear.x), str(gps_vel.twist.linear.y), str(gps_vel.twist.linear.z),
                    #str(compass_hdg.header.stamp.to_sec()),str(compass_hdg.comp_hdg.data),
                    str(compass_hdg.comp_hdg.data),
                    str(sonar_timestamp), str(sonar.range),
                    str(wind_raw.header.stamp.to_sec()), str(wind_raw.windspeedmph), str(wind_raw.winddir),
                    str(current_raw.header.stamp.to_sec()), str(current_raw.current_star_front), str(current_raw.current_port_front), str(current_raw.current_port_rear), str(current_raw.current_star_rear)

                ]) + '\n'
                self.seq_id = self.seq_id + 1
            #FIXME:Nare
            print("--debug--\n" + string_to_write +"---------\n")
            logfile.write(string_to_write)

        # TODO extend to multiple robots.





if __name__ == "__main__":


    # ROS parameters.
    gps_topic = rospy.get_param('~gps_topic', '/jetyak1/mavros/global_position/raw/fix')
    gps_vel_topic = rospy.get_param('~gps_vel_topic', '/jetyak1/mavros/global_position/raw/gps_vel')
    heading_topic = rospy.get_param('~heading_topic', '/jetyak1/mavros/global_position/compass_hdg')
    #hdg_msg = rospy.get_param('~hdg_msg', 'Float64')
    #Nare
    heading_topic = rospy.get_param('~heading_topic_updated', 'data_utils/wrapper_compass_hdg')
    sonar_topic = rospy.get_param('~sonar_topic', '/jetyak1/atu120at/sonar')
    wind_topic = rospy.get_param('~wind_topic', '/jetyak1/wind_sensor/wind_raw')
    current_topic = rospy.get_param('~current_topic', '/jetyak1/current_sensor/current_raw')
    rospy.init_node('time_synchronizer')
    logfile_path = rospy.get_param('~logfile_path', 'log.csv')
    logfile_path = os.path.expanduser(logfile_path)

    file_headline = "seq,Timestamp,Latitude,Longitude,vel_ts,boat_linear_x,boat_linear_y,z,boat_heading,depth_ts,depth,wind_ts,wind_sensor_speed,wind_sensor_dir,current_ts,current_star_front,current_port_front,current_port_rear,current_star_rear\n"
    with open(logfile_path, 'a') as csv_file:
        csv_file.write(file_headline)

    syncer = Syncer(logfile_path)

    # Creating subscribers for filter.
    # TODO pairwise.
    subscribers = []
    subscribers.extend([Subscriber(gps_topic, NavSatFix),
        Subscriber(gps_vel_topic, TwistStamped),
        Subscriber(heading_topic, hdg_wrapper_msg),
        #Subscriber(heading_topic, Float64),
        Subscriber(wind_topic, Wind),
        Subscriber(current_topic, WaterCurrent),
        Subscriber(sonar_topic, Range)
        ])

    # Initialize the callback.
    time_synchronizer = ApproximateTimeSynchronizer(subscribers, 100, 4.0, allow_headerless=True) #FIXME: Nare changed slop from 2 to 4
    #FIXME:NARE
    time_synchronizer.registerCallback(syncer.sync_gps_with_sonar_compass_gpsvelocity_wind_current)

    # Start the node.
    rospy.spin()
