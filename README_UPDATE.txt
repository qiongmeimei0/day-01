day-01 修复文件

使用方法：
1. 解压本压缩包。
2. 将其中所有文件上传到 GitHub 仓库根目录。
3. GitHub 提示同名文件时选择覆盖。
4. 复制 .env.example 为 .env，并填写需要的配置。
5. 默认 LIVE_TRADING=false，只进行模拟交易，不会真实下单。

运行命令：
pip install -r requirements.txt
python bot.py

重要：不要把包含 API 密钥的 .env 上传到 GitHub。
