import sys
import subprocess
import argparse

# 国内常用镜像源映射表
MIRRORS = {
    "tsinghua": "https://pypi.tuna.tsinghua.edu.cn/simple",
    "aliyun": "https://mirrors.aliyun.com/pypi/simple",
    "tencent": "https://mirrors.cloud.tencent.com/pypi/simple",
    "douban": "https://pypi.doubanio.com/simple",
}

def run_pip():
    # 1. 预处理参数：提取我们的自定义参数 -s
    # 我们需要手动分离，因为 pip 本身也有很多参数，直接用 argparse 会冲突
    raw_args = sys.argv[1:]
    
    selected_mirror = MIRRORS["tsinghua"] # 默认源
    pip_args = []
    
    # 简单的参数提取逻辑
    skip_next = False
    for i, arg in enumerate(raw_args):
        if skip_next:
            skip_next = False
            continue
        if arg == "-s" and i + 1 < len(raw_args):
            alias = raw_args[i+1]
            if alias in MIRRORS:
                selected_mirror = MIRRORS[alias]
            else:
                print(f"⚠️  未找到镜像源 '{alias}' (可用源: {', '.join(MIRRORS.keys())})，将使用默认清华源。")
            skip_next = True
        else:
            pip_args.append(arg)

    if not pip_args:
        subprocess.run([sys.executable, "-m", "pip"])
        return

    # 2. 构造命令
    new_command = [sys.executable, "-m", "pip"]
    
    # 只有这些命令需要注入镜像源
    if pip_args[0] in ["install", "download", "wheel"]:
        command = pip_args[0]
        remaining = pip_args[1:]
        # 注入镜像源参数
        new_command.extend([command, "-i", selected_mirror])
        new_command.extend(remaining)
    else:
        new_command.extend(pip_args)

    # 3. 执行
    try:
        # print(f"🚀 正在使用镜像源: {selected_mirror}")
        subprocess.run(new_command, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == "__main__":
    run_pip()