from hero_base.state import State
from hero.util import log, function
import re
import asyncio
from typing import Tuple, Optional
import traceback
import os
import signal

async def shell_util(command: str, state: State, timeout: Optional[int] = None) -> Tuple[str, str]:
    command = re.sub(r"#.*\n?", "", command).strip()
    if not command:
        return "", ""

    log.debug(f"COMMAND: {command}")

    dir = state.working_dir
    command = f"cd {dir} && {command}"

    log.debug(f"FULL COMMAND: {command}")

    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            start_new_session=True,
        )

        # 创建任务来实时读取stdout和stderr
        async def read_stream(std_stream, prefix):
            output = []
            buffer = b""
            last_line = None
            while True:
                try:
                    chunk = await std_stream.read(1024)
                    if not chunk:
                        break

                    # Process the chunk byte by byte
                    for byte in chunk:
                        if byte == ord(b"\r"):
                            # Found a carriage return, this might be a tqdm update
                            if buffer:
                                line_str = buffer.decode(
                                    "utf-8", errors="replace"
                                )
                                if "%" in line_str or "it/s" in line_str:
                                    # This is likely a tqdm progress line
                                    clean_line = re.sub(
                                        r"\x1b\[[0-9;]*[a-zA-Z]",
                                        "",
                                        line_str,
                                    )
                                    clean_line = clean_line.strip()
                                    # Skip if it's just a progress indicator
                                    if re.match(
                                        r"^\s*[\d.]+\%|\d+/\d+|\d+it/s",
                                        clean_line,
                                    ):
                                        buffer = b""
                                        continue
                                    if last_line:
                                        output[-1] = clean_line
                                    else:
                                        output.append(clean_line)
                                    last_line = clean_line
                                else:
                                    # Regular line with carriage return
                                    line_str = line_str.strip()
                                    if line_str:
                                        output.append(line_str)
                                buffer = b""
                        elif byte == ord(b"\n"):
                            # Found a newline, process the buffer
                            if buffer:
                                line_str = buffer.decode(
                                    "utf-8", errors="replace"
                                ).strip()
                                if line_str:
                                    output.append(line_str)
                                buffer = b""
                        else:
                            buffer += bytes([byte])

                except Exception as e:
                    log.error(f"Error reading stream: {str(e)}")
                    break

            # Process any remaining data in buffer
            if buffer:
                line_str = buffer.decode("utf-8", errors="replace").strip()
                if line_str:
                    output.append(line_str)
            return output

        # 并发读取stdout和stderr
        stdout_task = asyncio.create_task(read_stream(process.stdout, "stdout"))
        stderr_task = asyncio.create_task(read_stream(process.stderr, "stderr"))

        try:
            # 等待进程结束，支持超时
            if timeout is not None and timeout > 0:
                await asyncio.wait_for(process.wait(), timeout=timeout)
            else:
                await process.wait()
        except asyncio.TimeoutError:
            # 超时：杀死整个进程组
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except Exception:
                try:
                    process.kill()
                except Exception:
                    pass

            # 取消读取任务
            for t in (stdout_task, stderr_task):
                if not t.done():
                    t.cancel()
            try:
                await asyncio.gather(stdout_task, stderr_task, return_exceptions=True)
            except Exception:
                pass

            msg = f"命令执行超时（{timeout}s），已终止进程。"
            return "", msg

        # 正常结束：收集输出
        stdout_lines, stderr_lines = await asyncio.gather(stdout_task, stderr_task)

        stdout = function.clean_tqdm_output("\n".join(stdout_lines))
        stderr = function.clean_tqdm_output("\n".join(stderr_lines))

        return stdout, stderr

    except Exception as e:
        log.error(f"Error executing shell: {str(e)}")
        log.error(traceback.format_exc())
        return "", f"Error executing shell: {str(e)}"