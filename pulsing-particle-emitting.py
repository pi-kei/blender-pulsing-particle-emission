bl_info = {
    "name": "Pulsing particle emitting",
    "description": "Helps to achieve pulsing particle emitting.",
    "author": "ComputersDontCompost",
    "version": (1, 0),
    "blender": (3, 1, 2), # could work in older versions but not tested
    "location": "Object > Particle Properties > Particle Specials",
    #"warning": "", # used for warning icon and text in addons panel
    "doc_url": "https://github.com/pi-kei/blender-pulsing-particle-emitting#readme",
    "tracker_url": "https://github.com/pi-kei/blender-pulsing-particle-emitting/issues",
    "support": "COMMUNITY",
    "category": "Object",
}

import bpy
import re


class CreatePulsingParticleEmitters(bpy.types.Operator):
    """Creates particle systems from selected one and sets specific start frame and end frame"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.create_pulsing_particle_emitters"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Create Pulsing Patricle Emitters"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    
    bpm: bpy.props.FloatProperty(name="BPM", description="Beats per Minute", default=120.0, min=1.0, max=3600.0, step=100)
    beats_per_loop: bpy.props.IntProperty(name="Beats per Loop", description="Allows to skip beats in a loop", default=4, min=1, step=1)
    skip_nth_beat: bpy.props.StringProperty(name="Skip Nth Beat", description="Comma-separated list of beats to skip in a loop. Example: 1,3-4")
    frame_end: bpy.props.FloatProperty(name="Frame End", description="No beats after this frame", step=100)
    change_seed: bpy.props.BoolProperty(name="Change Seed", description="Sets seed to a different value for every created particle system")
    
    @classmethod
    def poll(self, context):
        return context.object is not None and context.object.particle_systems.active is not None and context.object.particle_systems.active.settings.type == 'EMITTER'
    
    def invoke(self, context, event):
        self.frame_end = context.scene.frame_end
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    def parse_skips(self):
        value = self.skip_nth_beat
        skip_nth_beat = set()
        
        if not value:
            return skip_nth_beat
        
        if re.match('^(\s*\d+\s*(\-\s*\d+\s*)?)(,(\s*\d+\s*(\-\s*\d+\s*)?))*$', value) is None:
            raise ValueError("Skip Nth Beat doesn't match pattern")
        
        for part in value.split(','):
            beat_range = part.strip().split('-', 2)
            if len(beat_range) == 2:
                for b in range(int(beat_range[0].strip()), int(beat_range[1].strip()) + 1):
                    skip_nth_beat.add(b)
            else:
                skip_nth_beat.add(int(beat_range[0].strip()))
        
        return skip_nth_beat

    def execute(self, context):        # execute() is called when running the operator.
        
        beats_per_loop = self.beats_per_loop
        skip_nth_beat = self.parse_skips()
        particle_systems = context.object.particle_systems
        change_seed = self.change_seed
        bpm = self.bpm # beats per minute
        fps = context.scene.render.fps / context.scene.render.fps_base # frames per second
        fpm = fps * 60.0 # frames per minute
        fpb = fpm / bpm # frames per beat
        frame_start = bpy.data.particles[particle_systems.active.settings.name].frame_start
        emit_duration = bpy.data.particles[particle_systems.active.settings.name].frame_end - frame_start
        seed_current = particle_systems.active.seed
        frame_current = frame_start
        frame_end = self.frame_end
        beat_current = 1
        beat_loop_current = 1
        first_beat_set = False
        

        while frame_current <= frame_end:
            if beat_loop_current not in skip_nth_beat:
                if first_beat_set:
                    bpy.ops.particle.duplicate_particle_system(use_duplicate_settings=True)
                    particle_systems.active_index = len(particle_systems.items()) - 1
                else:
                    first_beat_set = True
                bpy.data.particles[particle_systems.active.settings.name].frame_start = frame_current
                bpy.data.particles[particle_systems.active.settings.name].frame_end = frame_current + emit_duration
                if change_seed:
                    particle_systems.active.seed = seed_current
                    seed_current += 1
            frame_current += fpb
            beat_current += 1
            beat_loop_current = ((beat_current - 1) % beats_per_loop) + 1

        return {'FINISHED'}            # Lets Blender know the operator finished successfully.

def menu_func(self, context):
    self.layout.operator(CreatePulsingParticleEmitters.bl_idname)

def register():
    bpy.utils.register_class(CreatePulsingParticleEmitters)
    bpy.types.PARTICLE_MT_context_menu.append(menu_func)  # Adds the new operator to an existing menu.

def unregister():
    bpy.utils.unregister_class(CreatePulsingParticleEmitters)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
