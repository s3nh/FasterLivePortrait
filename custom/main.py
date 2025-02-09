import cv2
from portrait_to_3d import PortraitTo3D
from src.models.motion_extractor_model import MotionExtractorModel

def main():
    # Initialize FasterLivePortrait motion extractor
    motion_extractor = MotionExtractorModel(
        model_path="checkpoints/motion_extractor.onnx",
        predict_type="trt"
    )
    
    # Initialize 3D character pipeline
    portrait_3d = PortraitTo3D("path/to/your/3d/character.fbx")
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process frame and update 3D character
        portrait_3d.process_frame(frame, motion_extractor)
        
        # Display original frame (optional)
        cv2.imshow('Input', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
