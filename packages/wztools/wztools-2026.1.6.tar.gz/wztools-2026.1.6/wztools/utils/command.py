import logging
import subprocess
import threading

from typing import Tuple, Optional, List


def run_cmd(
    cmd: str,
    cwd: Optional[str] = None,
    shell: bool = True,
    text: bool = True,
    timeout: Optional[int] = None,
    stop_keywords: Optional[List[str]] = None,
    logger = None
) -> Tuple[int, str, str]:
    """
    执行命令行命令并实时返回结果
    
    参数:
        cmd: 要执行的命令字符串
        cwd: 命令执行的工作目录(文件夹路径),None表示当前目录
        shell: 是否通过shell执行命令
        text: 是否以文本模式返回输出(否则返回bytes)
        timeout: 命令执行超时时间(秒)
        stop_keywords: 关键词列表,检测到任一关键词时立即停止命令
    
    返回:
        (返回码, 标准输出, 标准错误)
    """
    if logger is None:
        logger = logging.getLogger()

    logger.info(f"开始执行命令: {cmd}")
    if cwd:
        logger.info(f"工作目录: {cwd}")
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=text,
            bufsize=1,  # 行缓冲,实时输出
            universal_newlines=text
        )
        
        stdout_lines = []
        stderr_lines = []
        stopped_by_keyword = None
        
        def read_stream(stream, lines, is_stderr=False):
            """实时读取流并记录到logger"""
            nonlocal stopped_by_keyword
            try:
                for line in iter(stream.readline, '' if text else b''):
                    if not line:
                        break
                    
                    # 去除末尾换行符
                    line_stripped = line.rstrip('\n\r') if text else line.rstrip(b'\n\r')
                    
                    # 累积输出
                    lines.append(line)
                    
                    # 实时记录到logger
                    if is_stderr:
                        logger.warning(line_stripped)
                    else:
                        logger.info(line_stripped)
                    
                    # 检查关键词
                    if stop_keywords:
                        line_str = line if text else line.decode('utf-8', errors='ignore')
                        for keyword in stop_keywords:
                            if keyword in line_str:
                                stopped_by_keyword = keyword
                                logger.warning(f"检测到关键词 '{keyword}',终止命令执行")
                                process.terminate()
                                return
            except Exception as e:
                logger.error(f"读取流时出错: {e}")
        
        # 创建线程读取stdout和stderr
        stdout_thread = threading.Thread(
            target=read_stream, 
            args=(process.stdout, stdout_lines, False),
            daemon=True
        )
        stderr_thread = threading.Thread(
            target=read_stream, 
            args=(process.stderr, stderr_lines, True),
            daemon=True
        )
        
        stdout_thread.start()
        stderr_thread.start()
        
        # 等待进程结束或超时
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            logger.error(f"命令执行超时 (>{timeout}秒),强制终止")
            process.kill()
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)
            stdout = ''.join(stdout_lines) if text else b''.join(stdout_lines)
            stderr = ''.join(stderr_lines) if text else b''.join(stderr_lines)
            return -1, stdout, stderr # type: ignore
        
        # 等待线程完成
        stdout_thread.join()
        stderr_thread.join()
        
        # 组合输出
        stdout = ''.join(stdout_lines) if text else b''.join(stdout_lines)
        stderr = ''.join(stderr_lines) if text else b''.join(stderr_lines)
        
        # 记录结果
        if stopped_by_keyword:
            logger.warning(f"命令因关键词 '{stopped_by_keyword}' 被终止")
            return -2, stdout, stderr # type: ignore
        
        logger.info(f"命令执行完成,返回码: {process.returncode}")
        return process.returncode, stdout, stderr # type: ignore
    
    except Exception as e:
        logger.error(f"执行命令时出错: {str(e)}")
        return -1, "", f"执行出错: {str(e)}"