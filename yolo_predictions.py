
from ultralytics import YOLO
import cv2

class SHARK :
    def __init__(self,model_path):
        # นำโมเดลเข้ามา
        self.model = YOLO(model_path)
                # เพิ่ม dictionary เก็บชื่อสายพันธุ์
        
    def __call__(self,filename_fullpath, results):
        # อ่านรูปที่ต้องการที่จะ detect
        img = cv2.imread(filename_fullpath)
        
        results = self.model(filename_fullpath)[0]

        
        # ใช้ for เพื่อรองรับการเจอ object มากกว่า 1 
        for i in range(len(results.boxes.data)):
            boxes = results.boxes.data[i].numpy().tolist()
            text_size = cv2.getTextSize(f'{results.names[int(boxes[5])]}:{int(boxes[4]*100)}%', 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            text_x = int(boxes[0]) + (int(boxes[2]) - int(boxes[0]) - text_size[0]) // 2
            text_y = int(boxes[1]) + text_size[1] + 8
            cv2.rectangle(img, (int(boxes[0]), int(boxes[1])),
                      (int(boxes[2]), int(boxes[3])), [0, 255, 0], 2)
            cv2.putText(img,
                        f'{results.names[int(boxes[5])]}:{int(boxes[4]*100)}%',
                        (text_x, text_y),cv2.FONT_HERSHEY_SIMPLEX,1, [225, 0, 0],thickness=2)
        cv2.imwrite(filename_fullpath,img)
        
    
    
    



