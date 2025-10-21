#!/usr/bin/env python3
"""
Web应用启动脚本

快速启动短视频生成Web应用
"""

import os
import sys

def check_dependencies():
    """检查依赖是否已安装"""
    try:
        import flask
        import moviepy
        import PIL
        print("✓ 核心依赖已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("\n请先安装依赖:")
        print("  pip install -r requirements.txt\n")
        return False

def check_ffmpeg():
    """检查FFmpeg是否已安装"""
    import subprocess
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✓ FFmpeg已安装")
            return True
        else:
            print("✗ FFmpeg未正确安装")
            return False
    except FileNotFoundError:
        print("✗ 未找到FFmpeg")
        print("\n请安装FFmpeg:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: 从 https://ffmpeg.org/download.html 下载\n")
        return False
    except Exception as e:
        print(f"检查FFmpeg时出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("  AI短视频生成工具 - Web应用")
    print("=" * 60)
    print()

    # 检查依赖
    print("检查系统环境...")
    deps_ok = check_dependencies()
    ffmpeg_ok = check_ffmpeg()

    if not deps_ok:
        print("\n⚠️  请先安装Python依赖")
        sys.exit(1)

    if not ffmpeg_ok:
        print("\n⚠️  警告: FFmpeg未安装，视频生成可能失败")
        response = input("是否继续启动? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)

    print("\n" + "=" * 60)
    print("启动Web应用...")
    print("=" * 60)
    print()

    # 提示用户
    print("📝 提示:")
    print("  - 应用将在 http://localhost:5000 启动")
    print("  - 在浏览器中打开该地址即可使用")
    print("  - 按 Ctrl+C 停止应用")
    print()

    # 检查是否设置了AI API密钥
    if os.environ.get('OPENAI_API_KEY'):
        print("✓ 检测到OpenAI API密钥，将启用AI功能")
    else:
        print("ℹ️  未设置OPENAI_API_KEY，将使用基于规则的分析")
        print("   如需AI功能，请设置环境变量: export OPENAI_API_KEY='your-key'")

    print()
    print("=" * 60)
    print()

    # 导入并运行应用
    try:
        from web_app.app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n应用已停止")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
