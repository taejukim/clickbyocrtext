    # Click By OCR Text
    # If you enter the some text, you can get coordinates of that text in the screen.(using pytesseract)
    def clickByOCRText(self, UIText, x_shift=0, y_shift=0, order=-1):
		#
		# UIText : Target Text
		# x, y_shift : if you want to click other point based target text, you can shift x, y Coordinates
		# order : if objects are two or more in the screen, you can choose object by order.
		# 
        try:
            OCRText, x, y = self.getCoordinates(UIText, x_shift, y_shift)[order]
        except Exception as e:
            System.Debug(e)
            System.Debug('There is not {} in Image'.format(UIText))
            return False
        System.Debug('Click Obj {}, ({}, {})'.format(OCRText, x, y))
        # You have to make a click function in your side
		retv = self.click(x, y)  
        return retv
    
    def getCoordinates(self, string, img_file=None, x_shift=0, y_shift=0, threshold=110):
        snapshotlist = []
		# You have to make a Screen Capture function in your side
        img_list = self.ScrCapture(snapshotlist, width=1280,height=720)[0]
        img = Image.open(img_list['path']+img_list['name'])

        conv_img = img.convert("L")
        conv_img = conv_img.point(lambda p: p > threshold and 255)
        w, h = conv_img.size
        conv_img.save('conv.png')
        w_resize_rate = 1920.0/w
        h_resize_rate = 1080.0/h
        try:
            if not pt.run_tesseract('conv.png', 'result', lang=None, extension='box', config='hocr'):
                return False
        except:
            if not pt.run_tesseract('conv.png', 'result', lang=None, boxes=True, config='hocr'):
                return False
        html = open('result.hocr').read().replace('\n','')
        soup = bs(html, 'html.parser')
        spans = soup.findAll('span')
        result = []
        for span in spans:
            if string.lower() in span.text.lower():
                title = span.attrs['title'].replace(';','')
                box = title.split(" ")
                x = (int(box[3]) - int(box[1])) / 2 + int(box[1])
                y = (int(box[4]) - int(box[2])) / 2 + int(box[2])
                result.append((span.text ,int((x+x_shift)*w_resize_rate), int((y+y_shift)*h_resize_rate)))
                
        os.remove('result.hocr')
        os.remove('conv.png')
        if result:
            return result
        else:
			# Recursion, while threshold 110 to 20 (1 step is -15)
            if threshold > 20:
                result = self.getCoordinates(string, img_file, x_shift, y_shift, threshold = threshold-15)
                if result:
                    return result
            return False