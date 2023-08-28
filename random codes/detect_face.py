__author__ = "Ernesto"
__email__ = "ernestondieki12@gmail.com"
# pip install opencv-python
# pip install opencv-contrib-python
import cv2


face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')
capture = cv2.VideoCapture(0)


def shots():
    # run forever only while the camera is on
    while (capture.isOpened()):
        ret, frame = capture.read()
        if ret:
            # convert to gray
            grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # detect faces, return tuple of faces coords
            faces = face_cascade.detectMultiScale(grayscale,
                                                  scaleFactor=1.5,
                                                  minNeighbors=5)
            for (x, y, w, h) in faces:
                # roi_gray = grayscale[y:y + h, x:x + w]
                cv2.putText(frame,
                            "See your life",  # text to display
                            (x, y - 10),  # coordinates of bottom-left
                            cv2.FONT_HERSHEY_COMPLEX,  # text font
                            1,  # font scale
                            (255, 255, 255),  # text color (RGB)
                            1,  # text line thickness in px
                            cv2.LINE_AA  # text line type
                            )
                # rectangle properties
                color = (0, 255, 0)
                stroke = 2
                width = x + w
                height = y + h
                # create rectangle around faces detected
                cv2.rectangle(frame,
                              (x, y),
                              (width, height),
                              color,
                              stroke)
            # show output to the screen
            cv2.imshow('CAMERA', frame)
            # press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
    # release resources
    capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # execute
    shots()
