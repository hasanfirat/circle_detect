from math import radians, cos, sin, pi, sqrt, pow
import cv2
import numpy as np
import time

aff = 0
def kamera_islem(goruntu):
    color_g = np.array([20,50,50]), np.array([80,255,255])
    roi,inrange, motor_hareket = main_islem(goruntu, color_g)
    roi = kamera_xy_cizgi(roi)
    return roi,inrange,motor_hareket

def main_islem(roi, color_g):
    global aff
    lower_color_HSV, upper_color_HSV = color_g
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    islencek_goruntu = cv2.inRange(hsv, lower_color_HSV, upper_color_HSV)
    kontur_sayisi = 100
    kernel = np.ones((2,2),np.uint8)
    is_goruntu = cv2.erode(islencek_goruntu, kernel, iterations=aff)
    #islencek_goruntu = cv2.dilate(islencek_goruntu, kernel, iterations=1)
    contours, hiyerarsi = cv2.findContours(is_goruntu, cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
    kontur_sayisi = len(contours)
    while kontur_sayisi > 30 and False:
        aff += 1
        is_goruntu = cv2.erode(islencek_goruntu, kernel, iterations=aff)
        #islencek_goruntu = cv2.dilate(islencek_goruntu, kernel, iterations=1)
        contours, hiyerarsi = cv2.findContours(is_goruntu, cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
        kontur_sayisi = len(contours)
    resim_yukseklik, resim_genislik, _ = roi.shape
    cam_orta_nokta_x, cam_orta_nokta_y = int(resim_genislik/2), int(resim_yukseklik/2)
    motor_hareket = None
    if len(contours)>0:
        roi, odak = goruntu_tarama(roi, contours, hiyerarsi, resim_yukseklik, resim_genislik)
        if odak is not None:
            uzaklikx, uzakliky, roi, motor_hareket = nesneye_kalibre(cam_orta_nokta_x, cam_orta_nokta_y, odak,roi)
    return roi, is_goruntu, motor_hareket

def goruntu_tarama( roi, contours, hiyerarsi, resim_yukseklik, resim_genislik):
    goruntu_tarandi = True
    sonuc_sayisi = 0
    if goruntu_tarandi == True and sonuc_sayisi == 0:
        roi,sonuc_sayisi,goruntu_tarandi, odak = cember_tarama(sonuc_sayisi, roi, contours, hiyerarsi, resim_yukseklik, resim_genislik,goruntu_tarandi)
    return roi, odak

def cember_tarama(sonuc_sayisi, roi, contours, hiyerarsi, resim_yukseklik, resim_genislik,goruntu_tarandi):
    kaideli_dizi = []
    kaideli_dizi_orta_nokta = []
    kaideli_dizi_alan = []
    kaideli_dizi_hiyerarsi = []

    h_kaideli_dizi = []
    h_kaideli_dizi_orta_nokta = []
    h_kaideli_dizi_alan = []
    h_kaideli_dizi_hiyerarsi = []

    ust_sinir = 200

    gecerli_dizi_hiyerarsi = []
    gecerli_dizi = []
    gecerli_dizi_say = []    
    gecerli_dizi_data = []
    gecerli_dizi_u = []
    
    for k in range(len(contours)):
        if len(contours[k])>10:
            nesne_yukseklik, nesne_genislik, angle_rect, nesne_orta_nokta_x, nesne_orta_nokta_y, bnd_x, bnd_y, bnd_w, bnd_h, nesne_box, rect = size_data(contours[k])            
            if bnd_x-5 > 0 and bnd_x+ bnd_w+5 < resim_genislik and bnd_y-5 > 0 and bnd_h+bnd_y+5 < resim_yukseklik:
                hiyer = hiyerarsi[0][k]
                Next, Previous, First_Child, Parent = hiyer[0],hiyer[1],hiyer[2],hiyer[3]
                if Parent != -1:
                    nesne_yukseklik_a, nesne_genislik_a, angle_rect_a, nesne_orta_nokta_x_a, nesne_orta_nokta_y_a, bnd_x_a, bnd_y_a, bnd_w_a, bnd_h_a, nesne_box_a, rect_a = size_data(contours[Parent])
                    if nesne_yukseklik  > nesne_yukseklik_a*0.01 and nesne_genislik > nesne_genislik_a*0.01 and nesne_genislik > resim_genislik*0.01 and nesne_yukseklik > resim_yukseklik*0.01:
                        if nesne_genislik > ust_sinir and nesne_yukseklik > ust_sinir:
                            contourse = kontur_kucult(contours[k], ust_sinir,nesne_genislik,nesne_yukseklik)
                            nesne_yukseklik_of, nesne_genislik_of, angle_rect_of, nesne_orta_nokta_x_of, nesne_orta_nokta_y_of, bnd_x_of, bnd_y_of, bnd_w_of, bnd_h_of, nesne_box_of, rect_of = size_data(contourse)
                            sonuc = drawing_ellipse(nesne_orta_nokta_x_of, nesne_orta_nokta_y_of, angle_rect_of,nesne_yukseklik_of, nesne_genislik_of,contourse)
                        else:
                            contourse = np.vstack(list(set(tuple(row[0]) for row in contours[k])))
                            sonuc = drawing_ellipse(nesne_orta_nokta_x, nesne_orta_nokta_y, angle_rect,nesne_yukseklik, nesne_genislik,contourse)                           
                        alan = nesne_genislik * nesne_yukseklik
                        if sonuc > 85 and int(ebob(nesne_yukseklik, nesne_genislik)*100) > 20:
                            sonuc_sayisi += 1
                            gecerli_dizi.append(contours[k])
                            while True == dizide_deger_ara(gecerli_dizi_say,alan):
                                alan-=1
                            gecerli_dizi_say.append(alan)
                            gecerli_dizi_hiyerarsi.append([Parent,k])
                            gecerli_dizi_u.append([nesne_orta_nokta_x,nesne_orta_nokta_y,nesne_genislik,nesne_yukseklik])
                            gecerli_dizi_data.append([int(sonuc),int(ebob(nesne_yukseklik,nesne_genislik)*100)])
                            cv2.putText(roi, "%"+ str(sonuc) + "e - %"+ str(int(ebob(nesne_yukseklik,nesne_genislik)*100)) + "c", (nesne_orta_nokta_x,nesne_orta_nokta_y), cv2.FONT_HERSHEY_SIMPLEX,0.5, (255,0,0), 1, cv2.LINE_AA)
                            cv2.ellipse(roi, (nesne_orta_nokta_x,nesne_orta_nokta_y), (nesne_genislik,nesne_yukseklik), 270+angle_rect, 0, 360, (255,0,0), 2)
                        else:
                            h_kaideli_dizi.append(contours[k])
                            h_kaideli_dizi_orta_nokta.append([nesne_orta_nokta_x, nesne_orta_nokta_y])
                            while True == dizide_deger_ara(h_kaideli_dizi_alan,alan):
                                alan-=1
                            h_kaideli_dizi_alan.append(alan)
                            h_kaideli_dizi_hiyerarsi.append([Parent,k])
            else:           
                pass

    mutemadiyen_dizi=[]
    malef = []

    rakunkee = []
    for j in range(len(gecerli_dizi_hiyerarsi)):
        rakunkee.append(gecerli_dizi_hiyerarsi[j][0])

    for j in range(len(h_kaideli_dizi_hiyerarsi)):
        if False == dizide_deger_ara(rakunkee, h_kaideli_dizi_hiyerarsi[j][0]):
            kaideli_dizi.append(h_kaideli_dizi[j])
            kaideli_dizi_hiyerarsi.append(h_kaideli_dizi_hiyerarsi[j])
            kaideli_dizi_orta_nokta.append(h_kaideli_dizi_orta_nokta[j])
            kaideli_dizi_alan.append(h_kaideli_dizi_alan[j])

    for h in range(1,len(kaideli_dizi_alan)+1):
        aradigimiz_indis = None
        en_buyuk_alanli_indis = listede_deger_arama(kaideli_dizi_alan,-h)
        ana_govde_x, ana_govde_y = kaideli_dizi_orta_nokta[en_buyuk_alanli_indis][0],kaideli_dizi_orta_nokta[en_buyuk_alanli_indis][1]
        degerli_sonuc = uzun_olan(resim_yukseklik, resim_genislik)
        for r in range(len(kaideli_dizi_orta_nokta)):
            if r != en_buyuk_alanli_indis:
                secilen_govde_x,secilen_govde_y = kaideli_dizi_orta_nokta[r][0],kaideli_dizi_orta_nokta[r][1]
                cikti = uzaklik_hesaplayici(ana_govde_x, ana_govde_y, secilen_govde_x,secilen_govde_y)
                if cikti < degerli_sonuc and kaideli_dizi_hiyerarsi[r][0] == kaideli_dizi_hiyerarsi[en_buyuk_alanli_indis][0]:
                    degerli_sonuc = cikti
                    aradigimiz_indis = r
        if aradigimiz_indis is not None:
            if False == dizide_deger_arama(malef,en_buyuk_alanli_indis,aradigimiz_indis):
                malef.append(en_buyuk_alanli_indis)
                malef.append(aradigimiz_indis)
                mutemadiyen_dizi.append([en_buyuk_alanli_indis,aradigimiz_indis])

    for keyfe in mutemadiyen_dizi:
        yeni_ctr = np.concatenate((kaideli_dizi[keyfe[0]], kaideli_dizi[keyfe[1]]), axis=0)
        nesne_yukseklik, nesne_genislik, angle_rect, nesne_orta_nokta_x, nesne_orta_nokta_y, bnd_x, bnd_y, bnd_w, bnd_h, nesne_box, rect = size_data(yeni_ctr)
        if nesne_genislik > ust_sinir and nesne_yukseklik > ust_sinir:
            contourse = kontur_kucult(yeni_ctr, ust_sinir,nesne_genislik,nesne_yukseklik)
            nesne_yukseklik_of, nesne_genislik_of, angle_rect_of, nesne_orta_nokta_x_of, nesne_orta_nokta_y_of, bnd_x_of, bnd_y_of, bnd_w_of, bnd_h_of, nesne_box_of, rect_of = size_data(contourse)
            sonuc = drawing_ellipse(nesne_orta_nokta_x_of, nesne_orta_nokta_y_of, angle_rect_of,nesne_yukseklik_of, nesne_genislik_of,contourse)
        else:
            contourse = np.vstack(list(set(tuple(row[0]) for row in yeni_ctr)))
            sonuc = drawing_ellipse(nesne_orta_nokta_x, nesne_orta_nokta_y, angle_rect,nesne_yukseklik, nesne_genislik,contourse)
        if sonuc > 55:
            cv2.putText(roi, "%"+ str(sonuc) + "e - %"+ str(int(ebob(nesne_yukseklik,nesne_genislik)*100)) + "c", (nesne_orta_nokta_x,nesne_orta_nokta_y), cv2.FONT_HERSHEY_SIMPLEX,0.5, (255,0,0), 1, cv2.LINE_AA)
            cv2.ellipse(roi, (nesne_orta_nokta_x,nesne_orta_nokta_y), (nesne_genislik,nesne_yukseklik), 270+angle_rect, 0, 360, (255,0,0), 2)
            sonuc_sayisi += 1                       
            gecerli_dizi.append(yeni_ctr)
            alan = nesne_genislik * nesne_yukseklik
            while True == dizide_deger_ara(gecerli_dizi_say,alan):
                alan-=1
            gecerli_dizi_say.append(alan)
            gecerli_dizi_hiyerarsi.append([Parent,k])
            gecerli_dizi_u.append([nesne_orta_nokta_x,nesne_orta_nokta_y,nesne_genislik,nesne_yukseklik])
            gecerli_dizi_data.append([int(sonuc),int(ebob(nesne_yukseklik,nesne_genislik)*100)]) 
        else:
            pass
    
    gruplama_gecerli_dizi = []
    gruplama_gecerli_dizi_say = []
    gruplama_gecerli_dizi_hiyerarsi = []
    gruplama_gecerli_dizi_data = []
    gruplama_gecerli_dizi_u = []
    
    ellallah = []

    if len(gecerli_dizi) > 0:
        for i in range(len(gecerli_dizi)):
            a_x, a_y, a_w, a_h = gecerli_dizi_u[i][0],gecerli_dizi_u[i][1],gecerli_dizi_u[i][2],gecerli_dizi_u[i][3]
            a,g,u,n,e = [],[],[],[],[]
            for l in range(len(gecerli_dizi)):
                b_x, b_y, b_w, b_h = gecerli_dizi_u[l][0],gecerli_dizi_u[l][1],gecerli_dizi_u[l][2],gecerli_dizi_u[l][3]
                if b_x - b_w < a_x < b_x + b_w and a_x - a_w < b_x < a_x + a_w and False == dizide_deger_ara(ellallah,l): #or da eklenebilir
                    ellallah.append(gecerli_dizi_say[l])
                    a.append(gecerli_dizi[l])
                    g.append(gecerli_dizi_say[l])
                    u.append(gecerli_dizi_hiyerarsi[l])
                    n.append(gecerli_dizi_data[l])
                    e.append(gecerli_dizi_u[l])
                    
            if False == dizi_kiyaslama(gruplama_gecerli_dizi_say, g):
                gruplama_gecerli_dizi.append(a)
                gruplama_gecerli_dizi_say.append(g)
                gruplama_gecerli_dizi_hiyerarsi.append(u)
                gruplama_gecerli_dizi_data.append(n)
                gruplama_gecerli_dizi_u.append(e)

    hedef_ctr = []
    odak = None

    if len(gruplama_gecerli_dizi) > 0:
        aranan_grup_i = 0
        ebci = listede_deger_arama_2d(gecerli_dizi_u, -1, 3)
        for i in range(len(gruplama_gecerli_dizi_u)):
            for e in range(len(gruplama_gecerli_dizi_u[i])):
                if gruplama_gecerli_dizi_u[i][e][3] == gecerli_dizi_u[ebci][3]:
                    aranan_grup_i = i
                    
        enci = listede_deger_arama_2d(gruplama_gecerli_dizi_u[aranan_grup_i], -1, 1)
        for e in range(len(gruplama_gecerli_dizi_u[aranan_grup_i])):
            if e == enci:
                hedef_ctr = gruplama_gecerli_dizi[aranan_grup_i][e]        
                es = e

        actr = hedef_ctr
        nesne_yukseklik, nesne_genislik, angle_rect, nesne_orta_nokta_x, nesne_orta_nokta_y, bnd_x, bnd_y, bnd_w, bnd_h, nesne_box, rect = size_data(actr)
        cv2.ellipse(roi, (nesne_orta_nokta_x,nesne_orta_nokta_y), (nesne_genislik,nesne_yukseklik), 270+angle_rect, 0, 360, (0,0,255), 3)
        cv2.putText(roi, "%"+ str(gruplama_gecerli_dizi_data[aranan_grup_i][es][0]) + "e - %"+ str(gruplama_gecerli_dizi_data[aranan_grup_i][es][1]) + "c", (nesne_orta_nokta_x,nesne_orta_nokta_y), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0,0,255), 1, cv2.LINE_AA)
        odak = nesne_orta_nokta_x, nesne_orta_nokta_y,bnd_w, bnd_h,nesne_yukseklik, nesne_genislik, gruplama_gecerli_dizi_data[aranan_grup_i][es][0],gruplama_gecerli_dizi_data[aranan_grup_i][es][1]
    elif len(contours) > 0:
        fctr = max(contours, key=cv2.contourArea)
        nesne_yukseklik, nesne_genislik, angle_rect, nesne_orta_nokta_x, nesne_orta_nokta_y, bnd_x, bnd_y, bnd_w, bnd_h, nesne_box, rect = size_data(fctr)
        if nesne_genislik > resim_genislik*0.01 and nesne_yukseklik > resim_yukseklik*0.01:
            cv2.rectangle(roi, (bnd_x,bnd_y), (bnd_x + bnd_w,bnd_y+bnd_h), (255,0,0), 2)
            odak = nesne_orta_nokta_x, nesne_orta_nokta_y,bnd_w, bnd_h,nesne_yukseklik, nesne_genislik, 0,0

    return roi,sonuc_sayisi,goruntu_tarandi, odak

def drawing_ellipse(nesne_orta_nokta_x, nesne_orta_nokta_y, angle_rect,nesne_yukseklik, nesne_genislik,ctr):
    cizilen_elips_tam = []
    angle = radians(180-angle_rect)
    kabulx = int(nesne_genislik*0.07)
    kabuly = int(nesne_yukseklik*0.07)
    if kabulx < 3:
        kabulx=3
    if kabuly < 3:
        kabuly=3
    steps_jump = int(kabulx/3)
    if(steps_jump > 1):
        pass
    else:
        steps_jump = 1
    steps = int(360 * ((uzun_olan(nesne_genislik, nesne_yukseklik)/57)))
    
    for t in range(steps):
        x_orj = int(nesne_genislik * cos(2 * pi * t/steps))
        y_orj = int(nesne_yukseklik * sin(2 * pi * t/steps))
        y = int(x_orj*cos(angle) - y_orj*sin(angle))
        x = int(x_orj*sin(angle) + y_orj*cos(angle))
        cizilen_elips_tam.append([x,y])
    cizilen_elips_tam_plus = np.vstack(list(set(tuple(row) for row in cizilen_elips_tam)))
    veriler = nesne_orta_nokta_x, nesne_orta_nokta_y,cizilen_elips_tam_plus,kabulx,kabuly
    sonuc = hesaplama(ctr,veriler)
    return sonuc

def hesaplama(ctr,veriler):
    sayac = 0
    nesne_orta_nokta_x, nesne_orta_nokta_y,cizilen_elips_tam,kabulx,kabuly = veriler
    for a in ctr:
        x,y = a[0],a[1]
        dogruluk = True
        for i in cizilen_elips_tam:
            if dogruluk == True and nesne_orta_nokta_x+kabulx > x+i[0] > nesne_orta_nokta_x-kabulx and nesne_orta_nokta_y+kabuly > y+i[1] > nesne_orta_nokta_y-kabuly:
                sayac += 1
                dogruluk = False
    return int((sayac/len(ctr))*100)

def nesneye_kalibre(cam_orta_nokta_x, cam_orta_nokta_y, odak,roi):
    nesne_orta_nokta_x, nesne_orta_nokta_y,bnd_w, bnd_h,nesne_yukseklik, nesne_genislik, sonuci, orani = odak
    motor_hareket = None,None,None,None,None,None,None #hedef isabetlendi, motor1,motor2,motor3,motor4,motor5,motor6
    uzaklikx = -(cam_orta_nokta_x - nesne_orta_nokta_x)
    uzakliky = cam_orta_nokta_y - nesne_orta_nokta_y
    ar, ra, _= roi.shape
    h = None
    cv2.putText(roi, "X:" + str(uzaklikx) + " Y:" + str(uzakliky), (cam_orta_nokta_x,cam_orta_nokta_y), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0,0,0), 1, cv2.LINE_AA)
    if orani > 80:
        if bnd_w < 200 and bnd_h < 200:
            pt1 = (nesne_orta_nokta_x-100,nesne_orta_nokta_y-100)
            pt2 = (nesne_orta_nokta_x+100,nesne_orta_nokta_y+100)
        else:
            pt1 = (int(nesne_orta_nokta_x-(15 + bnd_w*0.1)),int(nesne_orta_nokta_y-(15 + bnd_h*0.1)))
            pt2 = (int(nesne_orta_nokta_x+(15 + bnd_w*0.1)),int(nesne_orta_nokta_y+(15 + bnd_h*0.1)))
        cv2.rectangle(roi, pt1,pt2,(255,0,0), 2)
        motor_hareket = "git",100,0,100,100,0,100
    elif nesne_orta_nokta_x+nesne_genislik > cam_orta_nokta_x > nesne_orta_nokta_x-nesne_genislik and nesne_orta_nokta_y+nesne_yukseklik > cam_orta_nokta_y > nesne_orta_nokta_y-nesne_yukseklik:
        #kendi etrafında milimlik hareket
        if uzaklikx > 0:
            h = 100
        elif uzaklikx < 0:
            h = -100
        elif uzaklikx == 0:
            h = 0

        if uzakliky > 0:
            j = -100 # yukari çıkar
        elif uzakliky < 0:
            j = 100 # aşaği iner
        elif uzakliky == 0:
            j = 0 # hiçbirşey yapmaz
        motor_hareket = "gitme", h,j,h,h,j,h
    else: #yandan hareket
        if uzaklikx > 0:
            h = 100
        elif uzaklikx < 0:
            h = -100
        elif uzaklikx == 0:
            h = 0

        if uzakliky > 0:
            j = -100 # yukari çıkar
        elif uzakliky < 0:
            j = 100 # aşaği iner
        elif uzakliky == 0:
            j = 0 # hiçbirşey yapmaz
        motor_hareket = "gitme", h,j,h,-h,j,-h
    return uzaklikx, uzakliky, roi, motor_hareket

