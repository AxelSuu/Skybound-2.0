# Skybound Development Guide

This guide provides comprehensive information for developers working on the Skybound game project.

## Table of Contents
- [Getting Started](#getting-started)
- [Code Style Guidelines](#code-style-guidelines)
- [Architecture Overview](#architecture-overview)
- [Adding New Features](#adding-new-features)
- [Testing Guidelines](#testing-guidelines)
- [Performance Optimization](#performance-optimization)
- [Debugging Tips](#debugging-tips)
- [Common Issues](#common-issues)

## Getting Started

### Development Environment Setup

1. **Python Environment**
   ```bash
   # Recommended Python version
   python --version  # Should be 3.8+
   
   # Create virtual environment
   python -m venv skybound-env
   source skybound-env/bin/activate  # On Windows: skybound-env\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **IDE Configuration**
   - **Recommended IDEs**: PyCharm, VS Code, or Sublime Text
   - **Required Extensions**: Python, Pygame syntax highlighting
   - **Linting**: Enable PEP 8 compliance checking
   - **Type Checking**: Enable mypy or similar type checker

3. **Git Workflow**
   ```bash
   # Clone repository
   git clone https://github.com/yourusername/skybound.git
   cd skybound
   
   # Create feature branch
   git checkout -b feature/your-feature-name
   
   # Make changes and commit
   git add .
   git commit -m "Add: Your descriptive commit message"
   
   # Push and create pull request
   git push origin feature/your-feature-name
   ```

## Code Style Guidelines

### Python Style (PEP 8)

```python
# Good: Clear class and method documentation
class ExampleClass:
    """
    Brief description of the class.
    
    Detailed explanation of the class purpose, usage,
    and any important implementation details.
    
    Attributes:
        attribute_name (type): Description of the attribute
    """
    
    def __init__(self, param1: str, param2: int = 0):
        """
        Initialize the class with specified parameters.
        
        Args:
            param1 (str): Description of parameter
            param2 (int, optional): Description with default value
        """
        self.attribute_name = param1
        self.another_attribute = param2
    
    def example_method(self, input_value: float) -> bool:
        """
        Brief description of what the method does.
        
        Args:
            input_value (float): Description of the input
            
        Returns:
            bool: Description of the return value
            
        Raises:
            ValueError: When input_value is negative
        """
        if input_value < 0:
            raise ValueError("Input value must be non-negative")
        
        return input_value > 0
```

### Naming Conventions

```python
# Constants (ALL_CAPS)
MAX_HEALTH = 100
GRAVITY_CONSTANT = 0.5

# Classes (PascalCase)
class PlayerCharacter:
    pass

# Functions and variables (snake_case)
def calculate_distance(point_a, point_b):
    player_position = point_a
    return distance

# Private attributes (leading underscore)
class Example:
    def __init__(self):
        self._private_attribute = "internal use"
        self.public_attribute = "external use"
```

### Documentation Standards

```python
def complex_function(param1: str, param2: list, param3: dict = None) -> tuple:
    """
    One-line summary of the function.
    
    More detailed explanation of what the function does,
    including any algorithms, side effects, or important
    implementation details.
    
    Args:
        param1 (str): Description of the first parameter
        param2 (list): Description of the second parameter
        param3 (dict, optional): Description of optional parameter.
            Defaults to None.
    
    Returns:
        tuple: Description of the return value, including
            the structure if it's a complex type.
    
    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is not a list
    
    Example:
        >>> result = complex_function("test", [1, 2, 3])
        >>> print(result)
        (True, 3)
    """
    pass
```

## Architecture Overview

### System Dependencies

```
main.py (Entry Point)
    ├── State Management
    │   ├── Main Menu
    │   ├── Settings
    │   ├── Game Loop
    │   └── Achievements
    │
    ├── Game Systems
    │   ├── Player Management
    │   ├── Enemy AI
    │   ├── Physics Engine
    │   ├── Collision Detection
    │   └── Level Generation
    │
    ├── Audio Systems
    │   ├── Music Management
    │   ├── Sound Effects
    │   └── Spatial Audio
    │
    └── Persistence
        ├── Save/Load System
        ├── Settings Storage
        └── Achievement Progress
```

### Data Flow

```
User Input → Event System → Game State → Physics Update → Collision Detection → Rendering
     ↓           ↓              ↓             ↓               ↓                ↓
Audio System ← Effects ← Achievement ← Game Logic ← Sprite Update ← Screen Update
```

## Adding New Features

### Adding a New Enemy Type

1. **Create Enemy Class**
   ```python
   # In sprites/mob_types.py
   class NewEnemyType(BaseMob):
       """
       New enemy type with unique behavior.
       
       This enemy type provides [specific behavior description].
       """
       
       def __init__(self, x, y):
           super().__init__(x, y)
           self.unique_attribute = "specific_value"
           self.load_sprites()
       
       def update_ai(self, player_pos=None):
           """Implement unique AI behavior"""
           # Your AI logic here
           pass
       
       def load_sprites(self):
           """Load enemy-specific sprites"""
           # Sprite loading logic
           pass
   ```

2. **Update Enemy Factory**
   ```python
   # In sprites/mob_types.py
   def create_random_mob(x, y, level):
       """Update to include new enemy type"""
       mob_types = [BasicMob, JumperMob, ChaserMob, NewEnemyType]
       # Selection logic
   ```

3. **Test Integration**
   ```python
   # Create test cases
   def test_new_enemy_behavior():
       enemy = NewEnemyType(100, 100)
       enemy.update_ai((200, 100))  # Test AI
       assert enemy.some_expected_behavior()
   ```

### Adding a New Power-up

1. **Create Power-up Class**
   ```python
   # In sprites/powerups.py
   class NewPowerUp(BasePowerUp):
       """
       New power-up with unique effect.
       """
       
       def __init__(self, x, y):
           super().__init__(x, y)
           self.setup_appearance()
       
       def apply_effect(self, player):
           """Apply the power-up effect to player"""
           # Effect implementation
           pass
   ```

2. **Update Power-up Manager**
   ```python
   # In sprites/powerups.py
   class PowerUpManager:
       def spawn_random_powerup(self, x, y):
           powerup_types = [SpeedBoost, JumpBoost, NewPowerUp]
           # Spawning logic
   ```

### Adding New Achievements

1. **Define Achievement**
   ```python
   # In utils/achievements.py
   ACHIEVEMENTS = {
       "new_achievement": Achievement(
           "new_achievement",
           "Achievement Name",
           "Description of what player needs to do",
           "icon_name",
           requirement=100,
           reward=50
       )
   }
   ```

2. **Add Check Function**
   ```python
   def check_new_achievement(current_value):
       """Check if new achievement should be unlocked"""
       return check_achievement_unlock("new_achievement", current_value)
   ```

3. **Integrate in Game Loop**
   ```python
   # In gameloop/loop.py
   from utils.achievements import check_new_achievement
   
   # In appropriate game event
   achievement = check_new_achievement(player.some_stat)
   if achievement:
       # Show notification
   ```

## Testing Guidelines

### Unit Testing

```python
# tests/test_player.py
import unittest
from sprites.player import Player

class TestPlayer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.player = Player()
    
    def test_player_initialization(self):
        """Test player initializes with correct default values"""
        self.assertEqual(self.player.health, 3)
        self.assertEqual(self.player.coins, 0)
        self.assertFalse(self.player.has_double_jump)
    
    def test_player_movement(self):
        """Test player movement mechanics"""
        initial_pos = self.player.pos.copy()
        self.player.acc.x = 1.0
        self.player.update()
        self.assertNotEqual(self.player.pos.x, initial_pos.x)
    
    def test_power_up_application(self):
        """Test power-up effects on player"""
        self.player.apply_speed_boost(600)  # 10 seconds
        self.assertGreater(self.player.speed_boost_timer, 0)
```

### Integration Testing

```python
# tests/test_game_systems.py
import unittest
from gameloop.loop import Loop
from unittest.mock import Mock

class TestGameSystems(unittest.TestCase):
    def setUp(self):
        """Set up test game environment"""
        self.mock_main = Mock()
        self.game_loop = Loop(self.mock_main)
    
    def test_collision_detection(self):
        """Test player-enemy collision detection"""
        # Set up collision scenario
        # Test collision response
        pass
    
    def test_level_generation(self):
        """Test procedural level generation"""
        # Test platform placement
        # Test enemy spawning
        # Test reachability
        pass
```

### Performance Testing

```python
# tests/test_performance.py
import time
import psutil
from gameloop.loop import Loop

class TestPerformance(unittest.TestCase):
    def test_frame_rate_consistency(self):
        """Test that game maintains target frame rate"""
        game = Loop(Mock())
        start_time = time.time()
        
        # Run for 100 frames
        for _ in range(100):
            game.update()
        
        elapsed_time = time.time() - start_time
        fps = 100 / elapsed_time
        
        self.assertGreater(fps, 60)  # Should maintain 60+ FPS
    
    def test_memory_usage(self):
        """Test that memory usage stays within bounds"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Run game operations
        game = Loop(Mock())
        for _ in range(1000):
            game.update()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Should not increase by more than 50MB
        self.assertLess(memory_increase, 50 * 1024 * 1024)
```

## Performance Optimization

### Profiling

```python
# Use cProfile for performance analysis
import cProfile
import pstats

def profile_game_loop():
    """Profile the main game loop"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run game loop
    game = Loop(Mock())
    for _ in range(100):
        game.update()
    
    profiler.disable()
    
    # Analyze results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions
```

### Optimization Techniques

1. **Collision Detection Optimization**
   ```python
   # Use spatial partitioning for collision detection
   class SpatialGrid:
       def __init__(self, width, height, cell_size):
           self.cells = {}
           self.cell_size = cell_size
       
       def get_nearby_objects(self, x, y, radius):
           """Get objects in nearby cells only"""
           # Implementation
   ```

2. **Rendering Optimization**
   ```python
   # Batch sprite rendering
   def optimized_render(self, screen):
       """Render sprites in batches to reduce draw calls"""
       sprite_groups = self.group_sprites_by_texture()
       for texture, sprites in sprite_groups.items():
           # Batch render sprites with same texture
   ```

3. **Memory Management**
   ```python
   # Object pooling for frequently created/destroyed objects
   class ParticlePool:
       def __init__(self, size=100):
           self.pool = [Particle() for _ in range(size)]
           self.available = list(self.pool)
       
       def get_particle(self):
           if self.available:
               return self.available.pop()
           return Particle()  # Create new if pool empty
       
       def return_particle(self, particle):
           particle.reset()
           self.available.append(particle)
   ```

## Debugging Tips

### Common Debugging Scenarios

1. **Player Movement Issues**
   ```python
   # Add debug visualization
   def debug_player_physics(self, screen):
       """Draw debug information for player physics"""
       # Draw velocity vector
       end_pos = self.player.pos + self.player.vel * 10
       pg.draw.line(screen, (255, 0, 0), self.player.pos, end_pos, 2)
       
       # Draw acceleration vector
       acc_end = self.player.pos + self.player.acc * 100
       pg.draw.line(screen, (0, 255, 0), self.player.pos, acc_end, 2)
   ```

2. **Collision Detection Problems**
   ```python
   # Visualize collision boxes
   def debug_collision_boxes(self, screen):
       """Draw collision boxes for debugging"""
       for sprite in self.all_sprites:
           if hasattr(sprite, 'hitbox'):
               pg.draw.rect(screen, (0, 0, 255), sprite.hitbox, 2)
           pg.draw.rect(screen, (255, 255, 0), sprite.rect, 1)
   ```

3. **Performance Issues**
   ```python
   # Add performance monitoring
   class PerformanceMonitor:
       def __init__(self):
           self.frame_times = []
           self.max_samples = 60
       
       def update(self, frame_time):
           self.frame_times.append(frame_time)
           if len(self.frame_times) > self.max_samples:
               self.frame_times.pop(0)
       
       def get_average_fps(self):
           if not self.frame_times:
               return 0
           avg_time = sum(self.frame_times) / len(self.frame_times)
           return 1.0 / avg_time if avg_time > 0 else 0
   ```

### Debug Console

```python
# Add in-game debug console
class DebugConsole:
    def __init__(self):
        self.visible = False
        self.commands = {
            'player_health': self.set_player_health,
            'player_coins': self.set_player_coins,
            'spawn_enemy': self.spawn_enemy,
            'toggle_collision': self.toggle_collision_debug,
        }
    
    def handle_command(self, command_line):
        """Process debug commands"""
        parts = command_line.split()
        if not parts:
            return
        
        command = parts[0]
        args = parts[1:]
        
        if command in self.commands:
            self.commands[command](*args)
```

## Common Issues

### Issue: Player Falls Through Platforms

**Cause**: Collision detection running after physics update
**Solution**: 
```python
# Ensure collision detection happens before position update
def update(self):
    # Update velocity
    self.vel += self.acc
    
    # Check collisions before moving
    self.check_collisions()
    
    # Update position
    self.pos += self.vel
    self.rect.center = self.pos
```

### Issue: Audio Stuttering

**Cause**: Audio processing on main thread
**Solution**:
```python
# Use separate thread for audio processing
import threading

class AudioManager:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.audio_thread = threading.Thread(target=self.process_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()
    
    def process_audio(self):
        """Process audio in separate thread"""
        while True:
            try:
                audio_event = self.audio_queue.get(timeout=0.1)
                # Process audio event
            except queue.Empty:
                continue
```

### Issue: Memory Leaks

**Cause**: Not properly cleaning up pygame surfaces
**Solution**:
```python
# Proper cleanup in sprite classes
class Sprite(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surfaces_to_cleanup = []
    
    def kill(self):
        """Override kill to cleanup resources"""
        for surface in self.surfaces_to_cleanup:
            del surface
        super().kill()
```

## Conclusion

This development guide provides the foundation for working on the Skybound project. Always prioritize code quality, thorough testing, and comprehensive documentation. When in doubt, refer to the existing codebase for patterns and conventions.

For additional help, refer to:
- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [Pygame Documentation](https://www.pygame.org/docs/)
- [Game Development Best Practices](https://gameprogrammingpatterns.com/)

Happy coding!
