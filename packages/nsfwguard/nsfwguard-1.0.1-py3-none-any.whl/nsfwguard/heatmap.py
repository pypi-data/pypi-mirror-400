from nudenet import NudeDetector
import cv2

detector = NudeDetector()

def generate_heatmap(image, output="heatmap.jpg"):
    detections = detector.detect(image)
    img = cv2.imread(image)

    for d in detections:
        x1,y1,x2,y2 = d["box"]
        score = d["score"]
        color = (0, 0, int(255 * score))
        cv2.rectangle(img, (x1,y1), (x2,y2), color, 2)

    cv2.imwrite(output, img)
    return output
