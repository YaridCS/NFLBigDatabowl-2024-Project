import math
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.animation as animation
import numpy as np
from numpy import sin, cos, pi, linspace
import random
import pandas as pd
import time

def myround(x, base = 10):
    return base * round(x/base)

def orientation_translation(x):
    'translates input orientation from BigDataBowl to our orientation'
    return (x+90-(2*x))%360

def getAngle(a, b, c):
    'Returns the angle centered at b'
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang + 360 if ang < 0 else ang

def getPoint(angle, radius, start_x, start_y):
    x = (radius*math.cos(math.radians(angle)))
    y = (radius*math.sin(math.radians(angle)))
    return(round(x,5)+start_x,round(y,5)+start_y)
''' 
print(getAngle((10, 0), (0, 0), (0, 10)))
print(getPoint(90,10,0,0))

print(getAngle((10, 0), (0, 0), (7.07107, 7.07107)))
print(getPoint(45,10,0,0))

print(getPoint(22.5,10,0,0))
print(getAngle((10,0),(0,0),(9.2388, 3.82683)))
'''
def get_slice_loc(angle, slices):
    interval = 360/slices
    return int(angle//interval)

class Player():

    def __init__(self, nflId, height, weight, position, x, y, team, orietnation = 0, display_name = 'John Doe'):
        self.nflId = nflId
        self.height = height
        self.weight = weight
        self.position = position
        self.name = display_name
        self.team = team
        self.orientation = orientation
        self.x = x
        self.y = y

    def __repr__(self):
        return '{},{}, {} inch {} lb {} for {}, {} deg'.format(self.x, self.y, self.height, self.weight, self.position, self.team, self.orientation)

    def __str__(self):
        return self.__repr__()


def in_minicone(origin_x, origin_y, radius, mid_angle, arc_radius, player_x, player_y):
    if math.dist([origin_x,origin_y],[player_x, player_y]) > radius:
        return False
    player_angle = getAngle([origin_x+10,origin_y],[origin_x,origin_y],[player_x, player_y])
    start_angle = mid_angle - arc_radius
    end_angle = mid_angle + arc_radius
    #print(player_angle, start_angle, end_angle)
    #print(dist_to_angle(mid_angle, player_angle))
    if dist_to_angle(mid_angle, player_angle) >= arc_radius:
        return False
    return True

class Offensive_Player(Player):

    def __init__(self, nflId, height, weight, position, x, y, team, orientation = 0, display_name = 'John Doe'):
        self.nflId = nflId
        self.height = height
        self.weight = weight
        self.position = position
        self.name = display_name
        self.team = team
        self.x = x
        self.y = y
        self.engaged = False
        self.blocking = False
        self.Defensive = False
        self.orientation = orientation
        self.danger = 0

    def find_defender(self,defenders, max_dist = 2):
        min_dist = 999
        min_defender = False
        for i in range(len(defenders)):
            defender = defenders[i]
            dist = math.dist([self.x, self.y],[defender.x,defender.y])
            if dist < min_dist and dist <= max_dist:
                min_dist = dist
                min_defender = defender
        if min_defender != False:
            min_defender.engaged = True
            min_defender.blocked_by.append(self)
            self.enaged = True
            self.blocking = defender
            #print('blocker at {},{} engaged with defender at {},{}; dist of {}'.format(self.x, self.y, min_defender.x, min_defender.y, min_dist))
        return min_defender

    def updated_find_defender(self,defenders, mid_angle, cone_range, rb_x, rb_y, max_dist = 2):
        min_dist = 999
        min_defender = False
        for i in range(len(defenders)):
            defender = defenders[i]
            if in_minicone(self.x, self.y, max_dist, mid_angle, cone_range, defender.x, defender.y):
                if math.dist([rb_x,rb_y],[self.x,self.y]) <= math.dist([rb_x,rb_y],[self.x,self.y]):
                    ##If rb is closer to defender than OL, OL must be behind defender. 
                    dist = math.dist([self.x, self.y],[defender.x,defender.y])
                    if dist < min_dist and dist <= max_dist:
                        min_dist = dist
                        min_defender = defender
        if min_defender != False:
            min_defender.engaged = True
            min_defender.blocked_by.append(self)
            self.engaged = True
            self.blocking = defender
            #print('blocker at {},{} engaged with defender at {},{}; dist of {}'.format(self.x, self.y, min_defender.x, min_defender.y, min_dist))
        return min_defender

    def get_base_danger(self, defenders, rb_x, rb_y):
        if self.engaged == True:
            self.danger == 0
        candidates = []
        O_dist = math.dist([self.x, self.y], [rb_x, rb_y])
        for defender in defenders:
            D_dist = math.dist([defender.x, defender.y], [rb_x, rb_y])
            if D_dist > O_dist:
                candidates.append(defender)
        danger = 0
        if len(candidates) == 0:
            self.danger = 0 #Keep this? Yes.
            return 0
        for item in candidates:
            danger += item.danger/2
            #danger = distance_variable *(2/(2**n)), so distance_variable *(2/(2**n+1))= the original danger*(1/2)
        danger = -1*(danger/len(candidates))
        self.danger = danger
        return danger
        
            
        
            
        
                
            
        
                
                
def getSlope(angle):
    return math.tan(math.radians(angle))

def get_baseline(x1, y1, baseline):
    x = 10*math.cos(math.radians(baseline))
    y = 10*math.sin(math.radians(baseline))
    x = x+x1
    y = y+y1
    return [x,y]
    
def get_inner_angle(x1, y1, x2, y2, baseline):
    baseline_projected_point = get_baseline(x1, y1, baseline)
    a1 = getAngle([x2,y2],[x1,y1],baseline_projected_point)
    a2 = getAngle(baseline_projected_point,[x1,y1],[x2,y2])
    return min(a1,a2)
    
    
def calcAdjacent(angle, hypotenuse):
    cos = math.cos(math.radians(angle))
    adjacent = cos*hypotenuse
    return adjacent

def getPerpIntersect(x1,y1,x2,y2, angle):
    inner_angle = get_inner_angle(x1,y1,x2,y2, angle)
    stretch = calcAdjacent(inner_angle, math.dist([x1,y1],[x2,y2]))
    #print(stretch)
    x = stretch*math.cos(math.radians(angle))
    y = stretch*math.sin(math.radians(angle))
    #print(x,y)
    return [x,y]


def midpoint(points):
    x = 0
    y = 0
    for point in points:
        x += point[0]
        y += point[1]
    x = x/len(points)
    y = y/len(points)
    return [x,y]
                        
    
            

class Defensive_Player(Player):
    
    def __init__(self, nflId, height, weight, position, x, y, team, orientation = 0, display_name = 'John Doe'):
        self.nflId = nflId
        self.height = height
        self.weight = weight
        self.position = position
        self.name = display_name
        self.team = team
        self.x = x
        self.y = y
        self.engaged = False
        self.blocked_by = []
        self.danger = False
        self.Defensive = True
        self.orientation = orientation

    def __repr__(self):
        return '{},{}, {} inch {} lb {} for {}, engaged = {}, danger of {}'.format(self.x, self.y, self.height, self.weight,
                                                                                   self.position, self.team,self.engaged, self.danger)

    def calc_theta_one(self, blocker_x, blocker_y, rb_x, rb_y):
        angle = getAngle([blocker_x, blocker_y],[self.x, self.y],[rb_x, rb_y])
        angle2 = getAngle([rb_x, rb_y],[self.x, self.y],[blocker_x, blocker_y])
        return min(angle, angle2)

    def calc_theta_two(self, blocker_x, blocker_y, rb_x, rb_y, midline):
        dist = ((blocker_x - rb_x)*0.75)
        stretch = dist/math.cos(math.radians(midline))
        proj_x = stretch*math.cos(math.radians(midline)) #Projected x is 75% of the way from rb to offensive player in a direction
        slope = getSlope(rb_x, rb_y, midline)
        proj_y = stretch*math.sin(math.radians(midline)) + rb_y
        #print(proj_x,proj_y)
        angle = getAngle([blocker_x, blocker_y],[self.x, self.y],[proj_x, proj_y])
        angle2 = getAngle([proj_x, proj_y],[self.x, self.y],[blocker_x, blocker_y])
        #print('t2 opts {} {}'.format(angle, angle2))
        return min(angle, angle2)

    def new_theta_two(self, blocker_x, blocker_y, rb_x, rb_y, midline):
        x_dist = blocker_x - rb_x
        if x_dist < 0:
            x_dist *= -1
        bridge = math.dist([blocker_x, blocker_y], [rb_x, rb_y])
        proj_x = blocker_x + x_dist*0.4 + 2
        stretch = (proj_x - rb_x)/math.cos(math.radians(midline))
        proj_y = stretch*math.sin(math.radians(midline)) + rb_y
        angle = getAngle([blocker_x, blocker_y],[self.x, self.y],[proj_x, proj_y])
        angle2 = getAngle([proj_x, proj_y],[self.x, self.y],[blocker_x, blocker_y])
        #print('t2 opts {} {}'.format(angle, angle2))
        blocker_leverage = min(getAngle([blocker_x, blocker_y],[proj_x,proj_y],[self.x, self.y]),
                               getAngle([self.x, self.y],[proj_x,proj_y],[blocker_x, blocker_y]))
        #print('Blocker Lev = {}'.format(blocker_leverage))
        return min(angle, angle2)
        
    

    def new_calc_leverage(self, blocker_x, blocker_y, rb_x, rb_y, midline):
        'This is really the deprecated old leverage function, but for simplicity we just switched the function names'
        t1 = self.calc_theta_one(blocker_x, blocker_y, rb_x, rb_y)
        #print("t1 = {}".format(t1))
        t2 = self.new_theta_two(blocker_x, blocker_y, rb_x, rb_y, midline)
        #print("t2 = {}".format(t2))
        #self.leverage = t2
        self.leverage = (t2-t1)

    def calc_single_leverage(self, rb_x, rb_y, midline):
        blocker = self.blocked_by[0]
        blocker_x = blocker.x
        blocker_y = blocker.y
        proj = getPerpIntersect(rb_x, rb_y, self.x, self.y, midline)
        a1 = getAngle([blocker_x, blocker_y],[self.x, self.y],proj)
        a2 = getAngle(proj,[self.x, self.y],[blocker_x, blocker_y])
        angle = min(a1,a2)
        return angle/180

    def calc_multiple_leverage(self, rb_x, rb_y, midline):
        coords = []
        for player in self.blocked_by:
            coords.append([player.x, player.y])
        Midpoint = midpoint(coords)
        blocker_x = Midpoint[0]
        blocker_y = Midpoint[1]
        proj = getPerpIntersect(rb_x, rb_y, self.x, self.y, midline)
        a1 = getAngle([blocker_x, blocker_y],[self.x, self.y],proj)
        a2 = getAngle(proj,[self.x, self.y],[blocker_x, blocker_y])
        angle = min(a1,a2)
        mult = (angle/180)/len(self.blocked_by)
        options = [mult]
        ##First, calculate the leverage of the midpoint, and shrink it to account for the double team
        ##Then,calculate the single teams
        ##Return the option that gives the defender the worst leverage.
        for blocker in self.blocked_by:
            blocker_x = blocker.x
            blocker_y = blocker.y
            proj = getPerpIntersect(rb_x, rb_y, self.x, self.y, midline)
            a1 = getAngle([blocker_x, blocker_y],[self.x, self.y],proj)
            a2 = getAngle(proj,[self.x, self.y],[blocker_x, blocker_y])
            angle = min(a1,a2)
            options.append((angle/180)/len(self.blocked_by))
        return min(options)
            
            
        

    def calc_leverage(self, rb_x, rb_y, midline):
        if len(self.blocked_by) == 1:
            return self.calc_single_leverage(rb_x, rb_y, midline)
        elif len(self.blocked_by) == 0:
            return 1
        else:
            return self.calc_multiple_leverage(rb_x, rb_y, midline)
        





def Get_intersect_distance(origin, angle, desired_y, hypotenuse = True):
    x = origin[0]
    y = origin[1]
    angle = normalize_angle(angle)
    ###Make sure angle is poiting in the proper direction###
    if desired_y > y and angle > 180:
        return False
    if desired_y < y and angle < 180:
        return False
    if angle == 180 or angle == 0:
        return False
    if angle == 90 or angle == 270:
        if hypotenuse == False:
            return [x,desired_y]
        else:
            return(abs(desired_y - y))
    else:
        adjacent = math.dist(origin, [x,desired_y])
        #print(angle)
        if angle > 0 and angle < 90:
            inner_angle = 90-angle
        elif angle > 90 and angle < 180:
            inner_angle = angle - 90
        elif angle > 180 and angle < 270:
            inner_angle = 270 - angle
        elif angle > 270:
            inner_angle = angle - 270
        Hypotenuse  = calc_hypotenuse(inner_angle, adjacent)
        #print(hypotenuse)
        point = project_point(origin, angle, hypotenuse)
    if hypotenuse == True:
        return Hypotenuse
    return point       
         
def calc_hypotenuse(angle, adjacent):
    h = adjacent/math.cos(math.radians(angle))
    return h

def project_point(origin, angle, distance):
    x = distance*math.cos(math.radians(angle)) + origin[0]
    y = distance*math.sin(math.radians(angle)) + origin[1]
    return [x,y]

def segment_area(angle, radius):
    a = math.radians(angle)
    answer = ((a- math.sin(a))/2)*(radius**2)
    return abs(answer)

def triangle_area_by_points(p1, p2, p3):
    #print(p1,p2,p3)
    answer = abs((p1[0]*(p2[1]-p3[1])) + (p2[0]*(p3[1]-p1[1])) + (p3[0]*(p1[1]-p2[1])))
    answer = answer/2
    return answer

def sector_area(angle, radius):
    area = math.pi * radius * radius
    answer = (angle/360)*area
    return answer

def get_y_intercept(center, angle):
    y = center[1]
    x = center[0]
    answer = y - (x*getSlope(angle))
    return answer

def get_x(m, y, b):
    return ((y-b)/m)

def get_proj_x(center, angle, y):
    if angle == 0 or angle == 180:
        return [center[0]+1000, y]
    b = get_y_intercept(center, angle)
    #print(b)
    x = get_x(getSlope(angle), y, b)
    return [x,y]

def between(p1,p2, candidate):
    lst = [p1,p2,candidate]
    lst.sort()
    if lst[1] == candidate:
        return True
    return False

def test_in_bounds(top_y, bot_y):
    if top_y < 0 or bot_y < 0 or top_y > 53.33 or bot_y > 53.33:
        return False
    return True

def get_ovular_sector(center, start_angle, end_angle, y_boundary, radius):
    CP1 = get_proj_x(center, start_angle, y_boundary)
    CP2 = get_proj_x(center, end_angle, y_boundary)
    #print(CP1,CP2)
    if math.dist(CP1, center) < math.dist(CP2, center):
        P1 = CP1
    else:
        P1 = CP2
    #print(P1)
    ###We continue along the inersected angle to get p2
    if P1 == CP1:
        P2 = getPoint(start_angle, radius, center[0], center[1])
    else:
        P2 = getPoint(end_angle, radius, center[0], center[1])
    P3 = get_circle_intersection(radius, y_boundary, center)
    if math.dist(P3[1], P2) < math.dist(P3[0], P2):
        P3 = P3[1]
    else:
        P3 = P3[0]
    #Unknown
    #print(P1, P2, P3)
    segment = segment_area(min(getAngle(P2,center,P3), getAngle(P3,center,P2)), radius)
    triangle = triangle_area_by_points(P1, P2, P3)
    return (segment + triangle)

def get_triangle(start_angle, end_angle, center, proj_y):
    P1 = center
    P2 = get_proj_x(center, start_angle, proj_y)
    P3 = get_proj_x(center, end_angle, proj_y)
    return triangle_area_by_points(P1, P2,P3)

def get_circle_intersection(r, y, center):
    h = center[0]
    k = center[1]
    answer = math.sqrt((r**2)-((y-k)**2))
    a1 = (answer * -1) + h
    a2 = answer + h
    return [[a1, y], [a2,y]]

        
    
    
    

def in_bounds_sector_area(center, radius, start_angle, end_angle, top_y, bot_y, y_boundry,theta = False):
    if theta is False:
        theta = dist_to_angle(start_angle, end_angle)
    if test_in_bounds(top_y, bot_y):
        #print('in bounds')
        return 1
    else:
        sectorArea = sector_area(theta, radius)
        #print(sectorArea)
        if between(top_y, bot_y, y_boundry):
            #print('Oval')
            #print(center, start_angle, end_angle, y_boundry, radius)
            answer = sectorArea - get_ovular_sector(center, start_angle, end_angle, y_boundry, radius)
            #print(answer)
        else:
            #print('triangle')
            answer = get_triangle(start_angle, end_angle, center, y_boundry)
            #print(answer)
    return answer/sectorArea
    
    
    



        
        

class slice():

    def __init__(self, center_x, center_y, radius, top_x, top_y, bot_x, bot_y, start_angle, end_angle):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.bot_x = bot_x
        self.bot_y = bot_y
        self.top_x = top_x
        self.top_y = top_y
        self.offenders = []
        self.defenders = []
        self.length = 0
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.mid_angle = (self.start_angle + (dist_to_angle(self.start_angle, self.end_angle)/2))%360
        self.danger = False
        self.in_bounds = self.get_in_bounds()
        self.sidelining = self.Get_Sideline()


    def __repr__(self):
        answer = 'slice from {} to {} has a danger of {} and {} members\n'.format(self.start_angle%360, self.end_angle%360, self.danger, self.length)
        if self.length != 0:
            answer += '     OFFENDERS\n'
            for item in self.offenders:
                answer += ('         '+str(item) + '\n')
            answer += '     DEFENDERS\n'
            for item in self.defenders:
                answer += ('         '+str(item) + '\n')
        return answer


    def __str__(self):
        return 'slice from {} to {} has {} members'.format(self.start_angle, self.end_angle, self.length)

    def get_in_bounds(self):
        if self.center_y >= 10 and self.center_y <= 43.33:
            return 1
        elif self.center_y <= 10:
            return in_bounds_sector_area([self.center_x, self.center_y], self.radius, self.start_angle, self.end_angle, self.top_y, self.bot_y, 0)
        else:
            return in_bounds_sector_area([self.center_x, self.center_y], self.radius, self.start_angle, self.end_angle, self.top_y, self.bot_y, 53.33)

    def get_offensive_dangers(self):
        d = 0
        for player in self.offenders:
            d += player.get_base_danger(self.defenders, self.center_x, self.center_y)
        return d

    def add_member(self, new_member):
        if new_member.Defensive == True:
            self.defenders.append(new_member)
            self.length += 1
        elif new_member.Defensive == False:
            self.offenders.append(new_member)
            self.length += 1

    def Get_Sideline(self):
        #Determines the value of sidelining
        if self.in_bounds == 1:            return False ##Do not consider if in bounds
        else:
            #print([self.center_x, self.center_y], self.mid_angle)
            if self.center_y < 10:
                midline = get_proj_x([self.center_x, self.center_y], self.mid_angle, 0)
                if math.dist([self.center_x, self.center_y], midline) > self.radius:
                    intersect = get_circle_intersection(self.radius,0, [self.center_x, self.center_y]) #This will give the point where the circle intersects the sideline
                    if self.mid_angle >= 90 and self.mid_angle < 270:
                        P3 = intersect[0]
                    else:
                        P3 = intersect[1]
                else:
                    P3 = midline
                return math.dist([self.center_x, self.center_y],P3)
            elif self.center_y > 43.33:
                midline = get_proj_x([self.center_x, self.center_y], self.mid_angle, 53.33)
                if math.dist([self.center_x, self.center_y], midline) > self.radius:
                    intersect = get_circle_intersection(self.radius, 53.33, [self.center_x, self.center_y])
                    if self.mid_angle >= 90 and self.mid_angle < 270:
                        P3 = intersect[0]
                    else:
                        P3 = intersect[1]
                else:
                    P3 = midline
                return math.dist([self.center_x, self.center_y],P3)
            else:
                return False
                
                        
                

    def Old_Get_Sideline(self):
        midangle = self.mid_angle
        if self.center_y == 0:
            if midangle < 180:
                return False
        if self.center_y == 53.33:
            if midangle > 180:
                return False
        if self.center_y <= 10:
            answer = Get_intersect_distance([self.center_x, self.center_y],midangle, 0, True)
            #print(answer,[self.center_x, self.center_y],midangle, 10) 
        elif self.center_y >= 43.33:
            answer = Get_intersect_distance([self.center_x, self.center_y],midangle, 53.33, True)
            #print(answer,[self.center_x, self.center_y],midangle, 53.33) 
        else:
            answer = False 
        return answer

    def older_calc_dangers(self, scaling_factor = 2):
        if len(self.defenders) == 0:
            return 0
        theta = 0.4
        inv_theta = 1-theta
        total_danger = theta
        candidates = []
        for member in self.defenders:
            m = self.radius
            n = math.dist([self.center_x,self.center_y],[member.x, member.y])
            #print(member.x,member.y, m,n)
            distance_variable = ((m-n)**scaling_factor)/(m**scaling_factor)
            midline = self.mid_angle
            answer = distance_variable*member.calc_leverage(self.center_x, self.center_y, midline)
            member.danger = answer
            candidates.append(answer)
        candidates.sort(reverse = True)
        for i in range(len(candidates)):
            weight = (1-inv_theta)/(2**(i+1))
            #weight = 1
            total_danger += (candidates[i]*weight)
        self.danger = total_danger
        return total_danger

    def calc_dangers(self, scaling_factor = 2):
        total_danger = 0
        for member in self.defenders:
            m = self.radius
            n = math.dist([self.center_x,self.center_y],[member.x, member.y])
            #print(member.x,member.y, m,n)
            answer = ((m-n)**scaling_factor)/(m**scaling_factor)
            #print(answer)
            if member.engaged == True:
                answer = answer = answer*(2/(2**len(member.blocked_by)))
            else:
                answer = answer*2
            #print(answer)
            member.danger = answer
            total_danger += answer
        if self.sidelining is not False:
            m = self.radius
            n = self.sidelining
            #print(m,n)
            answer = ((m-n)**scaling_factor)/(m**scaling_factor)
            total_danger += answer*1
        if total_danger > 1:
            total_danger = 1
        offender_danger = self.get_offensive_dangers()
        total_danger += offender_danger
        self.danger = total_danger
        return total_danger

    def max_calc_dangers(self, scaling_factor = 2):
        Max = 0
        for member in self.defenders:
            m = self.radius
            n = math.dist([self.center_x,self.center_y],[member.x, member.y])
            #print(member.x,member.y, m,n)
            distance_variable = ((m-n)**scaling_factor)/(m**scaling_factor)
            if distance_variable > Max:
                Max = distance_variable
        self.danger = Max
        return Max
            
        
            
        
    def original_calc_dangers(self, scaling_factor = 2):
        total_danger = 0
        for member in self.defenders:
            m = self.radius
            n = math.dist([self.center_x,self.center_y],[member.x, member.y])
            #print(member.x,member.y, m,n)
            answer = ((m-n)**scaling_factor)/(m**scaling_factor)
            #print(answer)
            if member.engaged == True:
                answer = answer*1
            else:
                answer = answer*2
            #print(answer)
            member.danger = answer
            total_danger += answer
        self.danger = total_danger
        return total_danger

                    
                

        
        

class circle():
    
    def __init__(self, center_x, center_y, radius, slices = 16, start_point = False, end_point = False, start_angle = False ):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.slices = slices
        if start_point == False:
            self.floor_x = center_x + radius
        else:
            self.floor_x = start_point
        if end_point == False:
            self.floor_y = center_y
        else:
            self.floor_y = end_point
        self.danger = False
        self.Slice = dict()
        interval = 360/slices
        if start_angle == False:
            angle = getAngle([center_x+radius,center_y],[center_x, center_y],[self.floor_x, self.floor_y])
        else:
            ###If given a start angle, recalc floor_x and floor_y
            angle = start_angle
            points = getPoint(angle, radius, center_x, center_y)
            self.floor_x = points[0]
            self.floor_y = points[1]
        self.start_angle = angle
        self.intervals = [0]
        for i in range(self.slices):
            bot_x, bot_y = getPoint(angle, radius, center_x, center_y)
            angle += interval
            top_x, top_y = getPoint(angle, radius, center_x, center_y)
            self.Slice[i] = slice(center_x, center_y, radius,top_x, top_y, bot_x, bot_y, angle-interval, angle)
            self.intervals.append(angle)

    def __repr__(self):
        'This one is pretty involved, it will give an overveiw of the entire circle, slice by slice'
        answer = ''
        for key in self.Slice:
            answer += self.Slice[key].__repr__()
        return answer

    def get_edgepoints(self):
        coords = []
        for key in self.Slice:
            curr = self.Slice[key]
            coords.append([curr.bot_x, curr.bot_y])
        return coords
        

    def print_slices(self):
        for key in self.Slice:
            print(self.Slice[key])

    def get_slice(self, key):
        return self.Slice[key]


    def get_slice_loc(self, angle):
        #####NEEDS TO BE UPDATED FOR DYNAMIC CIRCLE TWISTING (Update: Done below, all set here!)
        INT = 360/self.slices
        ####We can utilize self.start_angle, and just adjust accordingly.
        ####Subtracting gets us to base zero
        #angle = angle - self.start_angle
        answer = int(angle//INT)
        #print(answer)
        if answer < 0:
            answer += self.slices
        return answer

    def in_slice(self, x , y):
        if math.dist([self.center_x,self.center_y],[x,y]) > self.radius:
            #print('out of range')
            return 'False'
        angle = getAngle([self.floor_x,self.floor_y],[self.center_x,self.center_y],[x,y])
        #print(angle)
        loc = self.get_slice_loc(angle)
        #print(loc)
        return loc

    def in_slices(self, x, y):
        if math.dist([self.center_x,self.center_y],[x,y]) > self.radius:
            #print('out of range')
            return []
        answers = []
        start_angle = 0
        end_angle = 360/self.slices
        interval = 360/self.slices
        for i in range(self.slices):
            #print(0,0,start_angle,end_angle,x,y)
            if point_intersects(self.center_x,self.center_y,start_angle,end_angle,x,y):
                answers.append(i)
            start_angle += interval
            end_angle += interval
        return answers

    def add_player(self, x, y, player):
        loc = self.in_slice(x,y)
        if loc == 'False':
            return False
        else:
            self.Slice[loc].add_member(player)
            return True

    def calc_danger(self):
        self.danger = 0
        for key in self.Slice:
            self.danger += self.Slice[key].danger
        return self.danger        
        

    def print_dangers(self):
        for key in self.Slice:
            print(key, self.Slice[key].danger)

    def get_player_coords(self):
        offensive = []
        defensive = []
        for key in self.Slice:
            curr = self.Slice[key]
            for player in curr.offenders:
                offensive.append([player.x, player.y])
            for player in curr.defenders:
                defensive.append([player.x, player.y])
        return [offensive,defensive]

    def plot_circle(self, alpha = 1, show_coords = False, show_d= False, print_desc = False):
        plt.plot(self.center_x,self.center_y, color = 'green', marker = 'o')
        #draw circle
        angles = linspace(0 * pi, 2 * pi, 100 )
        r = self.radius
        xs = r * cos(angles) + self.center_x
        ys = r * sin(angles) + self.center_y
        plt.plot(xs, ys, color = 'black')
        #draw diameter
        points = self.get_edgepoints()
        for i in range(len(points)):
            point = points[i]
            plt.plot(point[0], point[1], marker = 'o', color = 'black')
        for i in range(len(points)):
            point = points[i]
            mid = self.slices//2
            if i < mid:
                opp = points[i+mid]
                x_lst = [point[0],opp[0]]
                y_lst = [point[1],opp[1]]
                opp_point = points[i + mid]
                plt.plot(x_lst,y_lst, linestyle = '-',color = 'black')
                #plt.gca().annotate('', xy=(, -.25), xycoords='data')
        if show_coords == True:
            plt.gca().annotate('RB ({}, {})'.format(self.center_x,self.center_y), xy=(self.center_x + 0.1, self.center_y + 0.1), xycoords='data', fontsize=10)
        players = self.get_player_coords()
        offensive_players = players[0]
        defensive_players = players[1]
        for player in offensive_players:
            #print('o,',player)
            plt.plot(player[0],player[1], color = 'blue', marker = 'o')
            if show_coords == True:
                plt.gca().annotate('({}, {})'.format(player[0],player[1]), xy=(player[0]-0.5,player[1]+0.5), xycoords='data', fontsize=5)
        for player in defensive_players:
            plt.plot(player[0],player[1], color = 'red', marker = 'x')
            if show_coords == True:
                plt.gca().annotate('({}, {})'.format(player[0],player[1]), xy=(player[0]-0.5,player[1]+0.5), xycoords='data', fontsize=5)

        #draw arc
        start_arc = self.start_angle
        interval = 360/self.slices
        if print_desc == True:
            print('arcs for start at {}'.format(self.start_angle))
        norm = mpl.colors.Normalize(vmin = 0, vmax =1)
        n = 1001
        colors = mpl.cm.RdYlBu(np.linspace(1,0,n))
        for i in range(self.slices):
            c = colors[random.randint(0,3)]
            #print(start_arc, start_arc + interval, c)
            arc_angles = linspace(math.radians(start_arc), math.radians(start_arc + interval))
            arc_xs = r * cos(arc_angles) + self.center_x
            arc_ys = r * sin(arc_angles) + self.center_y
            d = self.Slice[i].danger
            index = int(myround(d,0.002)*1000)
            #print(index)
            plt.plot(arc_xs, arc_ys, c = colors[index], lw = 3)
            if show_d == True:
                plt.gca().annotate('D = {}'.format(round(d,3)), xy= getPoint(start_arc + interval/2, self.radius, self.center_x, self.center_y),
                                                                    xycoords='data', fontsize=20)
            start_arc += interval
        plt.xlim(-(alpha*r)+self.center_x, alpha*r+self.center_x)
        plt.ylim(-(alpha*r)+self.center_y, alpha*r+self.center_y)
        plt.gca().set_aspect('equal')
        #plt.xticks([i for i in range(-10,11)])
        #plt.yticks([i for i in range(-10,11)])
        plt.grid()
        plt.show()
        
        
            
            
            
                 
 

def populate_random(Range = 22):
    teams = ['Indianapolis', 'Baltimore']
    positions = ['OL','DL']
    circ = circle(0,0,10,16)
    import random
    for i in range(Range):
        x = random.randint(0,1000)/100
        y = random.randint(0,1000)/100
        neg_x = random.randint(0,1)
        neg_y = random.randint(0,1)
        team = random.randint(0,1)
        if neg_x:
            x = x * -1
        if neg_y:
            y = y * -1
        #print(x,y)
        if team == 0:
            p = Offensive_Player('Walter Payton{}'.format(random.randint(1000,9999)),
                                 random.randint(60,80),random.randint(180,375),positions[team],x,y, teams[team],0)
        elif team == 1:
            p = Defensive_Player('Lawrence Taylor{}'.format(random.randint(1000,9999)),
                                 random.randint(60,80),random.randint(180,375),positions[team],x,y, teams[team],0)
        circ.add_player(float(x), float(y), p)
    for s in circ.Slice:
        for player in circ.Slice[s].offenders:
           player.updated_find_defender(defenders = circ.Slice[s].defenders,mid_angle = player.orientation, cone_range = 30,
                                         rb_x = center_x, rb_y = center_y)
        circ.Slice[s].calc_dangers()
    return circ

def populate_determined_coords(offensive = [], defensive = [], teams =
                        ['Indianapolis', 'Baltimore'], positions = ['OL','DL'],  startx = 0, starty = 0, start_angle = False):
    if start_angle == False:
        circ = circle(0,0,10,16, startx, starty)
    else:
        circ = circle(0,0,10,16, start_angle = start_angle)
    import random
    for player in offensive:
        x = player[0]
        y = player[1]
        team = 0
        p = Offensive_Player('Walter Payton{}'.format(random.randint(1000,9999)),
                                 random.randint(60,80),random.randint(180,375),positions[team],x,y, teams[team],0)
        circ.add_player(float(x), float(y), p)
    for player in defensive:
        x = player[0]
        y = player[1]
        team = 1
        p = Defensive_Player('Lawrence Taylor{}'.format(random.randint(1000,9999)),
                             random.randint(60,80),random.randint(180,375),positions[team],x,y, teams[team],0)
        circ.add_player(float(x), float(y), p)
    for s in circ.Slice:
        for player in circ.Slice[s].offenders:
            player.updated_find_defender(defenders = circ.Slice[s].defenders,mid_angle = player.orientation, cone_range = 30,
                                         rb_x = 0, rb_y = 0)
        circ.Slice[s].calc_dangers()
    circ.calc_danger()
    return circ

class NotACircle(Exception):

    def __init__(self, ID = False):
        if ID == False:
            string = 'Not all items are circle objects'
        else:
            string = 'Item at index {} is not a circle object'.format(ID)
        super().__init__(string)

class InequalCircle(Exception):

    def __init__(self, ID = False):
        if ID == False:
            string = 'Not all candidate circles have identical origin and radius'
        else:
            string = 'Item at index {} has a different origin and radius than item at index 0'.format(ID)
        super().__init__(string)


def normalize_angle(angle):
    'Put all angles on a scale of 0 to 360 degrees'
    while angle > 360:
        angle -=360
    while angle < 0:
        angle += 360
    return angle

def dist_to_angle(a1, a2):
    dist = a2-a1
    if dist < 0:
        dist = normalize_angle(dist)
    return dist

def in_range(border_start, border_end, check_start, check_end):
    bstart = normalize_angle(border_start)
    bend = normalize_angle(border_end)
    cstart = normalize_angle(check_start)
    cend = normalize_angle(check_end)
    border_width = dist_to_angle(bstart,bend)
    check_width = dist_to_angle(cstart,cend)
    tr = dist_to_angle(bstart, cstart)
    #print('BORDER: {} to {}: SECTION: {} to {}: BW = {}, CW = {}, TR = {}'.format(bstart, bend, cstart, cend, border_width, check_width,tr))
    if tr + check_width <= border_width:
        #If the distance from the border_start to check_start, plus the width of our check subsector is less than
        #the width of the entire border sector, than we can reach the edge of check while staying in our big sector.
        return True                                                                             
    return False


def intersects_range(border_start, border_end, check_start, check_end):
    if in_range(border_start, border_end, check_start, check_end):
        return True
    bstart = normalize_angle(border_start)
    bend = normalize_angle(border_end)
    cstart = normalize_angle(check_start)
    cend = normalize_angle(check_end)
    check_width = dist_to_angle(cstart,cend)
    first_check = dist_to_angle(cstart, bstart)
    second_check = dist_to_angle(cstart, bend)
    #print('BORDER: {} to {}: SECTION: {} to {} , CW = {}, FC = {}, SC = {}'.format(bstart, bend, cstart, cend, check_width, first_check, second_check))
    for distance in [first_check, second_check]:
        if check_width >= distance:
            return True
            #If the distance from the border_start to check_start, plus the width of our check subsector is less than
            #the width of the entire border sector, than we can reach the edge of check while staying in our big sector.                                                                            
    return False
    
def point_intersects(center_x, center_y, border_start, border_end, check_x, check_y, arclen = (math.pi/6)):
    radius = math.dist([center_x, center_y],[check_x,check_y])
    ca1 = getAngle([center_x+10, center_y],[center_x, center_y],[check_x,check_y])
    #ca2 = getAngle([check_x, check_y],[center_x, center_y],[center_x+10, center_y])
    angle = ca1
    radians = arclen/radius
    split = math.degrees(radians)
    check_start = angle - (split/2)
    check_end = angle + (split/2)
    return intersects_range(border_start, border_end, check_start, check_end)
    
    
                     
class mini_slice():

    def __init__(self, start_angle, end_angle, circles):
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.circles = circles
        self.candidates = []
        self.danger = self.calc_minislice_danger()

    def calc_minislice_danger(self):
        #print('minislice {},{}'.format(self.start_angle, self.end_angle))
        'the danger is the minislice is the average dangers of all circles that make up it\'s area'
        danger = 0
        count = 0
        for circle in self.circles:
            curr_c = circle.Slice
            for key in curr_c:
                curr_s = curr_c[key]
                if in_range(curr_s.start_angle, curr_s.end_angle, self.start_angle, self.end_angle):
                    #print('{},{} is in range {},{}'.format(self.start_angle, self.end_angle,
                                                           #curr_s.start_angle, curr_s.end_angle))
                    count += 1
                    danger += curr_s.danger
                    self.candidates.append(curr_s.danger)
                    #print('count = {}, danger = {}'.format(count, danger))
        return (danger/count)
        

class big_circle():

    def __init__(self, members, slices = False):
        self.members = []
        self.rotations = 0
        self.center_x = members[0].center_x
        self.center_y = members[0].center_y
        self.radius = members[0].radius
        i = -1
        for member in members:
            i += 1
            if type(member) == circle:
                if member.center_x == self.center_x and member.center_y == self.center_y and member.radius == self.radius:
                    self.members.append(member)
                    self.rotations += 1
                else:
                    raise InequalCircle(i)
            else:
                raise NotACircle(i)
        if slices == False:
            slices = members[0].slices * 4
            print('No Slices Given')
        self.slices = slices
        self.Slice = dict()
        self.initialize_mini_slices()
        self.get_danger()
        self.edgepoints = self.get_edgepoints()

    def get_edgepoints(self):
        start = self.Slice[0].start_angle
        answer = []
        interval = 360/self.slices
        for i in range(self.slices):
            answer.append(getPoint(start + (i*interval), self.radius, self.center_x, self.center_y))
        return answer
        
                
    def initialize_mini_slices(self):
        interval = 360/self.slices
        angle = 0
        for i in range(self.slices):
            self.Slice[i] = mini_slice(angle, angle + interval, self.members)
            angle += interval

    def print_circle(self):
        for s in self.Slice:
            d = self.Slice[s].danger
            start = self.Slice[s].start_angle
            end = self.Slice[s].end_angle
            cand = self.Slice[s].candidates
            print('Slice {} from {} to {} has candidates {} and danger {}'.format(s,start,end,cand,d))

    def get_danger(self):
        danger = 0
        for item in self.Slice:
            danger += self.Slice[item].danger
        self.danger = danger/self.slices

    def get_player_coords(self):
        return self.members[0].get_player_coords()

    def plot_circle(self, alpha = 1, show_d = False, show_line = True, show_coords = False, show = True):
        plt.clf()
        img = plt.imread("Field.jpg")
        plt.imshow(img, extent = [0, 120, 0 ,53.3])
        plt.plot(self.center_x,self.center_y, color = 'brown', marker = 'o')
        #draw circle
        angles = linspace(0 * pi, 2 * pi, 100 )
        r = self.radius
        xs = r * cos(angles) + self.center_x
        ys = r * sin(angles) + self.center_y
        plt.plot(xs, ys, color = 'black')
        #draw diameter
        points = self.edgepoints
        if show_line == True:
            for i in range(len(points)):
                point = points[i]
                mid = self.slices//2
                if i < mid:
                    opp = points[i+mid]
                    x_lst = [point[0],opp[0]]
                    y_lst = [point[1],opp[1]]
                    opp_point = points[i + mid]
                    plt.plot(x_lst,y_lst, linestyle = '--',color = 'black', lw = 1)
        players = self.get_player_coords()
        offensive_players = players[0]
        defensive_players = players[1]
        for player in offensive_players:
            #print('o,',player)
            plt.plot(player[0],player[1], color = 'blue', marker = 'o')
            if show_coords == True:
                plt.gca().annotate('({}, {})'.format(player[0],player[1]), xy=(player[0]-0.5,player[1]+0.5), xycoords='data', fontsize=5)
        for player in defensive_players:
            plt.plot(player[0],player[1], color = 'red', marker = 'x')
            if show_coords == True:
                plt.gca().annotate('({}, {})'.format(player[0],player[1]), xy=(player[0]-0.5,player[1]+0.5), xycoords='data', fontsize=5)
        #draw arc
        start_arc = 0.0
        interval = 360/self.slices
        norm = mpl.colors.Normalize(vmin = 0, vmax =1)
        n = 1001
        colors = mpl.cm.gist_heat(np.linspace(1,0,n))
        for i in range(self.slices):
            c = colors[random.randint(0,3)]
            #print(start_arc, start_arc + interval, c)
            arc_angles = linspace(math.radians(start_arc), math.radians(start_arc + interval))
            arc_xs = r * cos(arc_angles) + self.center_x
            arc_ys = r * sin(arc_angles) + self.center_y
            d = self.Slice[i].danger
            index = int(myround(d,0.002)*1000)
            if index >=1000:
                index = 999
            #print(index)
            plt.plot(arc_xs, arc_ys, c = colors[index], lw = 3)
            if show_d == True:
                plt.gca().annotate('D = {}'.format(round(d,3)), xy= getPoint(start_arc + interval/2, self.radius, self.center_x, self.center_y),
                                                               xycoords='data', fontsize=20)
            start_arc += interval
        plt.xlim(-(alpha*r)+self.center_x, alpha*r+self.center_x)
        plt.ylim(-(alpha*r)+self.center_y, alpha*r+self.center_y)
        #plt.xlim(0,120)
        #plt.ylim(0,53.3)
        #Incorporate these into an animation ^
        plt.gca().set_aspect('equal')
        plt.title('{} Slices and {} Rotations, Danger of {}'.format(int(self.slices/self.rotations), self.rotations, self.danger))
        if show == True:
            plt.show()
        return plt




                


def populate_determined_players(offensive = [], defensive = [], radius = 10, slices = 16,
                                startx = 0, starty = 0, start_angle = False, center_x = 0, center_y = 0):
    if start_angle == False:
        circ = circle(center_x,center_y,radius, slices, startx, starty)
    else:
        circ = circle(center_x,center_y,radius, slices, start_angle = start_angle)
    import random
    for player in offensive:
        x = player.x
        y = player.y
        circ.add_player(float(x), float(y), player)
    for player in defensive:
        x = player.x
        y = player.y
        circ.add_player(float(x), float(y), player)
    for s in circ.Slice:
        for player in circ.Slice[s].offenders:
            player.updated_find_defender(defenders = circ.Slice[s].defenders,mid_angle = player.orientation, cone_range = 30,
                                         rb_x = center_x, rb_y = center_y)
        circ.Slice[s].calc_dangers()
    circ.calc_danger()
    return circ

def make_big_circ(offensive = [], defensive = [], radius = 10, startx = 0, starty = 0,
                  slices = 16, rotations = 4,start_angle = 0, center_x = 0, center_y = 0):
    interval = 360/(slices*rotations)
    members = []
    for i in range(rotations):
        curr = populate_determined_players(offensive, defensive, radius, slices, startx,
                                           starty, start_angle + (interval*i), center_x = center_x, center_y = center_y)
        members.append(curr)
    god = big_circle(members, slices*rotations)
    return god
        

def get_play(df, gameID, playID):
    return df.loc[(df['gameId'] == gameID) & (df['playId'] == playID)]

class play_circle():

    def __init__(self, play, radius = 10, slices = 16, rotations = 4):
        self.gameId = list(play.gameId)[0]
        self.playId = list(play.playId)[0]
        self.play = play
        self.frameIds = list(set(self.play.frameId))
        self.radius = radius
        self.slices = slices
        self.rotations = rotations
        self.frames = self.get_play_items()
        self.circles = self.make_members()
        self.dangers = self.get_dangers()
        self.score = (self.dangers[-1]-self.dangers[0])/len(self.dangers)

    def get_play_items(self):
        frames = self.frameIds
        oracle = dict()
        for frame in frames:
            curr = self.play.loc[(self.play['frameId'] == frame)]
            Offensive = []
            Defensive = []
            for index in curr.index:
                player = curr.loc()[index]
                if player['Ball Carrier'] == 0:
                    orientation = orientation_translation(player.o)
                    ID = player.nflId
                    team = player.club
                    x = player.x
                    y = player.y
                    name = player.displayName
                    if player['Offensive'] == 1:
                        ###Offensive Player
                        p = Offensive_Player(ID, 0, 0, 'HB', x, y, team, orientation, name)
                        Offensive.append(p)
                    elif player['Offensive'] == 0:
                        p = Defensive_Player(ID, 0, 0, 'LB', x, y, team, orientation, name)
                        Defensive.append(p)
                elif player['Ball Carrier'] == 1:
                    BC_Coords = [player.x, player.y]
            oracle[frame] = [BC_Coords, Offensive, Defensive]
        return oracle

    def make_members(self):
        answer = []
        frames = self.frames
        for frame in frames:
            o = frames[frame][1]
            d = frames[frame][2]
            center_coords = frames[frame][0]
            curr = make_big_circ(offensive = o, defensive = d, radius = self.radius, startx = 0, starty = 0,
                      slices = self.slices, rotations = self.rotations,start_angle = 0, center_x = center_coords[0], center_y = center_coords[1])
            answer.append(curr)
        return answer

    def get_dangers(self):
        answer = []
        for frame in self.circles:
            answer.append(frame.danger)
        return answer

    def scatter_plot(self):
        plt.clf()
        x = self.frameIds
        y = self.dangers
        plt.scatter(x,y)
        plt.title('Danger as play goes on, game {} play {}'.format(self.gameId, self.playId))
        plt.xlabel('frame')
        plt.ylabel('danger')
        plt.show()
        plt.clf()

    def animation_update(self, frame_number):
        BigCirc = self.circles[frame_number-1]
        self.ax.clear()
        img = plt.imread("Field.jpg")
        self.ax.imshow(img, extent = [0, 120, 0 ,53.3])
        self.ax.plot(BigCirc.center_x,BigCirc.center_y, color = 'darkgoldenrod', marker = 'o')
        #draw circle
        angles = linspace(0 * pi, 2 * pi, 100 )
        r = BigCirc.radius
        xs = r * cos(angles) + BigCirc.center_x
        ys = r * sin(angles) + BigCirc.center_y
        self.ax.plot(xs, ys, color = 'black')
        #draw diameter
        points = BigCirc.edgepoints
        if self.show_line == True:
            for i in range(len(points)):
                point = points[i]
                mid = BigCirc.slices//2
                if i < mid:
                    opp = points[i+mid]
                    x_lst = [point[0],opp[0]]
                    y_lst = [point[1],opp[1]]
                    opp_point = points[i + mid]
                    self.ax.plot(x_lst,y_lst, linestyle = '--',color = 'black', lw = 1)
        players = BigCirc.get_player_coords()
        offensive_players = players[0]
        defensive_players = players[1]
        for player in offensive_players:
            #print('o,',player)
            self.ax.plot(player[0],player[1], color = 'blue', marker = 'o')
            if self.show_coords == True:
                self.ax.gca().annotate('({}, {})'.format(player[0],player[1]), xy=(player[0]-0.5,player[1]+0.5), xycoords='data', fontsize=5)
        for player in defensive_players:
            self.ax.plot(player[0],player[1], color = 'red', marker = 'x')
            if self.show_coords == True:
                self.ax.gca().annotate('({}, {})'.format(player[0],player[1]), xy=(player[0]-0.5,player[1]+0.5), xycoords='data', fontsize=5)
        #draw arc
        start_arc = 0.0
        interval = 360/BigCirc.slices
        norm = mpl.colors.Normalize(vmin = 0, vmax =1)
        n = 1001
        colors = mpl.cm.gist_heat(np.linspace(1,0,n))
        for i in range(BigCirc.slices):
            c = colors[random.randint(0,3)]
            #print(start_arc, start_arc + interval, c)
            arc_angles = linspace(math.radians(start_arc), math.radians(start_arc + interval))
            arc_xs = r * cos(arc_angles) + BigCirc.center_x
            arc_ys = r * sin(arc_angles) + BigCirc.center_y
            d = BigCirc.Slice[i].danger
            index = int(myround(d,0.002)*1000)
            if index >=1000:
                index = 999
            if index < 0:
                index = 0
            #print(index)
            self.ax.plot(arc_xs, arc_ys, c = colors[index], lw = 3)
            if self.show_d == True:
                self.ax.gca().annotate('D = {}'.format(round(d,3)), xy= getPoint(start_arc + interval/2, BigCirc.radius, BigCirc.center_x, BigCirc.center_y),
                                                               xycoords='data', fontsize=10)
            start_arc += interval
        self.ax.set_xlim(-(self.alpha*r)+BigCirc.center_x, self.alpha*r+BigCirc.center_x)
        self.ax.set_ylim(-(self.alpha*r)+BigCirc.center_y, self.alpha*r+BigCirc.center_y)
        #self.ax.xlim(0,120)
        #self.ax.ylim(0,53.3)
        #Incorporate these into an animation ^
        #self.ax.gca().set_aspect('equal')
        self.ax.set_title('game {} play {} {} Slices and {} Rotations, Danger of {}'.format(self.gameId, self.playId, int(BigCirc.slices/BigCirc.rotations), BigCirc.rotations, round(BigCirc.danger,5)))
        if self.save_frames == True:
            if self.floc == False:
                plt.savefig('New_Slides/{}_{}_Frame{}   {}x{}.jpg'.format(self.gameId, self.playId, frame_number, int(BigCirc.slices/BigCirc.rotations), BigCirc.rotations ))
            else:
                plt.savefig(self.floc + ' {}_{}_Frame{}   {}x{}.jpg'.format(self.gameId, self.playId, frame_number, int(BigCirc.slices/BigCirc.rotations), BigCirc.rotations ))
        #self.ax.legend()
        

    def plot_play(self, alpha = 2, show_d = False, show_line = False, show_coords = False, show = True, saveframes = False, savegif = False, floc = False, gloc = False):
        self.alpha = alpha
        self.show_d = show_d
        self.show_line = show_line
        self.show_coords = show_coords
        self.save_frames = saveframes
        self.floc = floc
        fig, self.ax = plt.subplots()
        ani = animation.FuncAnimation(fig, self.animation_update, frames = self.frameIds, repeat= True, interval = 50)
        if savegif == True:
            writer = animation.PillowWriter(fps = 10, metadata=dict(artist='Me'), bitrate=1800)
            if gloc == False:
                ani.save('New_Gifs/{}_{}   {}x{}.gif'.format(self.gameId, self.playId, int(self.slices/self.rotations), self.rotations), writer = writer)
            else:
                ani.save(gloc + ' {}_{}   {}x{}.gif'.format(self.gameId, self.playId, int(self.slices/self.rotations), self.rotations), writer = writer)
        if show == True:
            plt.show()
    

        
if __name__ == '__main__':
    '''
    circ = circle(0,1,10, slices = 10, start_angle = 18)
    for s in circ.Slice:
        circ.Slice[s].calc_dangers()
    week_1 = pd.read_csv('Data/Updated/Updated_tracking_week_1.csv')
    play = get_play(week_1, 2022090800, 56)
    first_play = play_circle(play, slices = 8, rotations = 6)
    first_play.plot_play(alpha = 2, show_line = False, savegif = True, saveframes = True)
    x = input('break')      
    test = Defensive_Player(432, 0, 0, 'H', 3,6,'None', 0, 'Lebron')
    opponent1 = Offensive_Player(421, 0, 0, 'None', 3, 7, 'Bills', 0, 'Greg')
    opponent2 = Offensive_Player(421, 0, 0, 'None', 8, 5, 'Bills', 0, 'Greg')
    test.blocked_by = [opponent2]
    x = test.calc_leverage(0,0, 45)
    inputs = [[2,1],[0.5,2],[-2,3],[-2,1],
              [-2,-1],[-1,-2],[1,-3],[2,-1]]
    f = -45
    for i in range(len(inputs)):
        if i%2 == 0:
            f += 90
        print(inputs[i], f,getPerpIntersect(0,0,inputs[i][0],inputs[i][1],f))
    
    
    
    '''  
    O = [[4,5],[4,3],[4,1],[4,-1],[4,-3],[20,5]]
    D = [[5,6],[5,4],[5,1],[5,-2],[5,-4],[7,-1],[7,1],[7,3]]
    off = []
    Def = []
    for coords in O:
        p = Offensive_Player('Walter Payton{}'.format(random.randint(1000,9999)),
                                     random.randint(60,80),random.randint(180,375),'HB',coords[0],coords[1], 'CHI',0)
        off.append(p)
    for coords in D:
        p = Defensive_Player('Lawrence Taylor{}'.format(random.randint(1000,9999)),
                                 random.randint(60,80),random.randint(180,375),'LB',coords[0],coords[1], 'NYG',0)
        Def.append(p)    
    circ = populate_determined_coords(O,D)
    circ2 = populate_determined_coords(O,D, start_angle = 5.62499046342678)
    circ3 = populate_determined_coords(O,D, start_angle = 5.62499046342678*2)
    circ4 = populate_determined_coords(O,D, start_angle = 5.62499046342678*3)
    lst = [circ, circ2, circ3, circ4]
    print(in_range(19,20,355,375) == False)
    print(in_range(55,110,60,85) == True)
    print(in_range(345,360,350,355) == True)
    print(in_range(0,30,0,22.5) == True)
    print(in_range(350,10,5,8) == True)
    
    test_circles = []
    dangers = [[0,2.5,8.5,7],
               [1,2,7.5,8],
               [2,0.5,6,9.5],
               [0,5,8,3.5]]
    for i in range(4):
        test_circle = circle(0,0,10,4,start_angle = 0+(360/16)*i)
        curr = dangers[i]
        for j in range(len(curr)):
            test_circle.Slice[j].danger = dangers[i][j]
        test_circles.append(test_circle)
    god = big_circle(test_circles)
    god.print_circle()

    fcirc = populate_determined_players(off,Def)
    final = make_big_circ(off, Def, center_x = 1, center_y = 1, slices = 16, rotations = 4)
    '''

    colors = ['0xff0000', '0xf70d03', '0xf01a05', '0xe82608', '0xe0330a',
              '0xd9400d', '0xd14c0f', '0xc95912', '0xc26614', '0xba7317',
              '0xb2801a', '0xab8c1c', '0xa3991f', '0x9ca621', '0x94b224',
              '0x8cbf26', '0x85cc29', '0x7dd92b', '0x75e62e', '0x6ef230', '0x66ff33']

    def get_color(number):
        x = myround(100*number, len(colors))
        return x

        



    print(circ)
    circ.plot_circle()
    print(circ4)
    '''
