server:193.112.45.216:5000
服务开启：
cd home/sailfish/
sudo su
source env3.5/bin/activate
cd work
python server.py
服务关闭：
sudo lsof -i:5000
获得端口为5000的python id
sudo kill -9 ID
关闭对应id的python程序
download:图片下载
如下载名为2018-12-13-09-44-13-dd.png的图片:
http://193.112.45.216:5000/download/2018-12-13-09-44-13-dd.png
list查看服务器中已保存的图片:
如:http://193.112.45.216:5000/list/
upload:上传图片
对比后的文件存储在home/sailfish/work/uploads/result