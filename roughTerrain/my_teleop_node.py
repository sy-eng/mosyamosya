import sys
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from geometry_msgs.msg import Vector3
from pynput import keyboard

class MyTeleop(Node):
	def key_pressed(self, keyData):
		try:
			key = keyData.char
			
			if key == 'i':
				self.vel.linear.x += 0.1
			elif key == 'm':
				self.vel.linear.x -= 0.1
			elif key == 'l':
				self.vel.angular.z += 0.05
			elif key == 'j':
				self.vel.angular.z -= 0.05
			elif key == 'e':
				self.panTiltVel.z += 0.05
			elif key == 'c':
				self.panTiltVel.z -= 0.05
			elif key == 's':
				self.panTiltVel.y += 0.05
			elif key == 'f':
				self.panTiltVel.y -= 0.05
			elif key == 'q':
				self.arm1Angle.y += 0.01
			elif key == 'w':
				self.arm1Angle.y -= 0.01
			elif key == 'z':
				self.arm2Angle.y += 0.01
			elif key == 'x':
				self.arm2Angle.y -= 0.01
			else: 
				self.vel.linear.x = 0.0
				self.vel.angular.z = 0.0
				self.panTiltVel.z = 0.0
				self.panTiltVel.y = 0.0		
			
			print(self.vel.linear.x, self.vel.angular.z, self.panTiltVel.z, self.panTiltVel.y)
		
			self.publisher.publish(self.vel)
			self.publisherPanTilt.publish(self.panTiltVel)
			self.publisherArm1Angle.publish(self.arm1Angle)
			self.publisherArm2Angle.publish(self.arm2Angle)

		except AttributeError:
			return
			
		
	def __init__(self):
		super().__init__('my_teleop_node')
		self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
		self.vel = Twist()
		self.vel.linear.x = 0.0
		self.vel.angular.z = 0.0
		self.publisherPanTilt = self.create_publisher(Vector3, 'cmd_joint_vel', 10)
		self.panTiltVel = Vector3()
		self.panTiltVel.z = 0.0
		self.panTiltVel.y = 0.0		
		self.publisherArm1Angle = self.create_publisher(Vector3, 'cmd_arm1_angle', 10)
		self.arm1Angle = Vector3()
		self.arm1Angle.y = 0.0
		self.publisherArm2Angle = self.create_publisher(Vector3, 'cmd_arm2_angle', 10)
		self.arm2Angle = Vector3()
		self.arm2Angle.y = 0.0
		
		print("Press key on the simulator window.")
		
		with keyboard.Listener(on_press = self.key_pressed) as listener:
			listener.join()

def main():
	try:
		rclpy.init()
		node = MyTeleop()
			
		rclpy.spin(node)
	except KeyboardInterrupt:
		print('Ctrl + C is pressed')
	except ExternalShutdownException:
		sys.exit(1)
	finally:
		rclpy.try_shutdown()
		

