import bpy
import numpy as np
import cv2
from mathutils import Vector, Euler
import json
import os
from collections import defaultdict

class BlenderFacialAnimator:
    def __init__(self, character_armature_name="Armature", fps=30):
        """
        Initialize Blender facial animation system
        
        Args:
            character_armature_name: Name of the armature in Blender
            fps: Animation frames per second
        """
        self.armature = bpy.data.objects[character_armature_name]
        self.fps = fps
        self.frame_count = 0
        self.shape_key_mappings = self._initialize_shape_keys()
        self.bone_mappings = self._initialize_bone_mappings()
        
    def _initialize_shape_keys(self):
        """
        Initialize mappings between FasterLivePortrait expressions and Blender shape keys
        Returns dictionary of shape key mappings
        """
        # Assuming the active object is the mesh with shape keys
        mesh_obj = next((obj for obj in bpy.data.objects 
                        if obj.type == 'MESH' and obj.data.shape_keys), None)
        if not mesh_obj:
            raise ValueError("No mesh with shape keys found")
            
        # Default shape key mappings - adjust these based on your character
        return {
            "eye_blink_left": "eye_blink.L",
            "eye_blink_right": "eye_blink.R",
            "mouth_open": "mouth_open",
            "mouth_wide": "mouth_wide",
            "brow_up_left": "brow_up.L",
            "brow_up_right": "brow_up.R"
        }
        
    def _initialize_bone_mappings(self):
        """
        Initialize mappings between FasterLivePortrait rotations and Blender bones
        Returns dictionary of bone mappings
        """
        return {
            "head": "head",  # Main head bone
            "neck": "neck"   # Neck bone if available
        }
        
    def create_keyframe(self, frame_number, bone_name, rotation=None, location=None):
        """
        Create keyframe for bone animation
        """
        bone = self.armature.pose.bones.get(bone_name)
        if not bone:
            return
            
        if rotation:
            bone.rotation_euler = Euler(rotation)
            bone.keyframe_insert(data_path="rotation_euler", frame=frame_number)
            
        if location:
            bone.location = Vector(location)
            bone.keyframe_insert(data_path="location", frame=frame_number)
            
    def update_shape_keys(self, shape_values):
        """
        Update shape key values for facial expressions
        
        Args:
            shape_values: Dictionary of shape key names and their values
        """
        for mesh_obj in bpy.data.objects:
            if mesh_obj.type == 'MESH' and mesh_obj.data.shape_keys:
                for shape_name, value in shape_values.items():
                    if shape_name in self.shape_key_mappings:
                        blender_shape_name = self.shape_key_mappings[shape_name]
                        if blender_shape_name in mesh_obj.data.shape_keys.key_blocks:
                            shape_key = mesh_obj.data.shape_keys.key_blocks[blender_shape_name]
                            shape_key.value = value
                            shape_key.keyframe_insert("value", frame=self.frame_count)
                            
    def process_faster_portrait_data(self, facial_data):
        """
        Process facial data from FasterLivePortrait and apply to Blender character
        
        Args:
            facial_data: Dictionary containing facial animation data
        """
        # Convert head rotation (degrees to radians)
        head_rotation = [
            np.radians(facial_data['head_rotation']['x']),  # Pitch
            np.radians(facial_data['head_rotation']['y']),  # Yaw
            np.radians(facial_data['head_rotation']['z'])   # Roll
        ]
        
        # Apply head rotation
        self.create_keyframe(
            self.frame_count,
            self.bone_mappings["head"],
            rotation=head_rotation
        )
        
        # Update shape keys for facial expressions
        self.update_shape_keys(facial_data['blendshapes'])
        
        # Increment frame counter
        self.frame_count += 1
        
    def save_animation(self, filepath):
        """
        Save the animation to a Blender file
        """
        bpy.ops.wm.save_as_mainfile(filepath=filepath)
        
class BlenderFacialRecorder:
    def __init__(self, output_path="facial_animation_data.json"):
        """
        Initialize recorder for saving facial animation data
        
        Args:
            output_path: Path to save the animation data
        """
        self.output_path = output_path
        self.animation_data = []
        
    def record_frame(self, facial_data):
        """
        Record facial data for one frame
        
        Args:
            facial_data: Dictionary containing facial animation data
        """
        self.animation_data.append(facial_data)
        
    def save(self):
        """
        Save recorded animation data to file
        """
        with open(self.output_path, 'w') as f:
            json.dump(self.animation_data, f)
            
    def load(self):
        """
        Load recorded animation data from file
        """
        if os.path.exists(self.output_path):
            with open(self.output_path, 'r') as f:
                return json.load(f)
        return []
