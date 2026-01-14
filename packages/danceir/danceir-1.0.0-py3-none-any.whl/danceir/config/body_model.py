"""Body model definitions for keypoint systems.

This module contains marker/joint definitions and body part groupings
for various keypoint formats (COCO, etc.).
"""

# COCO-style marker/joint dictionary
MARKER_DICT = {
    0: "nose",
    1: "left_eye",
    2: "right_eye",
    3: "left_ear",
    4: "right_ear",
    5: "left_shoulder",
    6: "right_shoulder",
    7: "left_elbow",
    8: "right_elbow",
    9: "left_wrist",
    10: "right_wrist",
    11: "left_hip",
    12: "right_hip",
    13: "left_knee",
    14: "right_knee",
    15: "left_ankle",
    16: "right_ankle",
}

# Reverse mapping: name -> ID
MARKER_NAME_TO_ID = {name: idx for idx, name in MARKER_DICT.items()}

# Body part groupings for Center of Mass computation
COM_PART_INDICES = {
    "hips": [11, 12],      # left_hip, right_hip
    "shoulders": [5, 6],   # left_shoulder, right_shoulder
    "torso": None,         # Computed as mean of hips + shoulders
}

# Common marker groups
MARKER_GROUPS = {
    "wrist": [9, 10],      # left_wrist, right_wrist
    "ankle": [15, 16],     # left_ankle, right_ankle
    "hand": [9, 10],
    "foot": [15, 16],
}

