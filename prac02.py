from turtle import *
import numpy as np
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QLabel

import time

# setting
num = 100 # number of car
time_limit = 100000
total_distance = 10000
each_line = 500
win_w, win_h = 130000, 3000
limit_speed = 16   # meter per second
prob_fun = np.random.poisson
prob_cond = 0.1  # lambda
safe_dist = 40    # safe distance
car_shape = "resized_car.gif"


screen = Screen()
screen.screensize(win_w, win_h)

class Car(Turtle):
    num_of_car = 1
    def __init__(self, start_pos, start_velocity):
        super().__init__()
        self.start_pos = start_pos
        self.id = Car.num_of_car
        Car.num_of_car += 1
        self.next = None
        self.prev = None
        self.up()
        self.speed(0)
        self.setx(-start_pos)


        self.max_velocity = start_velocity
        self.velocity = start_velocity   # 현재 속
        self.prev_velocity = start_velocity  # 1초 전 속도
        self.decel_token = (False, 0)
        self.acel_token = True

    def break_signal(self):
        return
        # if you use below code, screen can be slow
        t = Turtle()
        t.hideturtle()
        t.penup()
        t.speed(0)
        t.setpos(self.pos())
        t.penup()
        t.left(90)
        t.forward(20)
        t.write("break!", font = 20)
        t.clear()
        del t


    def go(self):
        self.prev_velocity = self.velocity



        if self.prev == None:

            self.acel_token = True

            # 2번
            deceleration1 = prob_fun(prob_cond)
            self.velocity -= deceleration1
            if self.velocity < 0:
                self.velocity = 0

            if deceleration1 > 0 and self.velocity != 0:
                self.acel_token = False
                self.break_signal()

            # 3번.
            if (self.acel_token == True) and \
                (self.max_velocity > self.velocity) :
                self.velocity += 1 # 나중에 조절.


        elif self.prev != None:
            self.acel_token = True

            # 1번.
            if self.decel_token[0] == True:

                if self.prev.pos()[0] - (self.velocity + self.pos()[0]) > safe_dist:
                    pass
                else:
                    deceleration2 = prob_fun(prob_cond)
                    self.velocity -= (self.decel_token[1] + deceleration2)
                    if self.velocity < 0 : self.velocity = 0
                    if deceleration2 > 0 and self.velocity != 0:
                        self.acel_token = False
                        self.break_signal()
                self.decel_token = (False, 0)

            delta = self.prev.velocity - self.prev.prev_velocity
            if delta < 0:
                self.decel_token = (True, delta)

            # 2번


            deceleration = prob_fun(prob_cond)
            self.velocity -= deceleration
            if self.velocity < 0: self.velocity = 0
            if deceleration > 0 and self.velocity != 0:
                self.acel_token = False
                self.break_signal()

            # 3번.
            if (self.acel_token == True) and  \
                    (self.max_velocity > self.velocity) and \
                    (self.prev.pos()[0] - (self.velocity + self.pos()[0]) > safe_dist): # 안전 거리 조정 필
                self.velocity += 1 # 나중에 조



        if self.prev == None:
            self.forward(self.velocity)

        elif self.velocity + self.pos()[0] + safe_dist < self.prev.pos()[0]:
            self.forward(self.velocity)
        else:
            self.velocity = self.prev.pos()[0] - (safe_dist + self.pos()[0])

        if self.next == None:
            return True  # 한번 순환이 끝났다.
        else:
            self.next.go()


def make_line(total_distance, each_line):
    t = Turtle()
    t.speed(0)
    len_line = 20

    i = 0
    pont_size = 50
    while (total_distance >= each_line):
        t.left(90)
        t.forward(len_line)
        t.left(180)
        t.forward(len_line * 2)
        t.penup()
        t.forward(20)
        t.write(str(each_line * i) + "m", font = pont_size)
        i += 1
        t.left(180)
        t.forward(20)
        t.forward(len_line)
        t.right(90)
        t.pendown()
        t.forward(each_line)
        total_distance -= each_line


    t.left(90)
    t.forward(len_line)
    t.left(180)
    t.forward(len_line * 2)
    t.penup()
    t.forward(20)
    t.write(str(each_line * i) + "m", font = pont_size)
    i += 1
    t.left(180)
    t.forward(20)
    t.forward(len_line)
    t.right(90)
    t.pendown()


    t.forward(total_distance)
    t.left(90)
    t.forward(len_line)
    t.left(180)
    t.forward(len_line*2)

    t.penup()
    t.forward(20)
    t.write(str(each_line * (i-1) + total_distance) + "m", font = pont_size)
    t.hideturtle()

make_line(total_distance, each_line)



# make car
screen.addshape(car_shape)
cars = []
for i in range(num):
    if i == 0:
        new = Car(i*50, limit_speed)
        new.shape(car_shape)
        cars.append(new)
        old = new
    else:
        new = Car(i*50, limit_speed)
        new.shape(car_shape)
        new.prev = old
        old.next = new
        cars.append(new)
        old = new



# make timer
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 200, 100)
        self.setWindowTitle('Timer')

        self.label = QLabel(self)
        self.label.setGeometry(100, 40, 200, 20)


    def time_up(self, time):
        self.label.setText(str(time) + "s")

app = QApplication(sys.argv)
mainWindow = MainWindow()
mainWindow.show()

for time in range(time_limit):
    cars[0].go()  # 처음차 출발하면 자동으로 다음 차 출발
    mainWindow.time_up(str(time))

screen.mainloop()



