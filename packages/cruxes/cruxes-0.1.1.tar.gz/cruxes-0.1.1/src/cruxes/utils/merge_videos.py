import cv2
import numpy as np


def merge_videos_vertically(video_path1, video_path2, output_path):
    cap1 = cv2.VideoCapture(video_path1)
    cap2 = cv2.VideoCapture(video_path2)

    # Get properties
    fps1 = cap1.get(cv2.CAP_PROP_FPS)
    fps2 = cap2.get(cv2.CAP_PROP_FPS)
    fps = min(fps1, fps2) if fps1 and fps2 else 30

    width1 = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
    height1 = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width2 = int(cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
    height2 = int(cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Use the maximum width and height for resizing
    out_width = max(width1, width2)
    out_height = max(height1, height2)

    # Output video size: stacked vertically
    combined_height = out_height * 2

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (out_width, combined_height))

    # Calculate frame step for each video
    step1 = int(round(fps1 / fps)) if fps1 > fps else 1
    step2 = int(round(fps2 / fps)) if fps2 > fps else 1

    idx1 = 0
    idx2 = 0

    while True:
        # Read frame for video 1
        ret1 = False
        frame1 = None
        for _ in range(step1):
            ret, frame = cap1.read()
            if not ret:
                break
            ret1 = True
            frame1 = frame
        if not ret1:
            frame1 = np.zeros((out_height, out_width, 3), dtype=np.uint8)
        else:
            frame1 = cv2.resize(frame1, (out_width, out_height))

        # Read frame for video 2
        ret2 = False
        frame2 = None
        for _ in range(step2):
            ret, frame = cap2.read()
            if not ret:
                break
            ret2 = True
            frame2 = frame
        if not ret2:
            frame2 = np.zeros((out_height, out_width, 3), dtype=np.uint8)
        else:
            frame2 = cv2.resize(frame2, (out_width, out_height))

        if not ret1 and not ret2:
            break

        combined = np.vstack((frame1, frame2))
        out.write(combined)

    cap1.release()
    cap2.release()
    out.release()


# Example usage:
parent_dir = "/Users/tommyjtl/Documents/Projects/climbing/videos/barrel-campus-may10"
video1_path = f"{parent_dir}/liu_warped_with_trajectory.mp4"
video2_path = f"{parent_dir}/weng_with_trajectory.mp4"
video_output_path = f"{parent_dir}/output.mp4"

merge_videos_vertically(
    video1_path,
    video2_path,
    video_output_path,
)
print(f"Merged video saved to {video_output_path}")
