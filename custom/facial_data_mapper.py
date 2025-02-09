import numpy as np
import torch

class FacialDataMapper:
    def __init__(self):
        # Define blend shape mappings for your 3D character
        self.blendshape_mappings = {
            'brow_up': [0, 1],     # Landmark indices for eyebrow movement
            'brow_down': [2, 3],
            'eye_blink': [6, 18],  # Eye closure landmarks
            'mouth_open': [90, 102], # Mouth open/close landmarks
            'mouth_wide': [48, 66]  # Mouth width landmarks
        }
        
    def process_facial_data(self, pitch, yaw, roll, t, exp, scale, kp):
        """
        Convert FasterLivePortrait data to 3D character control parameters
        
        Args:
            pitch, yaw, roll: Head rotation angles
            t: Translation
            exp: Expression parameters
            scale: Scale factor
            kp: Facial landmarks (keypoints)
            
        Returns:
            dict: Mapped parameters for 3D character rig
        """
        # Convert rotation angles to character head rotation
        head_rotation = {
            'x': float(pitch),  # Map pitch to head up/down
            'y': float(yaw),    # Map yaw to head left/right
            'z': float(roll)    # Map roll to head tilt
        }
        
        # Process facial landmarks for blendshapes
        blendshapes = {}
        kp = np.array(kp)
        
        # Calculate eye blink
        left_eye_ratio = self._calculate_distance_ratio(
            kp, 
            self.blendshape_mappings['eye_blink'][0],
            self.blendshape_mappings['eye_blink'][1]
        )
        blendshapes['eye_blink_left'] = left_eye_ratio
        
        # Calculate mouth opening
        mouth_ratio = self._calculate_distance_ratio(
            kp,
            self.blendshape_mappings['mouth_open'][0],
            self.blendshape_mappings['mouth_open'][1]
        )
        blendshapes['mouth_open'] = mouth_ratio
        
        return {
            'head_rotation': head_rotation,
            'blendshapes': blendshapes,
            'translation': t.tolist(),
            'expression': exp.tolist()
        }
    
    def _calculate_distance_ratio(self, landmarks, idx1, idx2):
        """Calculate the distance ratio between two landmarks"""
        if landmarks.ndim > 2:
            landmarks = landmarks[0]  # Take first set if batched
        
        point1 = landmarks[idx1]
        point2 = landmarks[idx2]
        distance = np.linalg.norm(point1 - point2)
        return float(distance)
