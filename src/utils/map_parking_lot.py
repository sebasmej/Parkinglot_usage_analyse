import cv2

#Skript helps to map the parking lot and generate the parking_lot_map file with the corrdinates of the spots (not automatically)
# To use, run it. than by clicking a rectangle will appear drag the rectangle to the desire spot and realease the click to obtain the coordinates printed in the consola (x,y,w,h)
# Repeat this process as needed. To quit press q
# copy from console and manually make the map file
# If the rectagles are too big manually change the rect_width, rect_height


# Global variables
drawing = False  # True if mouse is pressed
start_x, start_y = -1, -1  # x, y coordinates of the starting point
rect_width, rect_height = 28, 35 # predefined dimensions of the rectangle
rect_x, rect_y = -1, -1  # x, y coordinates of the top-left corner of the rectangle
rectangles = []  # List to store drawn rectangles

# Mouse callback function
def draw_rectangle(event, x, y, flags, param):
    global start_x, start_y, drawing, rect_x, rect_y

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_x, start_y = x, y
        rect_x, rect_y = x - rect_width // 2, y - rect_height // 2
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            rect_x = x - rect_width // 2
            rect_y = y - rect_height // 2
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        rectangles.append((rect_x, rect_y, rect_x + rect_width, rect_y + rect_height))
        print(rect_x,",", rect_y,",",rect_width ,",", rect_height)

# Read an image
img = cv2.imread(r'C:\T3100\Projects\Parkinglot_usage_analyse\data\parking_lot.jpg')

# Create a window and bind the function to window
cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_rectangle)

while True:
    img_copy = img.copy()  # Make a copy of the original image
    if rectangles:
        for rect in rectangles:
            cv2.rectangle(img_copy, (rect[0], rect[1]), (rect[2], rect[3]), (0, 255, 0), 2)
    cv2.rectangle(img_copy, (rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height), (0, 255, 0), 2)
    cv2.imshow('image', img_copy)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

"""
159,582,239,662
213,560,293,640
261,539,341,619
310,512,390,592
360,495,440,575
412,476,492,556
457,453,537,533
502,430,582,510
591,394,671,474
637,376,717,456
679,358,759,438
721,340,801,420
763,326,843,406
803,313,883,393
880,280,960,360
915,261,995,341
953,247,1033,327
990,230,1070,310
1028,216,1108,296
1060,203,1140,283
1096,191,1176,271
277,598,357,678
327,573,407,653
372,544,452,624
422,522,502,602
472,502,552,582
525,485,605,565
573,461,653,541
616,438,696,518
663,418,743,498
708,402,788,482
794,366,874,446
838,350,918,430
880,333,960,413
923,317,1003,397
961,297,1041,377
1001,282,1081,362
1042,261,1122,341
1110,235,1190,315
1146,214,1226,294
1185,205,1265,285
1220,193,1300,273
387,619,467,699
446,590,526,670
494,568,574,648
543,547,623,627
592,522,672,602
642,500,722,580
693,478,773,558
742,456,822,536
834,416,914,496
880,397,960,477
922,377,1002,457
966,360,1046,440
1008,343,1088,423
1050,320,1130,400
1128,288,1208,368
1164,274,1244,354
1205,256,1285,336
1238,237,1318,317
1276,220,1356,300
1307,203,1387,283
1345,189,1425,269
503,642,583,722
566,614,646,694
620,588,700,668
673,563,753,643
723,538,803,618
776,517,856,597
825,492,905,572
875,471,955,551
924,448,1004,528
970,424,1050,504
1014,402,1094,482
1058,384,1138,464
1103,364,1183,444
1143,343,1223,423
1184,324,1264,404
1226,302,1306,382
1266,286,1346,366
1305,263,1385,343
1338,247,1418,327
1379,232,1459,312
1415,216,1495,296
1451,203,1531,283
1487,188,1567,268
651,658,731,738
713,630,793,710
769,608,849,688
822,585,902,665
876,560,956,640
930,535,1010,615
980,510,1060,590
1030,486,1110,566
1122,439,1202,519
1170,417,1250,497
1213,391,1293,471
1256,373,1336,453
1297,350,1377,430
1339,331,1419,411
1420,296,1500,376
1460,275,1540,355
1497,257,1577,337
1534,238,1614,318
1568,218,1648,298
815,694,895,774
857,662,937,742
932,635,1012,715
990,605,1070,685
1041,573,1121,653
1092,549,1172,629
1144,521,1224,601
1193,497,1273,577
1236,475,1316,555
1292,447,1372,527
1335,423,1415,503
1381,398,1461,478
1423,378,1503,458
1465,356,1545,436
1507,338,1587,418
1548,312,1628,392
1587,293,1667,373
1628,275,1708,355
1119,655,1199,735
1167,625,1247,705
1229,590,1309,670
1280,568,1360,648
1330,538,1410,618
1381,509,1461,589
1475,457,1555,537
1519,431,1599,511
1564,407,1644,487
1607,383,1687,463
1649,362,1729,442
1693,338,1773,418
1435,621,1515,701
1489,586,1569,666
1539,555,1619,635
1588,527,1668,607
1640,493,1720,573
1685,467,1765,547
1731,434,1811,514
"""