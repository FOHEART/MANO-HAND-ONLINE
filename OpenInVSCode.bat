@echo off
rem 切换到脚本所在目录，确保无论从哪里双击都打开正确的文件夹
cd /d "%~dp0"

rem 调用 VS Code 打开当前文件夹
code .

rem 脚本执行完毕，关闭命令行窗口
exit
