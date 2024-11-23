import cv2

cap = cv2.VideoCapture("/Users/vinayakgandhi/Downloads/default/ENG002200.avi")


fps = cap.get(cv2.CAP_PROP_FPS)
print(fps)
count = 0

while (True):
    ret, frame = cap.read()

    if ret == True:
        # cv2.imshow('win', frame)
        if (count % int(fps) == 0):
            cv2.imwrite(
                f"/Users/vinayakgandhi/Downloads/side_view/save/{count}.jpg", frame)
        count += 1
    else:
        break


cap.release()
cv2.destroyAllWindows()
