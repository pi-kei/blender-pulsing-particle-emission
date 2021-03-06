bl_info = {
    "name": "Pulsing particle emission",
    "description": "Helps to achieve pulsing particle emission.",
    "author": "ComputersDontCompost",
    "version": (1, 0),
    "blender": (3, 1, 2), # could work in older versions but not tested
    "location": "Object > Particle Properties > Particle Specials",
    #"warning": "", # used for warning icon and text in addons panel
    "doc_url": "https://github.com/pi-kei/blender-pulsing-particle-emission#readme",
    "tracker_url": "https://github.com/pi-kei/blender-pulsing-particle-emission/issues",
    "support": "COMMUNITY",
    "category": "Object",
}

import bpy
import re


class CreatePulsingParticleEmission(bpy.types.Operator):
    """Creates particle systems from selected one and sets specific start frame and end frame"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.create_pulsing_particle_emission"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Create Pulsing Patricle Emission"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    
    bpm: bpy.props.FloatProperty(name="BPM", description="Beats per Minute", default=120.0, min=1.0, max=3600.0, step=100)
    beats_per_loop: bpy.props.IntProperty(name="Beats per Loop", description="Allows to skip beats in a loop", default=4, min=1, step=1)
    skip_nth_beat: bpy.props.StringProperty(name="Skip Nth Beat", description="Comma-separated list of beats to skip in a loop. Example: 1,3-4")
    hide_skipped: bpy.props.BoolProperty(name="Hide Skipped Beats", description="Add but hide skipped beats")
    frame_end: bpy.props.FloatProperty(name="Frame End", description="No beats after this frame", step=100)
    change_seed: bpy.props.BoolProperty(name="Change Seed", description="Sets seed to a different value for every created particle system")
    custom_property_name: bpy.props.StringProperty(name="Custom Property Name", description="Name of the custom property of particle settings to be controlled by f-curve below")
    
    fcurve_items = []
    fcurve_map = {}
    
    def get_fcurves(self, context):
        fcurves = []
        CreatePulsingParticleEmission.fcurve_map = {}
        fcurves.append(("No-fcurve", "", ""))
        for a in bpy.data.actions:
            for fc in a.fcurves:
                el = "action_name=" + a.name + " data_path=" + fc.data_path + " index=" + str(fc.array_index)
                fcurves.append((el, el, ""))
                CreatePulsingParticleEmission.fcurve_map[el] = fc
        CreatePulsingParticleEmission.fcurve_items = fcurves
        return fcurves
    
    custom_property_fcurve: bpy.props.EnumProperty(name="F-curve", description="F-curve to set particle settings custom property for every created particle system", items=get_fcurves)
    set_noncustom_props: bpy.props.BoolProperty(name="Set Non-Custom Properties", description="Takes value from a custom property of particle system settings and copies it to a non-custom property with the same name")
    
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
            beat_range = part.split('-', 2)
            if len(beat_range) == 2:
                for b in range(int(beat_range[0].strip()), int(beat_range[1].strip()) + 1):
                    skip_nth_beat.add(b)
            else:
                skip_nth_beat.add(int(beat_range[0].strip()))
        
        return skip_nth_beat
    
    def find_particle_system_modifier(self, context, particle_system):
        modifiers = context.object.modifiers
        count = len(modifiers)
        for i in range(count - 1, -1, -1):
            m = modifiers[i]
            if m.type == 'PARTICLE_SYSTEM' and m.particle_system == particle_system:
                return m
        return None
    
    def hide_particle_system_modifier(self, context, particle_system):
        m = self.find_particle_system_modifier(context, particle_system)
        if m is None:
            return
        m.show_render = False
        m.show_viewport = False

    def execute(self, context):
        
        particle_systems = context.object.particle_systems
        
        custom_property_name = self.custom_property_name
        custom_property_fcurve = None
        
        if self.custom_property_fcurve and self.custom_property_fcurve in CreatePulsingParticleEmission.fcurve_map:
            custom_property_fcurve = CreatePulsingParticleEmission.fcurve_map[self.custom_property_fcurve]
            
        set_noncustom_props = self.set_noncustom_props
        noncustom_props = []
        
        if set_noncustom_props:
            for cust_prop_name in particle_systems.active.settings.keys():
                if hasattr(particle_systems.active.settings, cust_prop_name):
                    noncustom_props.append(cust_prop_name)
            if len(noncustom_props) == 0:
                set_noncustom_props = False
        
        beats_per_loop = self.beats_per_loop
        skip_nth_beat = self.parse_skips()
        hide_skipped = self.hide_skipped
        change_seed = self.change_seed
        bpm = self.bpm # beats per minute
        fps = context.scene.render.fps / context.scene.render.fps_base # frames per second
        fpm = fps * 60.0 # frames per minute
        fpb = fpm / bpm # frames per beat
        frame_start = particle_systems.active.settings.frame_start
        emit_duration = particle_systems.active.settings.frame_end - frame_start
        seed_current = particle_systems.active.seed
        frame_current = frame_start
        frame_end = self.frame_end
        beat_current = 1
        beat_loop_current = 1
        loop_current = 1
        first_beat_set = False

        while frame_current <= frame_end:
            to_skip = beat_loop_current in skip_nth_beat
            if hide_skipped or not to_skip:
                if first_beat_set:
                    bpy.ops.particle.duplicate_particle_system(use_duplicate_settings=True)
                    particle_systems.active_index = len(particle_systems.items()) - 1
                else:
                    first_beat_set = True
                ps_active = particle_systems.active
                if change_seed:
                    ps_active.seed = seed_current
                    seed_current += 1
                ps_active.settings.frame_start = frame_current
                ps_active.settings.frame_end = frame_current + emit_duration
                ps_active.settings["beat"] = beat_current
                ps_active.settings["beat_loop"] = beat_loop_current
                ps_active.settings["loop"] = loop_current
                if custom_property_name and custom_property_fcurve:
                    ps_active.settings[custom_property_name] = custom_property_fcurve.evaluate(frame_current)
                    if set_noncustom_props:
                        # set frame to update drivers if present to use updated values while setting non-custom props
                        context.scene.frame_set(int(frame_current))
                        for prop_name in noncustom_props:
                            setattr(ps_active.settings, prop_name, ps_active.settings[prop_name])
                if hide_skipped and to_skip:
                    self.hide_particle_system_modifier(context, ps_active)
            frame_current += fpb
            beat_current += 1
            beat_loop_current = ((beat_current - 1) % beats_per_loop) + 1
            loop_current = int((beat_current - 1) / beats_per_loop) + 1

        return {'FINISHED'}

class RemoveParticleSystems(bpy.types.Operator):
    """Removes particle systems matching pattern"""      # tooltip
    bl_idname = "object.remove_particle_systems"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Remove Patricle Systems"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    
    pattern: bpy.props.StringProperty(name="Pattern", description="Pattern to apply on particle system's name. Empty matches all")
    exclude_selected: bpy.props.BoolProperty(name="Exclude Selected", description="Selected particle system will not be removed", default=True)
    is_regexp: bpy.props.BoolProperty(name="Regular Expression", description="Pattern is a regular expression or it's a name substring")
    
    @classmethod
    def poll(self, context):
        return context.object is not None
    
    def invoke(self, context, event):
        if context.object.particle_systems.active:
            self.pattern = context.object.particle_systems.active.name
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        
        pattern = self.pattern
        exclude_selected = self.exclude_selected
        is_regexp = self.is_regexp
        
        selected = context.object.particle_systems.active
        count = len(context.object.particle_systems.items())
        
        for i in range(count - 1, -1, -1):
            context.object.particle_systems.active_index = i
            if exclude_selected and context.object.particle_systems.active == selected:
                continue
            if is_regexp and re.match(pattern, context.object.particle_systems.active.name) is None:
                continue
            if not is_regexp and pattern not in context.object.particle_systems.active.name:
                continue
            bpy.ops.object.particle_system_remove()

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(CreatePulsingParticleEmission.bl_idname)
    self.layout.operator(RemoveParticleSystems.bl_idname)

def register():
    bpy.utils.register_class(CreatePulsingParticleEmission)
    bpy.utils.register_class(RemoveParticleSystems)
    bpy.types.PARTICLE_MT_context_menu.append(menu_func)

def unregister():
    bpy.utils.unregister_class(CreatePulsingParticleEmission)
    bpy.utils.unregister_class(RemoveParticleSystems)
    bpy.types.PARTICLE_MT_context_menu.remove(menu_func)


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
