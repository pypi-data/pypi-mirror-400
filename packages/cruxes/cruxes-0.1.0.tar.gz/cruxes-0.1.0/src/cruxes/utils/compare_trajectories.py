import cv2
import mediapipe as mp
import numpy as np

from .pose_helpers import get_track_point_coords


def extract_pose_and_draw_trajectory_compare(
    video_paths,
    output_path=None,
    track_points=["hip_mid"],
):
    """
    Args:
        video_paths: List of input video paths.
        output_path: Path to save output video.
        track_points: List of track points, e.g. ["hip_mid"], ["upper_body_center"], or both.
    """
    mp_pose = mp.solutions.pose
    poses = [mp_pose.Pose() for _ in video_paths]
    caps = [cv2.VideoCapture(vp) for vp in video_paths]

    # Get video properties (use min of all for output)
    fps = min([cap.get(cv2.CAP_PROP_FPS) for cap in caps])
    width = int(min([cap.get(cv2.CAP_PROP_FRAME_WIDTH) for cap in caps]))
    height = int(min([cap.get(cv2.CAP_PROP_FRAME_HEIGHT) for cap in caps]))
    fourcc = int(caps[0].get(cv2.CAP_PROP_FOURCC))

    if output_path is None:
        output_path = (
            video_paths[0].rsplit(".", 1)[0] + "_compare_trajectory_output.mp4"
        )

    out = cv2.VideoWriter(
        output_path,
        fourcc if fourcc != 0 else cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    # Store trajectories for each video and track point
    trajectories = [{tp: [] for tp in track_points} for _ in video_paths]

    # Colors for each video (cycle if more than 10)
    color_palette = [
        (0, 0, 255),  # Red
        (0, 255, 0),  # Green
        (255, 0, 0),  # Blue
        (0, 255, 255),  # Yellow
        (255, 0, 255),  # Magenta
        (255, 255, 0),  # Cyan
        (128, 0, 128),  # Purple
        (0, 128, 255),  # Orange
        (128, 128, 0),  # Olive
        (0, 128, 128),  # Teal
    ]
    video_colors = [
        color_palette[i % len(color_palette)] for i in range(len(video_paths))
    ]

    # Store last valid frame and pose results for each video
    last_frames = [None for _ in video_paths]
    last_results = [None for _ in video_paths]

    while True:
        # Read frames for all videos
        frames = []
        rets = []
        for i, cap in enumerate(caps):
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
                rets.append(True)
                last_frames[i] = frame
            else:
                # If video ended, reuse last frame
                frames.append(last_frames[i])
                rets.append(False)
        # Stop only if all videos are done
        if all(r is False for r in rets):
            break

        # Resize all frames to the same size
        frames = [
            (
                cv2.resize(f, (width, height))
                if f is not None
                else np.zeros((height, width, 3), dtype=np.uint8)
            )
            for f in frames
        ]

        # Use the first video's frame as the background
        draw_frame = (
            frames[0].copy()
            if frames[0] is not None
            else np.zeros((height, width, 3), dtype=np.uint8)
        )

        # Add a semi-transparent black overlay
        overlay = draw_frame.copy()
        alpha = 0.5  # Adjust transparency (0: fully transparent, 1: fully black)
        cv2.rectangle(overlay, (0, 0), (width, height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, alpha, draw_frame, 1 - alpha, 0, draw_frame)

        # Draw legend (top left)
        legend_font = cv2.FONT_HERSHEY_SIMPLEX
        legend_scale = 0.7
        legend_thickness = 2
        legend_y = 30
        legend_gap = 35
        legend_x = 20
        legend_items = [
            (video_colors[i], f"Video {i+1}: {video_paths[i].split('/')[-1]}")
            for i in range(len(video_paths))
        ]
        for i, (color, label) in enumerate(legend_items):
            y = legend_y + i * legend_gap
            cv2.rectangle(
                draw_frame, (legend_x, y - 18), (legend_x + 28, y + 8), color, -1
            )
            cv2.putText(
                draw_frame,
                label,
                (legend_x + 38, y),
                legend_font,
                legend_scale,
                (255, 255, 255),
                legend_thickness,
                cv2.LINE_AA,
            )

        # Process all frames and update trajectories
        for idx, (pose, frame) in enumerate(zip(poses, frames)):
            if frame is not None:
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(image_rgb)
                last_results[idx] = results
            else:
                # If no frame, reuse last results
                results = last_results[idx]
            landmarks = (
                results.pose_landmarks.landmark
                if results and results.pose_landmarks
                else None
            )
            h, w = frame.shape[:2] if frame is not None else (height, width)
            for tp in track_points:
                if landmarks is not None:
                    coords = get_track_point_coords(tp, landmarks, w, h)
                    mid_point = coords[0] if coords is not None else None
                else:
                    mid_point = None
                if mid_point is not None:
                    trajectories[idx][tp].append(mid_point)
                else:
                    # If no new point, repeat last point if available
                    if len(trajectories[idx][tp]) > 0:
                        trajectories[idx][tp].append(trajectories[idx][tp][-1])
                    else:
                        trajectories[idx][tp].append(None)

        # Draw trajectories for all videos
        for vidx, traj_dict in enumerate(trajectories):
            color = video_colors[vidx]
            for tp in track_points:
                traj = traj_dict[tp]
                for i in range(1, len(traj)):
                    if traj[i - 1] is not None and traj[i] is not None:
                        cv2.line(draw_frame, traj[i - 1], traj[i], color, 2)
                # Draw an arrow at the latest segment if available
                if len(traj) > 1 and traj[-2] is not None and traj[-1] is not None:
                    # draw circle at the last point
                    cv2.circle(draw_frame, traj[-1], 5, color, -1)
                    cv2.arrowedLine(
                        draw_frame, traj[-2], traj[-1], color, 4, tipLength=0.6
                    )

        cv2.imshow("Compare Trajectories", draw_frame)
        out.write(draw_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    for cap in caps:
        cap.release()
    out.release()
    cv2.destroyAllWindows()
