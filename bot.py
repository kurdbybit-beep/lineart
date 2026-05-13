def process_to_line_art(input_path, output_path):
    # خوێندنەوەی وێنە
    img = cv2.imread(input_path)
    
    # 1. گۆڕین بۆ ڕەنگی خۆڵەمێشی
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. کەمکردنەوەی وردەکارییە بێزارکەرەکان (Bilateral Filter)
    # ئەمە وێنەکە لووس دەکات بەبێ ئەوەی هێڵە سەرەکییەکان تێک بدات
    smooth = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # 3. دەرهێنانی هێڵەکان بە Canny
    # لێرەدا هێڵە سەرەکییەکان دەدۆزینەوە
    edges = cv2.Canny(smooth, 70, 150)
    
    # 4. ئەستوورکردنی هێڵەکان (Dilation)
    # بۆ ئەوەی وەک وێنە نموونەییەکە هێڵەکان دیار و پۆڵد بن
    kernel = np.ones((2, 2), np.uint8)
    thick_edges = cv2.dilate(edges, kernel, iterations=1)
    
    # 5. پێچەوانەکردنەوە (بۆ ئەوەی پشتخلف سپی و هێڵەکان ڕەش بن)
    line_art = cv2.bitwise_not(thick_edges)
    
    # پاشەکەوتکردنی وێنە
    cv2.imwrite(output_path, line_art)
