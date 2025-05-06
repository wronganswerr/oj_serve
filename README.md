fastapi WEB架构
# 需要的服务
1. rabbitmq 远程主机运行
2. mysql 本地服务
3. mongodb 本地服务

# mysql 本地部署流程
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql

mysql -u root -p localhost

CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON database_name.* TO 'newuser'@'localhost';

CREATE DATABASE 数据库名;

sudo apt-get install phpmyadmin 安装 phpmyadmin

GRANT ALL PRIVILEGES ON `phpmyadmin`.* TO 'phpmyadmin'@'localhost' IDENTIFIED BY 'your_phpmyadmin_password';
FLUSH PRIVILEGES;


# mongodb 本地部署流程
参考官方文档
https://www.mongodb.com/zh-cn/docs/manual/tutorial/install-mongodb-on-ubuntu/#overview

