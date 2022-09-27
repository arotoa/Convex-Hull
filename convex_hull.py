from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25


#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

	# Class constructor
	def __init__(self):
		super().__init__()
		self.pause = False

	# Some helper methods that make calls to the GUI, allowing us to send updates
	# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line, color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self, line, color):
		self.showTangent(line, color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon, color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self, polygon):
		self.view.clearLines(polygon)

	def showText(self, text):
		self.view.displayStatusText(text)

	# This is the method that gets called by the GUI and actually executes
	# the finding of the hull
	def compute_hull(self, points, pause, view):
		self.pause = pause
		self.view = view
		assert (type(points) == list and type(points[0]) == QPointF)

		t1 = time.time()
		points = sorted(points, key=lambda QPointF: QPointF.x())
		t2 = time.time()

		t3 = time.time()
		# solve convex hull and get final points
		final_hull = divide_and_conquer(points)
		final_points = final_hull.get_points()
		polygon = [QLineF(final_points[i], final_points[(i + 1)]) for i in range(len(final_points) - 1)]
		polygon.append(QLineF(final_points[0], final_points[len(final_points) - 1]))

		# TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon, RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4 - t3))


def divide_and_conquer(sorted_points):
	length = len(sorted_points)

	# base case
	if length == 1:
		# create new node with point
		new_node = Node(sorted_points[0])
		# create hull with new node
		new_hull = Hull()
		new_hull.change_left(new_node)
		new_hull.change_right(new_node)
		return new_hull

	# combine two sides
	else:
		left_side = sorted_points[:length // 2]
		right_side = sorted_points[length // 2:]
		left_hull = divide_and_conquer(left_side)
		right_hull = divide_and_conquer(right_side)
		return combine_hulls(left_hull, right_hull)


def combine_hulls(L, R):
	# find both tangents
	upper_tan = find_upper_tangent(L, R)
	lower_tan = find_lower_tangent(L, R)
	# first index is always left hull, second is right hull
	left_node = upper_tan[0]
	right_node = upper_tan[1]
	#point the two nodes to each other
	left_node.change_clockwise(right_node)
	right_node.change_counter(left_node)
	left_node = lower_tan[0]
	right_node = lower_tan[1]
	left_node.change_counter(right_node)
	right_node.change_clockwise(left_node)

	# create new hull with new left and right points
	new_hull = Hull()
	new_hull.change_left(L.left_most_val)
	new_hull.change_right(R.right_most_val)
	return new_hull


def find_upper_tangent(L, R):
	# current nodes we are testing
	left_current_node = L.right_most_val
	right_current_node = R.left_most_val
	correct_left_point = left_current_node.point
	correct_right_point = right_current_node.point

	# get initial slope
	temp = get_slope(correct_left_point, correct_right_point)

	done = False
	while not done:
		done = True
		is_upper = False

		# left hull
		while not is_upper:
			#choose next counterclockwise node and get slope
			left_current_node = left_current_node.counter_node
			test_point = left_current_node.point
			test_slope = get_slope(test_point, correct_right_point)
			# if new slope is less than original slope, update current point
			if test_slope < temp:
				temp = test_slope
				correct_left_point = test_point
				done = False
			# if new slope is not correct, then break and go back to correct node
			else:
				is_upper = True
				left_current_node = left_current_node.clockwise_node

		# right hull
		is_upper = False
		while not is_upper:
			#choose next clockwise node and get slope
			right_current_node = right_current_node.clockwise_node
			test_point = right_current_node.point
			test_slope = get_slope(correct_left_point, test_point)
			# if new slope is greater than original slope, update current point
			if test_slope > temp:
				temp = test_slope
				correct_right_point = test_point
				done = False
			# if new slope is not correct, then break and go back to correct node
			else:
				is_upper = True
				right_current_node = right_current_node.counter_node

	# return list of two nodes that are upper tangent
	upper_tan_nodes = [left_current_node, right_current_node]
	return upper_tan_nodes


def find_lower_tangent(L, R):
	# current nodes we are testing
	left_current_node = L.right_most_val
	right_current_node = R.left_most_val
	correct_left_point = left_current_node.point
	correct_right_point = right_current_node.point

	# get initial slope
	temp = get_slope(correct_left_point, correct_right_point)


	done = False
	while not done:
		done = True
		is_lower = False

		# left hull
		while not is_lower:
			#choose next clockwise node and get slope
			left_current_node = left_current_node.clockwise_node
			test_point = left_current_node.point
			test_slope = get_slope(test_point, correct_right_point)
			# if new slope is greater than original slope, update current point
			if test_slope > temp:
				temp = test_slope
				correct_left_point = test_point
				done = False
			# if new slope is not correct, then break and go back to correct node
			else:
				is_lower = True
				left_current_node = left_current_node.counter_node

		# right hull
		is_lower = False
		while not is_lower:
			#choose next counterclockwise node and get slope
			right_current_node = right_current_node.counter_node
			test_point = right_current_node.point
			test_slope = get_slope(correct_left_point, test_point)
			# if new slope is less than original slope, update current point
			if test_slope < temp:
				temp = test_slope
				correct_right_point = test_point
				done = False
			# if new slope is not correct, then break and go back to correct node
			else:
				is_lower = True
				right_current_node = right_current_node.clockwise_node

	# return list of two nodes that are lower tangent
	lower_tan_nodes = [left_current_node, right_current_node]
	return lower_tan_nodes


def get_slope(point_one, point_two):
	return (point_one.y() - point_two.y()) / (point_one.x() - point_two.x())


class Node:
	def __init__(self, data=QPointF):
		self.point = data
		self.clockwise_node = self
		self.counter_node = self

	def change_clockwise(self, data):
		self.clockwise_node = data

	def change_counter(self, data):
		self.counter_node = data


class Hull:
	def __init__(self):
		self.left_most_val = None
		self.right_most_val = None

	def change_left(self, data=Node):
		self.left_most_val = data

	def change_right(self, data=Node):
		self.right_most_val = data

	def get_points(self):
		hull_points = []
		curr_node = self.left_most_val
		first_point = curr_node.point
		hull_points.append(curr_node.point)
		curr_node = curr_node.counter_node
		# go through linked list
		while True:
			if curr_node.point != first_point:
				hull_points.append(curr_node.point)
				curr_node = curr_node.counter_node
			else:
				break
		return hull_points