def size_data(ctr):
    rect = cv2.minAreaRect(ctr)
    nesne_yukseklik, nesne_genislik = int(rect[1][0]/2),int(rect[1][1]/2)
    angle_rect = int(rect[2])
    nesne_orta_nokta_x, nesne_orta_nokta_y = int(rect[0][0]),int(rect[0][1])
    (bnd_x, bnd_y, bnd_w, bnd_h) = cv2.boundingRect(ctr)
    box = cv2.boxPoints(rect)
    nesne_box = np.int0(box)
    return nesne_yukseklik,nesne_genislik,angle_rect,nesne_orta_nokta_x,nesne_orta_nokta_y,bnd_x,bnd_y,bnd_w,bnd_h,nesne_box, rect

def kamera_xy_cizgi(ior):
    resim_yukseklik,resim_genislik,_ = ior.shape
    for i in range(0, resim_yukseklik ):
        ior[i, int(resim_genislik/2)] = [0,150,150]
    for i in range(0, resim_genislik ):
        ior[int(resim_yukseklik/2), i] = [0,150,150]
    return ior

def uzaklik_hesaplayici(ana_govde_x, ana_govde_y, secilen_govde_x,secilen_govde_y):
    return sqrt(pow((ana_govde_x-secilen_govde_x),2) + pow((ana_govde_y-secilen_govde_y),2))

