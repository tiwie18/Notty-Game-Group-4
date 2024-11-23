import math

import pygame.time


class AnimationCurve:
    '''
    Input a time(t) to it and get the value
    '''
    def __init__(self):
        pass

    def evaluate(self, t):
        '''
        :param t: The time
        :return: The value
        '''
        return 1


class Animation2DCurve(AnimationCurve):
    """
    The animation curve that used to control 2D tuples
    """
    def __init__(self, curve_x, curve_y):
        super().__init__()
        self.curve_x = curve_x
        self.curve_y = curve_y

    def evaluate(self, t):
        return self.curve_x.evaluate(t), self.curve_y.evaluate(t)


class AnimationTask:
    def __init__(self, duration, loop=True):
        self.duration = duration
        self.loop = loop
        self.playtime = 0
        self.propertyDict = {}

    @property
    def finished(self):
        return self.playtime >= self.duration

    def reset(self):
        self.playtime = 0

    def bind_property(self, propertyName, curve):
        '''
        :param propertyName: The property you want the animation curve to control
        :param curve: The animation curve
        :return: None
        '''
        self.propertyDict[propertyName] = curve

    def evaluate(self, gameObject, t):
        if gameObject is None:
            print(f"Warning: Animation task {self.__repr__()} has not bound any game object, ignored.")
            return
        for (propertyName, curve) in self.propertyDict.items():
            setattr(gameObject, propertyName, curve.evaluate(t))

    def update(self, gameObject, dt):
        self.playtime += dt
        if self.playtime >= self.duration:
            if not self.loop:
                self.playtime = self.duration
            else:  # loop
                while self.playtime >= self.duration:
                    self.playtime -= self.duration

        self.evaluate(gameObject, self.playtime)


class AnimationSequenceTask(AnimationTask):
    def __init__(self, loop=True):
        super().__init__(duration=0, loop=loop)
        self.duration = 0
        self._sub_task_list = []
        self._sub_task_start_time_list = []

    def add_sub_task(self, sub_animation_task):
        self._sub_task_list.append(sub_animation_task)
        self._sub_task_start_time_list.append(self.duration)
        self.duration = sum([sub_task.duration for sub_task in self._sub_task_list])

    def evaluate(self, gameObject, t):
        if gameObject is None:
            print(f"Warning: Animation task {self.__repr__()} has not bound any game object, ignored.")
            return
        for i in range(len(self._sub_task_list)):
            if t <= 0:
                self._sub_task_list[0].evaluate(gameObject, 0)
            elif t > self.duration:
                self._sub_task_list[-1].evaluate(gameObject, t - self._sub_task_start_time_list[-1])
            elif i < len(self._sub_task_list) - 1 and self._sub_task_start_time_list[i + 1] <= t:
                continue
            else:
                sub_task = self._sub_task_list[i]
                sub_time = t - self._sub_task_start_time_list[i]
                sub_task.evaluate(gameObject, sub_time)
                break


class Animation:
    """
    The animation system that actually runs the animation tasks
    """
    def __init__(self):
        print("Animation initialized")
        self.gameObjectAnimationTaskDict = {}
        self.clock = pygame.time.Clock()

    def register_animation_task(self, gameObject, animation_task):
        self.gameObjectAnimationTaskDict[gameObject] = animation_task

    def play_animation(self, gameObject, animation_task):
        self.register_animation_task(gameObject,animation_task)

    def update(self):
        dt = self.clock.tick(60)/1000
        for (gameObject, animationTask) in self.gameObjectAnimationTaskDict.items():
            if animationTask is not None:
                if animationTask.finished:
                    self.gameObjectAnimationTaskDict[gameObject] = None
                    continue
                else:
                    animationTask.update(gameObject, dt)


class ConstantCurve(AnimationCurve):
    """
    return a constant value when evaluated
    """
    def __init__(self, value):
        super().__init__()
        self.constant_value = value

    def evaluate(self, t):
        return self.constant_value


class SineCurve(AnimationCurve):
    """
    return a sine curve when evaluated
    """
    def __init__(self, a=1, omiga=1, phi=0, c=0):
        super().__init__()
        self.a = a
        self.omiga = omiga
        self.phi = phi
        self.c = c

    def evaluate(self, t):
        return self.a * math.sin(self.omiga * t + self.phi) + self.c


class PingPongCurve(AnimationCurve):
    """
    constantly and smoothly move between start and end
    """
    def __init__(self, start, end, duration):
        super().__init__()
        self.start = start
        self.end = end
        self.duration = duration

    def evaluate(self, t):
        length = self.end - self.start
        x = t / self.duration
        return 0.5 * (1 - math.cos(math.pi * x)) * length + self.start


class MoveToCurve(AnimationCurve):
    """
    linear movement between start and end
    """
    def __init__(self, start, end, duration):
        super().__init__()
        self.start = start
        self.end = end
        self.duration = duration

    def evaluate(self, t):
        rate = t/self.duration
        return (1 - rate) * self.start + rate * self.end


class SmoothDampCurve(AnimationCurve):
    def __init__(self, start, end, duration):
        super().__init__()
        self.start = start
        self.end = end
        self.duration = duration
        self._v = 0
        self._t = 0
        self._current = start
        self._max_speed = 2 * (end - start)/duration

    def evaluate(self, t):
        target = self.end
        smoothTime = max(self.duration * 0.9999, 0.0001)
        dt = t - self._t
        self._t = t
        num1 = 2 / smoothTime
        num2 = num1 * dt
        num3 = 1/(1 + num2 + 0.48 * num2 * num2 + 0.235 * num2 * num2 * num2)
        num4 = self._current - target
        num5 = target
        num6 = max(min(num4,self._max_speed), -self._max_speed)
        target = self._current - num6
        num7 = (self._v + num1 * num6) * dt
        self._v = (self._v - num1 * num7) * num3
        num8 = target + (num6 + num7) * num3
        if (num5 - self._current > 0) == (num8 > num5):
            num8 = num5
            self._v = (num8 - num5)/dt
        self._current = num8
        return num8


