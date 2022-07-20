# underwater yellow circle detect

![](https://raw.githubusercontent.com/hasanfirat/circle_detect/main/magi.jpg)

##required
- Python
- Numpy library
- OpenCV library

for Windows
<br>
`pip install opencv-python`
<br>
`pip install numpy`

yükseklik(b) ve genişliği(a) bilinen orta noktası (h,k) olan bir elipsin çizimi;

x = h + ( a*cos⁡(2π t/360)  )  
y = k + ( b*sin⁡(2π t/360)  )
t=0→t=2π
	A(x,y) noktasının orjine göre α derece açıyla yer değiştirmesi:
			Rα(A) = (x.cosα- y.sinα ,x.sinα+ y.cosα)
      
##input
![](https://github.com/hasanfirat/underwater_yellow_circle_detect/blob/main/balthasar/u.png)

##output
![](https://github.com/hasanfirat/underwater_yellow_circle_detect/blob/main/balthasar/cikti.png)
