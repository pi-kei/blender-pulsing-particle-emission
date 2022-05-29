bl_info = {
    "name": "Pulsing particle emitting",
    "description": "Controlls when to emit particles and when not.",
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


class CreatePulsingParticleEmitters(bpy.types.Operator):
    """Creates particle systems from selected one and sets specific start ans end frames"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.create_pulsing_particle_emitters"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Create Pulsing Patricle Emitters"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    
    bpm: bpy.props.FloatProperty(name="BPM", description="Beats per minute", default=120.0, min=1.0, max=3600.0, step=100)
    frame_end: bpy.props.FloatProperty(name="Frame End", description="Final Frame to Start Emitting Particles", step=100)
    
    @classmethod
    def poll(self, context):
        return context.object is not None and context.object.particle_systems.active is not None
    
    def invoke(self, context, event):
        self.frame_end = context.scene.frame_end
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):        # execute() is called when running the operator.
        
        bpm = self.bpm # beats per minute
        fps = context.scene.render.fps / context.scene.render.fps_base # frames per second
        fpm = fps * 60.0 # frames per minute
        fpb = fpm / bpm # frames per beat
        frame_start = bpy.data.particles[bpy.context.object.particle_systems.active.settings.name].frame_start
        emit_duration = bpy.data.particles[bpy.context.object.particle_systems.active.settings.name].frame_end - frame_start
        original_settings = bpy.context.object.particle_systems.active.settings
        frame_current = frame_start + fpb
        frame_end = self.frame_end
        

        while frame_current <= frame_end:
            bpy.ops.particle.duplicate_particle_system()
            bpy.context.object.particle_systems.active_index = len(bpy.context.object.particle_systems.items()) - 1
            bpy.context.object.particle_systems.active.settings = original_settings.copy()
            bpy.data.particles[bpy.context.object.particle_systems.active.settings.name].frame_start = frame_current
            bpy.data.particles[bpy.context.object.particle_systems.active.settings.name].frame_end = frame_current + emit_duration
            frame_current += fpb

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