class EaseInOutCurve(AnimationCurve):
    """
    move smoothly from start to the end in given duration
    """
    def __init__(self, start, end, duration):
        super().__init__()
        self.start = start
        self.end = end
        self.duration = duration

    def evaluate(self, t):
        rate = t/self.duration
        _2pi = math.pi * 2
        u = _2pi * rate
        return (u - math.sin(u))/_2pi * (self.end - self.start) + self.start


class HopCurve(AnimationCurve):
    """
    A parabola
    """
    def __init__(self, pos, height, duration):
        super().__init__()
        self.pos = pos
        self.height = height
        self.duration = duration

    def evaluate(self, t):
        x = t/self.duration
        return (1-(2 * x - 1)**2) * self.height + self.pos


def sine_scale_2d(property_name):
    """
    create an animation task that do a simple sine movement
    :param property_name: property name to control
    :return: animation task
    """
    animation_task = AnimationTask(math.pi * 2, loop=True)
    sine2dAnimationCurve = Animation2DCurve(SineCurve(c=3), SineCurve(c=3))
    animation_task.bind_property(property_name, sine2dAnimationCurve)
    return animation_task


def ease_in_out_2d(property_name, start_pos, end_pos, duration=1):
    animation_task = AnimationTask(duration=duration, loop=False)
    curve_x = EaseInOutCurve(start_pos[0], end_pos[0], duration)
    curve_y = EaseInOutCurve(start_pos[1], end_pos[1], duration)
    _2d_curve = Animation2DCurve(curve_x, curve_y)
    animation_task.bind_property(property_name, _2d_curve)
    return animation_task


def ping_pong(property_name, start_pos, end_pos, duration):
    animation_task = AnimationTask(duration=duration, loop=True)
    curve_x = PingPongCurve(start_pos[0], end_pos[0], duration * 0.5)
    curve_y = PingPongCurve(start_pos[1], end_pos[1], duration * 0.5)
    _2d_curve = Animation2DCurve(curve_x, curve_y)
    animation_task.bind_property(property_name, _2d_curve)
    return animation_task


def hop_2d(property_name, start_pos, offset, duration=1):
    animation_task = AnimationTask(duration=duration, loop=False)
    curve_x = HopCurve(start_pos[0], offset[0], duration)
    curve_y = HopCurve(start_pos[1], offset[1], duration)
    _2d_curve = Animation2DCurve(curve_x, curve_y)
    animation_task.bind_property(property_name, _2d_curve)
    return animation_task


def constant_2d(property_name, constant2d, duration=1):
    animation_task = AnimationTask(duration=duration, loop=False)
    curve_x = ConstantCurve(constant2d[0])
    curve_y = ConstantCurve(constant2d[1])
    _2d_curve = Animation2DCurve(curve_x, curve_y)
    animation_task.bind_property(property_name, _2d_curve)
    return animation_task


def move_to(property_name, start_pos, end_pos, duration = 1):
    animation_task = AnimationTask(duration=duration, loop=False)
    move_to_curve_x = MoveToCurve(start_pos[0], end_pos[0], duration)
    move_to_curve_y = MoveToCurve(start_pos[1], end_pos[1], duration)
    move_to_2d_curve = Animation2DCurve(move_to_curve_x, move_to_curve_y)
    animation_task.bind_property(property_name, move_to_2d_curve)
    return animation_task


def smooth_damp_2d(property_name, start_pos, end_pos, duration = 1):
    animation_task = AnimationTask(duration=duration, loop=False)
    smooth_damp_x = SmoothDampCurve(start_pos[0], end_pos[0], duration)
    smooth_damp_y = SmoothDampCurve(start_pos[1], end_pos[1], duration)
    smooth_damp_2d_curve = Animation2DCurve(smooth_damp_x, smooth_damp_y)
    animation_task.bind_property(property_name, smooth_damp_2d_curve)
    return animation_task


def hop_sequence(property_name, start_pos, offset, pre_time=1, post_time=1, hop_time = 0.3, loop=True):
    animation_task_1 = constant_2d(property_name, start_pos, pre_time)
    animation_task_2 = hop_2d(property_name, start_pos, offset, hop_time)
    animation_task_3 = constant_2d(property_name, start_pos, post_time)

    sequence_task = AnimationSequenceTask(loop=loop)
    sequence_task.add_sub_task(animation_task_1)
    sequence_task.add_sub_task(animation_task_2)
    sequence_task.add_sub_task(animation_task_3)

    return sequence_task

def sway_sequence(property_name, start_pos, end_pos, pre_time=1, post_time=1, hop_time = 0.5, loop=True):

    animation_task_1 = constant_2d(property_name, start_pos, pre_time)
    animation_task_2 = ping_pong(property_name, start_pos,  end_pos, hop_time)
    animation_task_3 = constant_2d(property_name, start_pos, post_time)

    sequence_task = AnimationSequenceTask(loop=loop)
    sequence_task.add_sub_task(animation_task_1)
    sequence_task.add_sub_task(animation_task_2)
    sequence_task.add_sub_task(animation_task_3)

    return sequence_task


animation = Animation()



