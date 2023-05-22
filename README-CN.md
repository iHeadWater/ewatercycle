# eWaterCycle开发者中文使用说明
eWaterCycle软件包目前只有英文版，为了方便大家在水文模型中使用eWaterCycle软件包，特写此文档eWaterCycle软件包中文使用说明。主要内容如下：
## 目录
- [前言](#前言)
- [系统安装](#1系统安装)
  - [环境配置](#1、环境配置)
  - [era5cli工具安装](#2、era5cli工具安装)
  - [ESMValTool配置](#3、ESMValTool配置)
  - [容器安装与配置](#4、容器安装与配置)
  - [eWaterCycle包安装](#5、eWaterCycle包安装)
  - [eWaterCycle配置](#6、eWaterCycle配置)
- [eWaterCycle模型的运行](#2eWaterCycle模型的运行)
## 前言
1. 电脑需要Linux系统，如无Linux系统，推荐安装WSL，步骤可参考[Install Ubuntu on WSL2 and get started with graphical applications](https://ubuntu.com/tutorials/install-ubuntu-on-wsl2-on-windows-11-with-gui-support)
（1）安装WSL，以管理员身份打开cmd并运行：wsl --install
（2）在Powershell终端中运行：wsl --list --online，查看所有可用的发行版
（3）可以通过运行以下命令安装发行版：wsl --install -d Ubuntu-22.04
（4）配置Ubuntu：sudo apt update，然后：sudo apt full-upgrade，出现提示时按 Y。
2. 在Ubuntu中安装conda。
3. VSCode连接UBuntu。

##  系统安装
注意：在进行系统安装时，将前言的步骤完成，以免影响此步操作。若使用eWaterCycle软件包，您需要进行eWaterCycle模型的配置与数据集的下载。可参考[ ewatercycle’s documentation](https://ewatercycle.readthedocs.io/en/latest)

### 1、环境配置
ewatercycle包需要一些地理空间非python包来生成强制数据。最好创建一个conda环境：
```Bash
wget https://raw.githubusercontent.com/eWaterCycle/ewatercycle/main/environment.yml
conda install mamba -n base -c conda-forge -y
mamba env create --file environment.yml
conda activate ewatercycle
```
### 2、era5cli工具安装
用于下载ERA5 数据文件。
```Bash
pip install era5cli
```
### 3、ESMValTool配置
用于从下载的气象数据生成模型需要的forcing，包括温度、降雨等。
```Bash
esmvaltool config get_config_user
```
### 4、容器安装与配置
在eWaterCycle中，模型是在容器中运行。推荐您安装Docker，容器安装完后，需对它进行配置，以支持在没有sudo的情况下调用容器。安装方法有：使用存储库apt安装、手动安装、使用脚本安装（用于测试和开发环境）。以下介绍使用存储库apt安装步骤：
#### （1）设置存储库
首次安装Docker之前，需要设置Docker存储库:
```Bash
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
```
添加 Docker 的官方 GPG 密钥:
```Bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```
使用以下命令设置存储库：
```Bash
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
#### (2) 安装Docker
更新包索引：
```Bash
sudo apt-get update
```
安装Docker最新版本:
```Bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
验证Docker是否安装成功：
```Bash
sudo docker run hello-world
```
#### (3) 没有sudo的情况下调用Docker容器
创建组:
```Bash
sudo groupadd docker
```
将您的用户添加到组中:
```Bash
sudo usermod -aG docker $USER
```
运行以下命令来激活对组的更改:
```Bash
newgrp docker
```
验证是否可以在没有sudo的情况下运行：
```Bash
docker run hello-world
```
#### (4) 配置Docker为使用systemd启动
要自动启动Docke，在引导时运行以下命令：
```Bash
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
```
若要停止此行为:
```Bash
sudo systemctl disable docker.service
sudo systemctl disable containerd.service
```
### 5、eWaterCycle包安装
（1）注意：不要运行pip install ewatercycle。此代码为ewatercycle的包，将代码git clone到项目文件夹下。（2）在项目文件夹下配置环境。在.vscode文件夹下添加launch.json文件与settings.json文件,在项目文件夹下添加.env文件，三个文件中的内容可参考[开源Python项目（四）--开发篇](https://dlut-water.yuque.com/kgo8gd/tnld77/nzfd52h3dbn0hllt)。
### 6、eWaterCycle配置
eWaterCycle是通过从配置文件中读取一些目录和设置来简化API实现数据准备、模型调用与运行。在Python环境中完成eWaterCycle配置文件的生成。
```Bash
#（1）依赖包引入
import logging
logging.basicConfig(level=logging.INFO)
import src.ewatercycle
import src.ewatercycle.parameter_sets
#（2）指定模型运行的容器类型
src.ewatercycle.CFG.container_engine  = 'docker' 
#（3）指定模型运行的的结果输出目录
src.ewatercycle.CFG.output_dir = '/home/wangjingyi/code/ewatercycle/scripts/output'
#（4）指定GRDC观测数据存储目录
src.ewatercycle.CFG.grdc_location = '/home/wangjingyi/code/ewatercycle/scripts/grdc-observations'
#（5）指定模型参数集存储位置
src.ewatercycle.CFG.parameterset_dir = '/home/wangjingyi/code/ewatercycle/scripts/parameter-sets'
#（6）指定模型配置文件存储位置
src.ewatercycle.CFG.ewatercycle_config = '/home/wangjingyi/code/ewatercycle/ewatercycle.yaml'
#（7）配置信息写入文件
src.ewatercycle.CFG.save_to_file('/home/wangjingyi/code/ewatercycle/ewatercycle.yaml')
#（8）在eWaterCycle中运行模型之前要读入配置文件
src.ewatercycle.CFG.load_from_file('/home/wangjingyi/code/ewatercycle/ewatercycle.yaml')
#（9）模型镜像导入容器(Terminal下) 
# 拉取一个即可，如果想要运行其他模型，可自行选择。
docker pull ewatercycle/marrmot-grpc4bmi:2020.11
#（10）模型参数集准备
# 下载示例参数集
src.ewatercycle.parameter_sets.download_example_parameter_sets()
cat ./ewatercycle.yaml #(Terminal下)
ewatercycle.parameter_sets.available_parameter_sets()
parameter_set = ewatercycle.parameter_sets.get_parameter_set('pcrglobwb_rhinemeuse_30min')
print(parameter_set)
#准备其他数据集
#准备标准输入文件 https://doi.org/10.5281/zenodo.1045339
cat ./ewatercycle.yaml#(Terminal下)
#（11）下载示例强制文件
#为了能够运行Marrmot示例，需要一个强制文件
cd docs/examples
wget https://github.com/wknoben/MARRMoT/raw/dev-docker-BMI/BMI/Config/BMI_testcase_m01_BuffaloRiver_TN_USA.mat
cd -
#（12）下载观测数据
# GRDC每日数据文件在 https://www.bafg.de/GRDC/EN/02_srvcs/21_tmsrs/riverdischarge_node.html。
# GRDC文件应存储在目录中：ewatercycle.CFG.grdc_location
```
##  eWaterCycle模型的运行
官方文档有五个模型的例子，可自行选择例子试运行，本文档主要介绍Marrmot M14模型的运行
```Bash
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import pandas as pd
import src.ewatercycle.analysis
import src.ewatercycle.parameter_sets
import src.ewatercycle.forcing
import src.ewatercycle.models
import src.ewatercycle.models.marrmot
import matplotlib.pyplot as plt

#下载强制数据
src.ewatercycle.CFG.load_from_file('/home/wangjingyi/code/ewatercycle/ewatercycle.yaml')
forcing = src.ewatercycle.forcing.load_foreign(
    "marrmot",
    directory="/home/wangjingyi/code/ewatercycle/docs/examples",
    start_time="1989-01-01T00:00:00Z",
    end_time="1992-12-31T00:00:00Z",
    forcing_info={"forcing_file": "BMI_testcase_m01_BuffaloRiver_TN_USA.mat"},
)
print(forcing)
#创建模型对象，需要选择一个版本
src.ewatercycle.models.marrmot.MarrmotM14.available_versions
model = src.ewatercycle.models.marrmot.MarrmotM14(version="2020.11", forcing=forcing)
#设置模型参数
cfg_file, cfg_dir = model.setup(
    maximum_soil_moisture_storage=12.0,
    end_time="1989-02-01T00:00:00Z",
)
print(cfg_file)
print(cfg_dir)
#模型初始化
model.initialize(cfg_file)
#获取模型变量名称
model.output_var_names
#模型运行
discharge = []
time_range = []
end_time = model.end_time
while model.time < end_time:
    model.update()
    discharge.append(model.get_value("flux_out_Q")[0])
    time_range.append(model.time_as_datetime.date())
    print(model.time_as_isostr)

simulated_discharge_df = pd.DataFrame({'simulated': discharge}, index=pd.to_datetime(time_range))
model.finalize()
#查看结果
simulated_discharge = pd.DataFrame(
    {"simulation": discharge}, index=pd.to_datetime(time_range)
)
plotsim = simulated_discharge.plot(figsize=(12, 8))
plt.savefig('/home/wangjingyi/code/ewatercycle/scripts/output/plotsim.jpg')
```
 ## 贡献者列表
欢迎大家积极贡献，这里是目前的贡献者：<https://github.com/iHeadWater/ewatercycle/graphs/contributors>
