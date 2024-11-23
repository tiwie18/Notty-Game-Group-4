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


def vec_2d_plus(vec1, vec2):
    return vec1[0] + vec2[0], vec1[1] + vec2[1]

def vec_2d_minus(vec1, vec2):
    return vec1[0] - vec2[0], vec1[1] - vec2[1]

def vec_2d_dot(vec1, vec2):
    return vec1[0] * vec2[0] + vec1[1] * vec2[1]

def normalize_vec2d(vec):
    sq_sum = vec[0] * vec[0] + vec[1] * vec[1]
    if sq_sum == 0:
        # normalization failed
        return None
    ratio = 1 / math.sqrt(sq_sum)
    return vec[0] * ratio, vec[1] * ratio

def vec_2d_mul(vec, num):
    return vec[0] * num, vec[1] * num

def rotate_vec2d(vec, rot):
    return vec[0] * rot[0] - vec[1] * rot[1], vec[1] * rot[0] + vec[0] * rot[1]