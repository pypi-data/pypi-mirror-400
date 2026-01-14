import cv2
import numpy as np
import mediapipe as mp

def extract_pose_mediapipe(video_path, output_npy=None, display=False):
    """
    Extract 2D pose landmarks (33 points) from a video using MediaPipe Pose.

    Args:
        video_path (str): Path to input video file.
        output_npy (str): Optional path to save pose data as .npy file.
        display (bool): If True, visualize landmarks on video.

    Returns:
        poses (list[np.ndarray]): List of frames, each (33, 3) -> [x, y, visibility]
    """
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    # Initialize Pose model
    pose = mp_pose.Pose(static_image_mode=False,
                        model_complexity=1,
                        enable_segmentation=False,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5)

    cap = cv2.VideoCapture(video_path)
    poses = []
    frame_idx = 0
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("FPS:", fps)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            pose_2d = np.array([[lm.x, lm.y, lm.visibility] for lm in landmarks])
        else:
            pose_2d = np.zeros((33, 3))  # Empty if no person detected

        poses.append(pose_2d)

        if display:
            annotated = frame.copy()
            mp_drawing.draw_landmarks(
                annotated, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            cv2.imshow('MediaPipe Pose', annotated)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        frame_idx += 1

    cap.release()
    cv2.destroyAllWindows()
    pose.close()

    poses = np.array(poses)
    print(f"Processed {frame_idx} frames → pose array shape: {poses.shape}")

    return poses, fps