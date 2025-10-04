Skybound 2.0

A 2D platformer built with Python and Pygam with random procedural level generation, enemys, multiple screens, power-ups, achievements, and visual effects. Straight up run main.py or run pyinstaller skybound.spec for the included build system

<table>
  <tr>
    <td><img src="imgs/pic1.png"/></td>
    <td><img src="imgs/pic2.png"/></td>
    <td><img src="imgs/pic3.png"/></td>
  </tr>
</table>

<table>
  <tr>
    <td><img src="imgs/pic4.png"/></td>
    <td><img src="imgs/pic9.png"/></td>
    <td><img src="imgs/pic10.png"/></td>
  </tr>
</table>

<table>
  <tr>
    <td><img src="imgs/pic8.png"/></td>
    <td><img src="imgs/pic6.png"/></td>
  </tr>
</table>


Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/AxelSuu/Skybound-2.0
   cd Skybound
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Build the application
   ```
   pyinstaller skybound.spec
   ```
4. Or run in code
   ```
   python3 main.py
   ```

Gameplay
- Physics-based movement with acceleration and friction
- Procedural level generation with increasing difficulty
- Multiple enemy types with unique AI behaviors  
- Power up system with temporary and permanent upgrades
- Health and damage system with invincibility frames
- Coin collection and persistent statistics

Visual Effects
- Particle systems for explosions, trails, and ambient effects
- Floating text for damage numbers and notifications
- Power-up indicators and visual feedback
- Smooth animations for all characters and objects

Audio
- Dynamic background music that changes with game state
- Procedural sound effects for actions and collisions

Progression Systems
- Achievement system with 15+ unique achievements
- Persistent player statistics across sessions
- Character customization with unlockable hats
- High score tracking and level progression

Controls
- **Space/Up Arrow**: Jump
- **Left/Right Arrow**: Move left/right

Functionality to add:
- Background shaders, web version port

I took the background images from here
[Background images](https://craftpix.net/freebies/free-sky-with-clouds-background-pixel-art-set/)



