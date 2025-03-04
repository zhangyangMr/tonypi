# import cv2
# from PIL import Image
#
# from ultralytics import YOLO
#
# model = YOLO("yolo11n.pt")
# # accepts all formats - image/dir/Path/URL/video/PIL/ndarray. 0 for webcam
# # results = model.predict(source="0")
# # results = model.predict(source="folder", show=True)  # Display preds. Accepts all YOLO predict arguments
# #
# # from PIL
# im1 = Image.open("bus.jpg")
# results = model.predict(source=im1, save=True)  # save plotted images
#
# print(results)
#
# # # from ndarray
# # im2 = cv2.imread("bus.jpg")
# # results = model.predict(source=im2, save=True, save_txt=True)  # save predictions as labels
# #
# # # from list of PIL/ndarray
# # results = model.predict(source=[im1, im2])
import time

# from ultralytics import YOLO
#
# # Load a model
# model = YOLO("yolo11n.pt")  # pretrained YOLO11n model
#
# # Run batched inference on a list of images
# results = model(["bus.jpg"])  # return a list of Results objects
#
# # Process results list
# for result in results:
#     boxes = result.boxes  # Boxes object for bounding box outputs
#     masks = result.masks  # Masks object for segmentation masks outputs
#     keypoints = result.keypoints  # Keypoints object for pose outputs
#     probs = result.probs  # Probs object for classification outputs
#     obb = result.obb  # Oriented boxes object for OBB outputs
#     result.show()  # display to screen
#     result.save(filename="result.jpg")  # save to disk

# import cv2
#
# from ultralytics import YOLO
#
# # Load the YOLO model
# model = YOLO("yolo11n.pt")
#
# # Open the video file
# video_path = "path/to/your/video/file.mp4"
# cap = cv2.VideoCapture(0)
#
# # Loop through the video frames
# while cap.isOpened():
#     # Read a frame from the video
#     success, frame = cap.read()
#
#     if success:
#         # Run YOLO inference on the frame
#         results = model(frame)
#
#         # Visualize the results on the frame
#         annotated_frame = results[0].plot()
#
#         # Display the annotated frame
#         cv2.imshow("YOLO Inference", annotated_frame)
#
#         # Break the loop if 'q' is pressed
#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break
#     else:
#         # Break the loop if the end of the video is reached
#         break
#
# # Release the video capture object and close the display window
# cap.release()
# cv2.destroyAllWindows()

import cv2

from ultralytics import YOLO

# Load the YOLO11 model
model = YOLO("yolo11n.pt")

# Open the video file
video_path = "path/to/video.mp4"
cap = cv2.VideoCapture(0)

# Loop through the video frames
while cap.isOpened():
    time.sleep(0.1)
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLO11 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True)

        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame
        cv2.imshow("YOLO11 Tracking", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()