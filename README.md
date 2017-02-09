# Breezes
Breezes:  Multi Center and Multi Version Docker Registry Management UI.


## LICENSE
MIT


## Environment
> 1. Python Version: 2.7
> 2. Web Framework: Flask, Flask-RESTful
> 3. Required Modules: requirements.txt


## Usage

```
1. Requirement:
    1.0 yum install -y gcc gcc-c++ python-devel
    1.1 pip install -r requirements.txt
    
2. modify config.py or add environment variables(os.getenv key in the reference configuration item):

3. run:
    3.1 python main.py        #development
    3.2 sh Control.sh         #production
    3.3 python -O Product.py  #production
    3.4 python super_debug.py #Performance optimization

4. Access it for IP:10210
```


## Usage for Docker

```
   docker build -t breezes .
   docker run -tdi --name breezes --net=host --always=restart breezes
   ps aux|grep Breezes //watch the process
```


## UI
![registries][1]
![images][2]


## Release Note

### v0.1
```
1. 管理多私有仓，V1、V2版本皆可
2. Docker Registry私有仓V1、V2查询(所有镜像查询、镜像某一标签详细数据查询,自识别V1、V2版本)
3. V1删除镜像和标签
4. HTTP RESTFul API支持对V1、V2查询和V1删除操作
```


  [1]: ./misc/registries.png
  [2]: ./misc/images.png