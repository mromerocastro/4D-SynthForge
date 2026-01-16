# Examples Directory

This directory contains example videos for testing the 4D-SynthForge pipeline.

## Demo Videos

### ball_cup.mp4
**Auto-generated demo video**

- **Duration**: 5 seconds
- **Resolution**: 1920x1080 @ 60fps
- **Content**: Orange ball hits red cup, causing it to fall
- **Physics**: Projectile motion with gravity, collision dynamics
- **Purpose**: Perfect for testing the complete pipeline

**Generate it:**
```bash
python demo_video_creator.py
```

## Using Your Own Videos

You can use your own videos! Best practices:

### Video Requirements
- ✅ **Format**: MP4, MOV, or AVI
- ✅ **Duration**: 3-10 seconds (shorter = faster analysis)
- ✅ **Resolution**: 720p or higher recommended
- ✅ **Frame rate**: 30-60 fps

### Best Content for Analysis
✅ **Good examples:**
- Ball rolling down a ramp
- Objects falling and bouncing
- Simple collisions (ball hitting pins)
- Pendulum swinging
- Block stacking and falling

❌ **Avoid:**
- Complex scenes with many objects
- Fast motion (motion blur confuses analysis)
- Poor lighting or low contrast
- Human subjects (not the focus of this demo)

### Example Usage

```bash
# Analyze your own video
python video_analyzer.py your_video.mp4

# Full pipeline with your video
python main.py your_video.mp4 --count 100
```

## Sample Videos (Ideas for Recording)

### 1. Ball on Ramp
- Place a ball at the top of an inclined surface
- Let it roll down
- Simple gravity + rolling friction

### 2. Domino Effect
- Stack 3-5 dominoes
- Push the first one
- Captures collision chain reaction

### 3. Cup Tower
- Stack plastic cups in a pyramid
- Throw a ball to knock them down
- Tests complex multi-object interactions

### 4. Marble Run
- Simple marble rolling through a tube
- Clear trajectory for velocity estimation

## Tips for Recording

1. **Stable Camera**: Use a tripod or stable surface
2. **Good Lighting**: Even, bright lighting (natural light works great)
3. **Plain Background**: Helps with object detection
4. **Slow Motion**: If available, 120fps helps with analysis accuracy
5. **Multiple Angles**: Record same action from different angles for best results

## File Naming

Use descriptive names:
- `ball_hits_pins.mp4`
- `marble_roll.mp4`
- `block_stack_collapse.mp4`

This helps organize your analyses in the `output/` directory.
