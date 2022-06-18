# Blender Addon: Pulsing Particle Emission

Creates pulsing particle emission based on selected particle system which could be useful for music visualization.
Blender does not have a way to turn on/off emission of the particles and this approach is kind of a workaround.

[Demo Videos on YouTube](https://www.youtube.com/playlist?list=PLf8ExqLxOaiZnVnTQTR4uFbH6LwK73rZn)

## Installation

1. Go to [github repository](https://github.com/pi-kei/blender-pulsing-particle-emission)
2. Click Code -> [Download ZIP](https://github.com/pi-kei/blender-pulsing-particle-emission/archive/refs/heads/master.zip)
3. Unzip anywhere
4. Open Blender
5. Go to Edit -> Preferences -> Add-ons
6. Click Install
7. Choose .py file from previously unzipped archive and click Install Add-on
8. Enable add-on

## Usage

1. Select object that would be particle emitter
2. Add particle system
3. Tweak settings keepeing on your mind that this particle system is first pulse and every new particle system would be the same except start frame and end frame<sup>\*</sup>
4. With particle system being selected open Particle Specials menu and choose Create Pulsing Particle Emission
5. Set inputs (see description below)
6. Click OK

<sup>\*</sup> Also two custom properties `beat`, `beat_loop` and `loop` with their corresponding values would be added to each particle system.

## Inputs

- **BPM** Beats per minute or pulses per minute. First beat frame will be taken from selected particle system from Frame Start.
- **Beats per Loop** Allows to skip beats in a loop. Ignore this if you don't need to skip beats.
- **Skip Nth Beat** Comma-separated list of beats to skip in a loop. Ranges are also accepted. Example: `1, 3-4`. Leave it empty if you don't need to skip beats.
- **Hide Skipped Beats** Add but hide skipped beats. Useful if you need a little manual tweaks for some beat variations.
- **Frame End** No beats after this frame.
- **Change Seed** Sets seed to a different value for every created particle system.
- **Custom Property Name** Name of the custom property of particle settings to be controlled by f-curve below. Property have to be created before. Leave it empty if you don't need custom property.
- **F-curve** F-curve to set particle settings custom property for every created particle system. F-curve will be evaluated at a Frame Start for created particle system and this value will be used as a value of a custom property. Leave it empty if you don't want this behavior.
- **Set Non-Custom Properties** Takes value from a custom property of particle system settings and copies it to a non-custom property with the same name. This allows you to change properties like `count` (total number of particles) per pulse which is not animatable otherwise. Doesn't do anything if Custom Property Name and F-curve omitted. To get non-custom property name quickly you can right click on the setting and select Copy Data Path.

## Additional notes about custom property and f-curve

When you specify Custom Property Name and F-curve each particle system corresponding to one beat will contain certain value inside custom property. Value is evaluated from F-curve at a Frame Start of particle system. And this value remains constant for each particle system during the lifetime of each particle. This value could be used to control the size of a particles with driver (driver must be added before applying this add-on to be copied across all particle systems) and to control material properties with Attribute shading node (set Type to Instancer and Name to custom property name).

![blender_0cRAVe89hR](https://user-images.githubusercontent.com/3518025/170894299-7e6fd83d-90dc-4a33-893d-10ec73932ee0.gif)
