"""
Demo Video Creator

Creates a simple example video for testing the pipeline.
Generates a ball hitting a cup using OpenCV.
"""

import cv2
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DemoVideoCreator:
    """
    Creates a simple physics demo video using OpenCV.
    """
    
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 60):
        """
        Initialize video creator.
        
        Args:
            width: Video width
            height: Video height
            fps: Frames per second
        """
        self.width = width
        self.height = height
        self.fps = fps
        self.duration = 5.0  # seconds
        self.total_frames = int(self.fps * self.duration)
    
    def create_ball_cup_demo(self, output_path: str | Path) -> Path:
        """
        Create a simple ball-hitting-cup demo video.
        
        Args:
            output_path: Where to save the video
            
        Returns:
            Path to created video
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"🎬 Creating demo video: {output_path.name}")
        logger.info(f"   Resolution: {self.width}x{self.height}")
        logger.info(f"   Duration: {self.duration}s @ {self.fps}fps")
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            str(output_path),
            fourcc,
            self.fps,
            (self.width, self.height)
        )
        
        # Physics parameters
        gravity = 9.81  # m/s^2
        ball_velocity_x = 2.0  # m/s horizontal
        ball_start_y = 1.5  # meters above ground
        
        # Convert to pixel space (scale: 1 meter = 200 pixels)
        scale = 200
        ground_y = self.height - 100
        
        ball_x_start = 100
        ball_y_start = ground_y - int(ball_start_y * scale)
        ball_radius = 25
        
        cup_x = self.width // 2 + 200
        cup_y = ground_y
        cup_radius = 30
        cup_height = 80
        
        # Generate frames
        for frame_num in range(self.total_frames):
            # Create blank frame
            frame = np.ones((self.height, self.width, 3), dtype=np.uint8) * 250
            
            # Add ground
            cv2.rectangle(
                frame,
                (0, ground_y),
                (self.width, self.height),
                (180, 150, 120),  # Brown ground
                -1
            )
            
            # Calculate ball position (projectile motion)
            t = frame_num / self.fps
            
            # Ball physics
            ball_x = ball_x_start + int(ball_velocity_x * scale * t)
            ball_y = ball_y_start + int(0.5 * gravity * scale * t * t)
            
            # Check if ball has hit cup
            if ball_x >= cup_x - cup_radius and ball_x <= cup_x + cup_radius:
                if ball_y >= cup_y - cup_height:
                    # Collision! Cup falls
                    cup_tilt = min(90, (frame_num - (cup_x / (ball_velocity_x * scale))*self.fps) * 3)
                    
                    # Draw falling cup
                    cup_center_y = cup_y - cup_height // 2 + int(cup_tilt * 0.5)
                    
                    # Rotated rectangle for cup
                    pts = self._get_rotated_rect(
                        cup_x, cup_center_y,
                        cup_radius * 2, cup_height,
                        cup_tilt
                    )
                    cv2.fillPoly(frame, [pts], (200, 100, 100))
                    cv2.polylines(frame, [pts], True, (150, 50, 50), 3)
                    
                else:
                    # Cup still standing
                    cv2.rectangle(
                        frame,
                        (cup_x - cup_radius, cup_y - cup_height),
                        (cup_x + cup_radius, cup_y),
                        (200, 100, 100),  # Red cup
                        -1
                    )
                    cv2.rectangle(
                        frame,
                        (cup_x - cup_radius, cup_y - cup_height),
                        (cup_x + cup_radius, cup_y),
                        (150, 50, 50),
                        3
                    )
            else:
                # Cup standing
                cv2.rectangle(
                    frame,
                    (cup_x - cup_radius, cup_y - cup_height),
                    (cup_x + cup_radius, cup_y),
                    (200, 100, 100),
                    -1
                )
                cv2.rectangle(
                    frame,
                    (cup_x - cup_radius, cup_y - cup_height),
                    (cup_x + cup_radius, cup_y),
                    (150, 50, 50),
                    3
                )
            
            # Draw ball (with shadow for depth)
            if ball_y < ground_y:
                # Shadow
                shadow_y = ground_y
                shadow_radius = int(ball_radius * 0.8)
                cv2.ellipse(
                    frame,
                    (ball_x, shadow_y),
                    (shadow_radius, shadow_radius // 2),
                    0, 0, 360,
                    (100, 100, 100),
                    -1
                )
                
                # Ball
                cv2.circle(
                    frame,
                    (ball_x, ball_y),
                    ball_radius,
                    (100, 150, 255),  # Orange ball
                    -1
                )
                cv2.circle(
                    frame,
                    (ball_x, ball_y),
                    ball_radius,
                    (80, 120, 200),
                    3
                )
                
                # Highlight
                cv2.circle(
                    frame,
                    (ball_x - 8, ball_y - 8),
                    5,
                    (255, 255, 255),
                    -1
                )
            else:
                # Ball has hit ground, stay there
                cv2.circle(
                    frame,
                    (ball_x, ground_y - ball_radius),
                    ball_radius,
                    (100, 150, 255),
                    -1
                )
                cv2.circle(
                    frame,
                    (ball_x, ground_y - ball_radius),
                    ball_radius,
                    (80, 120, 200),
                    3
                )
            
            # Add text overlay
            cv2.putText(
                frame,
                "4D-SynthForge Demo",
                (50, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                (50, 50, 50),
                3
            )
            
            cv2.putText(
                frame,
                f"Frame: {frame_num}/{self.total_frames}",
                (50, self.height - 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (100, 100, 100),
                2
            )
            
            # Write frame
            out.write(frame)
        
        out.release()
        
        logger.info(f"✅ Demo video created: {output_path}")
        logger.info(f"   Frames: {self.total_frames}")
        logger.info(f"   Size: {output_path.stat().st_size / (1024*1024):.1f} MB")
        
        return output_path
    
    def _get_rotated_rect(
        self,
        cx: int,
        cy: int,
        width: int,
        height: int,
        angle: float
    ) -> np.ndarray:
        """Get points for a rotated rectangle."""
        angle_rad = np.deg2rad(angle)
        
        # corners of rectangle before rotation
        corners = np.array([
            [-width/2, -height/2],
            [width/2, -height/2],
            [width/2, height/2],
            [-width/2, height/2]
        ])
        
        # Rotation matrix
        rot_matrix = np.array([
            [np.cos(angle_rad), -np.sin(angle_rad)],
            [np.sin(angle_rad), np.cos(angle_rad)]
        ])
        
        # Rotate and translate
        rotated = corners @ rot_matrix.T
        rotated[:, 0] += cx
        rotated[:, 1] += cy
        
        return rotated.astype(np.int32)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Create examples directory
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    
    output_path = examples_dir / "ball_cup.mp4"
    
    if output_path.exists():
        print(f"⚠️  Demo video already exists: {output_path}")
        response = input("Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    # Create demo video
    creator = DemoVideoCreator(width=1920, height=1080, fps=60)
    video_path = creator.create_ball_cup_demo(output_path)
    
    print(f"\n✅ Demo video ready!")
    print(f"   Path: {video_path}")
    print(f"\n🚀 Next steps:")
    print(f"   1. Analyze: python video_analyzer.py {video_path}")
    print(f"   2. Full pipeline: python main.py {video_path} --count 9")
