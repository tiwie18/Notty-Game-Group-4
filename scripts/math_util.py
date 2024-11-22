import math


def calc_normalized_rotation(rotation2d):
    sq_sum = rotation2d[0] * rotation2d[0] + rotation2d[1] * rotation2d[1]
    if sq_sum == 0:
        # normalization failed
        return None
    ratio = 1 / math.sqrt(sq_sum)
    return rotation2d[0] * ratio, rotation2d[1] * ratio


def rotation_to_euler_angle(rotation2d):
    # y first
    rad = math.atan2(rotation2d[1], rotation2d[0])
    return math.degrees(rad)


def euler_angle_to_rotation(angle):
    rad = math.radians(angle)
    x = math.cos(rad)
    y = math.sin(rad)
    return x, y