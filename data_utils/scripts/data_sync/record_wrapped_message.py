#!/usr/bin/env python

"""

    This module takes as input in_bag_filename, out_bag_filename and topic Name
    uses in_bag_filename to read all messages and in addition to add timestamp to the topic_name
    topic. Finally it creates a intermediate output_bag_filename with that new timestamped topicself.
    and plays it back

    File Name: record_wrapped_message.py
    Author: Nare Karapetyan
    Data Created: Feb 10 2019
    Date Last Modified: Feb 10 2019
"""

from data_utils.msg import hdg_wrapper_msg
from std_msgs.msg import Bool
import sys
import rosbag
import rospy
import os
import subprocess

def readFromRosBagAndPutTimestamp(in_bag_filename, out_bag_filename, topic_name, time_stamp_topic):
    with rosbag.Bag(out_bag_filename, 'w') as outbag:
        for topic, msg,t in rosbag.Bag(in_bag_filename).read_messages():
            new_msg = hdg_wrapper_msg()
            if topic == time_stamp_topic:
                new_msg.header = msg.header
                print("-----------")
                print(new_msg.header)
                print ("------------------")
            if topic == topic_name:
                #msg_header = msg.header.stamp if msg._has_header else t
                new_msg.comp_hdg = msg
                new_msg.header.stamp = t
                print(new_msg)
                outbag.write("data_utils/wrapper_compass_hdg", new_msg, t)
            outbag.write(topic, msg, t)

def rewriteTopicWithTimestamp(in_bag_filename, out_bag_filename, topic_name):
    """
    Will read all messages and write all into new bag file and in addition will add new topic with modified messages

    Parameters:
    ----------

    in_bag_filename
    out_bag_filename
    topic_name          the name of the topic that needs to be rewritten

    Return:
    ------
    NONE

    """
    with rosbag.Bag(out_bag_filename, 'w') as outbag:
        for topic, msg,t in rosbag.Bag(in_bag_filename).read_messages():
            new_msg = hdg_wrapper_msg()
            if topic == topic_name:
                #msg_header = msg.header.stamp if msg._has_header else t
                new_msg.comp_hdg = msg
                new_msg.header.stamp = t
                print(new_msg)
                outbag.write("data_utils/wrapper_compass_hdg", new_msg, t)
            outbag.write(topic, msg, t)



if __name__ == '__main__':

    rospy.init_node('bag_rewriting_node')
    #pub = rospy.Publisher("data_utils/is_ready", Bool, queue_size = 2)
    #rospy.sleep(1.) # sleeps for 10 sec
    print("---------")
    #pub.publish(False)

    in_bag_filename = rospy.get_param('~input_bag_filename', 'input.bag')
    out_bag_filename = rospy.get_param('~output_bag_filename', 'output.bag')
    topic_name = rospy.get_param('~topic_name', '/jetyak1/mavros/global_position/compass_hdg')

    rewriteTopicWithTimestamp(in_bag_filename, out_bag_filename, topic_name)

    if( not os.path.isfile(out_bag_filename)):
        print("The file does not exist")
        exit()
    rosbag_proc = subprocess.Popen("rosbag play " + out_bag_filename + " --clock -r 50", shell=True, stdout=subprocess.PIPE)


    # not a good solution but just a quick way of announcing that
    # that the node has finished recording
    #rospy.sleep(5.)
    #pub.publish(True)
    #rospy.signal_shutdown("The node finished its work!")
