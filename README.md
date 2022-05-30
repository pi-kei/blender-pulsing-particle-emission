# Blender Addon: Pulsing Particle Emitting

Creates pulsing particle emitters based on selected particle system whitch could be useful for music visualization.
Blender does not have a way to turn on/off emission of the particles and this approach is kind of a workaround.

## Installation

1. Go to [github repository](https://github.com/pi-kei/blender-pulsing-particle-emitting)
2. Click Code -> [Download ZIP](https://github.com/pi-kei/blender-pulsing-particle-emitting/archive/refs/heads/master.zip)
3. Unzip anywhere
4. Open Blender
5. Go to Edit -> Preferences -> Add-ons
6. Click Install
7. Choose .py file from previously unzipped archive and click Install Add-on
8. Enable add-on

## Usage

1. Select object that would be particle emitter
2. Add particle system
3. Tweak settings keepeing on your mind that this particle system is first pulse and every new particle system would be the same except start frame and end frame
4. With particle system being selected open Particle Specials menu and choose Create Pulsing Particle Emitters
5. Set inputs (see description below)
6. Click OK

## Inputs

- **BPM** Beats per minute or pulses per minute. First beat frame will be taken from selected particle system from Frame Start.
- **Beats per Loop** Allows to skip beats in a loop. Ignore this if you don't need to skip beats.
- **Skip Nth Beat** Comma-separated list of beats to skip in a loop. Ranges are also accepted. Example: `1, 3-4`. Leave it empty if you don't need to skip beats.
- **Frame End** No beats after this frame.
- **Change Seed** Sets seed to a different value for every created particle system.

![blender_0cRAVe89hR](https://user-images.githubusercontent.com/3518025/170894299-7e6fd83d-90dc-4a33-893d-10ec73932ee0.gif)
