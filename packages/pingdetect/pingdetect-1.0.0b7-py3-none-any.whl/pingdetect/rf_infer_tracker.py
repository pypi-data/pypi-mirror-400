'''
Copyright (c) 2025 Cameron S. Bodine
'''

import os, sys
import cv2
from inference import get_model
import importlib
import supervision as sv
import numpy as np
import time
import pandas as pd

# ensure supervision.detection.utils has box_iou_batch (compatibility shim)
try:
    utils_mod = importlib.import_module('supervision.detection.utils')
except Exception:
    utils_mod = None

if utils_mod is not None and not hasattr(utils_mod, 'box_iou_batch'):
    def box_iou_batch(boxes1, boxes2):
        """
        Simple numpy implementation returning pairwise IoU matrix between boxes1 (N,4) and boxes2 (M,4).
        Boxes are [x1, y1, x2, y2].
        """
        boxes1 = np.asarray(boxes1)
        boxes2 = np.asarray(boxes2)
        if boxes1.size == 0 or boxes2.size == 0:
            return np.zeros((boxes1.shape[0], boxes2.shape[0]))
        x1 = np.maximum(boxes1[:, None, 0], boxes2[None, :, 0])
        y1 = np.maximum(boxes1[:, None, 1], boxes2[None, :, 1])
        x2 = np.minimum(boxes1[:, None, 2], boxes2[None, :, 2])
        y2 = np.minimum(boxes1[:, None, 3], boxes2[None, :, 3])
        inter_w = np.maximum(0.0, x2 - x1)
        inter_h = np.maximum(0.0, y2 - y1)
        inter = inter_w * inter_h
        area1 = (boxes1[:, 2] - boxes1[:, 0]) * (boxes1[:, 3] - boxes1[:, 1])
        area2 = (boxes2[:, 2] - boxes2[:, 0]) * (boxes2[:, 3] - boxes2[:, 1])
        union = area1[:, None] + area2[None, :] - inter
        iou = inter / (union + 1e-9)
        return iou
    setattr(utils_mod, 'box_iou_batch', box_iou_batch)

# import trackers after shim
# from trackers import SORTTracker
from trackers import DeepSORTFeatureExtractor, DeepSORTTracker

# Add at the top of your file
last_boxes = None
last_ids = None


def do_tracker_inference(rf_model: str,
                         in_vids: list,
                         export_vid: bool=True,
                         confidence: float=0.2,
                         iou_threshold: float=0.2,
                         stride: float=0.2,
                         nchunk: int=500,
                         track_prop: float=0.8,
                         debug_export_frames: bool=False,
                         debug_frames_dir: str|None=None):

    '''
    '''

    # Store all annotations
    allCrabPreds = []

    # Get the model, tracker, and annotator
    model = get_model(rf_model)

    # minimum_consecutive_frames = int((nchunk / (nchunk*stride)) * track_prop)
    # print("Minimum Consecutive Frames: {}".format(minimum_consecutive_frames))

    feature_extractor = DeepSORTFeatureExtractor.from_timm(model_name="mobilenetv4_conv_small.e1200_r224_in1k")
    tracker = DeepSORTTracker(feature_extractor=feature_extractor,
                              lost_track_buffer=10,
                              frame_rate=10,
                              track_activation_threshold=0.1,                              
                              minimum_consecutive_frames=1,
                              minimum_iou_threshold=iou_threshold,
                              appearance_threshold=0.8,
                              appearance_weight=0.5,
                              distance_metric='cos',
                              )

    tracker.reset()
    annotator = sv.LabelAnnotator(text_position=sv.Position.TOP_CENTER)

    

    

    # Do inference
    start_time = time.time()
    for vid in in_vids:
        # Prep output name
        out_dir = os.path.dirname(vid)
        in_vid_name = os.path.basename(vid)
        out_vid_name = in_vid_name.replace('.mp4', '_track.mp4')
        out_vid = os.path.join(out_dir, out_vid_name)

        # Prepare debug frame directory
        if debug_export_frames:
            debug_dir = debug_frames_dir or os.path.join(out_dir, 'debug_frames')
            os.makedirs(debug_dir, exist_ok=True)

        print("\nProcessing Video: {}\n".format(vid))
        
        # Create callback for this video
        current_vid = vid
        def callback(frame: np.ndarray, index: int) -> np.ndarray:
            global last_boxes, last_ids
            result = model.infer(frame, confidence=confidence, iou_threshold=iou_threshold)[0]

            # create supervision annotators
            bounding_box_annotator = sv.BoxAnnotator()
            label_annotator = sv.LabelAnnotator()

            # load the results into the supervision Detections api
            detections = sv.Detections.from_inference(result).with_nms(threshold=iou_threshold, class_agnostic=True)
            detections = tracker.update(detections, frame=frame)
            
            # Prepare label for annotations
            labels = [f"{tracker_id} {confidence:0.2f}" for tracker_id, confidence in zip(detections.tracker_id, detections.confidence)]    

            # annotate the image with our inference results
            annotated_image = bounding_box_annotator.annotate(
                            scene=frame, detections=detections)
            annotated_image = label_annotator.annotate(
                scene=annotated_image, detections=detections, labels=labels)
            
            # Save current boxes and IDs for next frame
            last_boxes = detections.xyxy.copy()
            last_ids = detections.tracker_id.copy() # type: ignore

            if detections.tracker_id.size>0:
                # Build DataFrame from Detections attributes
                df = pd.DataFrame({
                    'video': current_vid,  # Use current_vid instead of in_vids[0]
                    'vid_frame_id':index,
                    'tracker_id': detections.tracker_id.tolist(),
                    'class_id': detections.class_id.tolist(),
                    'data': detections.data['class_name'],
                    'xyxy': detections.xyxy.tolist(),
                    'confidence': detections.confidence.tolist(),
                })

                df['vid_frame_id'] = index
                df['frame_width'] = frame.shape[1]
                df['frame_height'] = frame.shape[0]
                
                # Extract and store transect ID from video filename
                # Expected pattern: {rec}_{channel}_wcp_{transect_id}_movWin.mp4
                vid_parts = os.path.basename(current_vid).split('_')
                df['transect'] = int(vid_parts[-2])  # Second to last part is transect ID

                allCrabPreds.append(df)            

            if debug_export_frames:
                # Save annotated frame for debugging; pad index for ordering
                fname = os.path.join(debug_dir, f"frame_{index:06d}.jpg")
                cv2.imwrite(fname, annotated_image)

            return annotated_image
        
        sv.process_video(source_path=vid, target_path=out_vid, callback=callback, show_progress=True)
    print("\n\nInference Time (s):", round(time.time() - start_time, ndigits=1))
    
    # Extract detections
    if len(allCrabPreds) == 0:
        return
    else:
        crabDetections = pd.concat(allCrabPreds)

        # Write a deterministic combined CSV based on the FIRST video name
        first_vid = in_vids[0]
        first_out_vid = os.path.join(os.path.dirname(first_vid), os.path.basename(first_vid).replace('.mp4', '_track.mp4'))
        out_file = first_out_vid.replace('.mp4', '_ALL.csv')
        crabDetections.to_csv(out_file, index=False)

        return