def ebob(i,k):
    if i >= k:
        return k/i
    else:
        return i/k

def uzun_olan(k,l):
    if k > l:
        return k
    else:
        return l

def kisa_olan(k,l):
    if k > l:
        return l
    else:
        return k

def listede_deger_arama(listem,a):
    furtem = sorted(listem)
    aranandeger = furtem[a]
    arananindis = None
    for i in range(len(listem)):
        if aranandeger == listem[i]:
            arananindis = i
    return arananindis

def listede_deger_arama_2d(listem,a,b):
    muntestem = []
    for i in range(len(listem)):
        muntestem.append(listem[i][b])
    furtem = sorted(muntestem)
    aranandeger = furtem[a]
    arananindis = None
    for i in range(len(listem)):
        if aranandeger == listem[i][b]:
            arananindis = i
            break
    if arananindis is not None:
        return arananindis

def fps_func(prev_frame_time,new_frame_time):
    new_frame_time = time.time()
    fps = 1/(new_frame_time-prev_frame_time)
    prev_frame_time = new_frame_time
    fps = str(int(fps))
    return fps, prev_frame_time, new_frame_time

def dizide_deger_arama(listem,a,b):
    buul = False
    for i in listem:
        if a == i or b == i:
            buul = True
    return buul

def dizide_deger_ara(listem,a):
    buul = False
    for i in listem:
        if a == i:
            buul = True
    return buul

def dizi_kiyaslama(listust,listalt):
    buul = False
    for i in listust:
        for u in i:
            for h in listalt:
                if h == u:
                    buul = True
    return buul

def kontur_kucult(kontur, ust, nesne_genislik,nesne_yukseklik):
    M = cv2.moments(kontur)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    cnt_norm = kontur - [cx, cy]
    scaled = ((100 / (uzun_olan(nesne_genislik,nesne_yukseklik)/ust))/100)
    cnt_scaled = cnt_norm * scaled
    cnt_scaled = cnt_scaled + [cx, cy]
    cnt_scaled = cnt_scaled.astype(np.int32)
    data = np.vstack(list(set(tuple(row[0]) for row in cnt_scaled)))
    return data