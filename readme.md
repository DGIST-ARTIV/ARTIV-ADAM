# 차량 운행 기록계 ADMS (ver. 6.0.3)

* 센서로부터 발행되는 ros massage로 steer 값, 주행 속도, 엑셀 값 등 차량 주행 상태를 실시간으로 시각적으로 확인할 수 있습니다.   
* 카메라, LiDAR, GPS 등 각 센서별로 주행 시나리오를 숏컷으로 테스트할 수 있습니다.   
* 차량 운행을 rosbag 파일로 녹화하여 기록할 수 있습니다.
* 시스템 로그, CAN통신과 UI 간 딜레이도 확인하여 돌발 상황에 즉각적인 대처가 가능합니다.

## Environment
### Software
* Ubuntu 18.04 LTS
* Python 3.6
* ROS2 dashing
* Qt
### Hardware
* Jetson

## How to Run
```python
$ . /opt/ros/dashing/setup.bash  # ros2
$ python3 adam.py
```
다음과 같이 login 창이 팝업된다. '093'과 같이 DB에 등록된 키를 입력하면 로그인이 가능하다.
![login](https://github.com/DGIST-ARTIV/ARTIV-ADAM/assets/48004826/79fd081c-b79c-405e-af09-a5def2815568)

## UI
![adms_play](https://github.com/DGIST-ARTIV/ARTIV-ADAM/assets/48004826/9661c71f-14d8-46dd-9e60-7925db403846)  
업데이트는 약 66fps 로 이뤄진다.

### 수집 정보
* 원하는 노드 토픽을 선택적으로 rosbag 파일로 기록할 수 있다.
* Reload를 누르면 현재 토픽들이 나옴? test
* rosbag 저장위치를 설정하지 않으면 `/Desktop/ADMSrosbag`에 저장된다. (admsv6) 파일 이름은 '로그인 id + 기록 시작 시간'이다.

### 차량 정보
기어, Steer, 브레이크 값 등 차량 주행 상태를 실시간으로 시각화합니다.

### Delay Check
CAN통신과 UI 업데이트 사이 delay를 확인할 수 있습니다. Delay가 1초 이상일 경우 경고 텍스트를 띄워 빠른 대응이 가능하도록 했다.

### System Log
ROS 로그를 확인할 수 있습니다. FATAL 레벨의 로그 발생 시 시각적 및 청각적으로 알려 빠른 대응이 가능하도록 했다.

### 주행 시나리오 숏컷 커스터마이징
ADMS는 주행 시나리오를 간단하게 테스트 할 수 있는 숏컷을 자유로이 추가/변경/제거할 수 있는 기능을 제공한다.주행 시나리오를 subprocess에서 셀 명령어로 실행시켜 테스트 할 수 있다.
1. 추가하는 법
좌측하단의 Add 버튼을 누르면 추가하고자 하는 주행 시나리오를 작성할 수 있는 창이 팝업됩니다. 각 카테고리 별로 최대 15개까지 추가할 수 있다.
* Category : 추가할 주행 시나리오가 어느 센서 및 파트와 관련되어 있는지 설정
* Switch Name : UI 상에 나타날 스위치 이름
* Command : 스위치 활성화 시 생성될 자식 프로세스에서 실행할 셀 명령어
* Workspace : Build 옵션 설정.
* Environment : 시나리오 실행 이전에, ROS1, ROS2, 혹은 커스텀 환경(`sh`)이 필요할 경우 설정
* Dependencies : roscore, ROSbridge 중 필요하면 설정

1-1. 프로그램을 재실행해도 남아있는 스위치 추가하는 법
최초 실행 시 root에 "ADMS_switch_list.txt" 파일이 생성된다. Category, Swtich Name, Command, Workspace, Environment, Dependencies를 "|"로 구분하여 차례대로 작성하면 된다. 각 버튼은 줄띄우기("\n")로 구분하여 생성된다.
* 복수개의 environment, dependencies 를 사용하고 싶다면 "&"를 사이에 추가하여 작성하면 된다.
ex)  
```
Vision|bridge w/out core| ||ROS1&ROS2&|ROSbridge
Vision|roscore| ||ROS1&|roscore&
LIDAR|usb_cam2|ros2 run usb_camera_driver2 usb_camera_driver_node2|~/colcon_ws/install/setup.bash|ROS2&|roscore&ROSbridge
```

2. 실행
생성한 스위치의 버튼을 클릭하면 해당 스위치에 등록한 Command가 실행이 된다. 다시 클릭하면 해당 스위치의 command를 실행하는 자식 프로세스가 중단된다.(`SIGINT`) ROScore 및 ROSbridge 는 이들을 사용하는 프로세스가 존재하지 않을 경우 자동으로 꺼진다.

3. 제거하는 법
스위치를 선택한 후 Delete 를 누르면, "ADMS_switch_list.txt" 파일에서도 제거된다. 동시에 여러 개를 제거할 수 있다.

### Light mode / Dark mode
Light / Dark 모드 UI를 제공한다.
