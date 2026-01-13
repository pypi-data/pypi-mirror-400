import subprocess
import os
import asyncio
import signal
import logging
import shlex
import uuid
from src.requests import ExecutionStatus

from typing import Optional, Dict, List
from pathlib import Path

executor_logger = logging.getLogger(__name__)

class Executor:
    """Code execution handler with tmux support"""
    
    def __init__(
        self,
        task_id: str,
        code: str,
        language: str,
        tag: str,
        language_configs: Dict,
        wrappers: Dict,
        timeout: int,
        sudo_enabled: bool,
        running_tasks: Dict,
        execution_status,
        get_result_dir_func,
        get_result_files_func,
        monitor_log_files_func,
        wrap: Optional[str] = None,
        sudo: bool = False,
        password: Optional[str] = None,
        interactive: bool = False,
        image: Optional[str] = None,
        wrapper_script_opts: Optional[List[str]] = None
    ):
        self.task_id = task_id
        self.code = code
        self.language = language
        self.tag = tag
        self.language_configs = language_configs
        self.wrappers = wrappers
        self.timeout = timeout
        self.sudo_enabled = sudo_enabled
        self.running_tasks = running_tasks
        self.ExecutionStatus = execution_status
        self.get_result_dir = get_result_dir_func
        self.get_result_files = get_result_files_func
        self.monitor_log_files = monitor_log_files_func
        self.wrap = wrap
        self.sudo = sudo
        self.password = password
        self.interactive = interactive
        self.image = image  # 画像の拡張子（例: "png"）
        self.wrapper_script_opts = wrapper_script_opts or []  # ラッパースクリプトに渡す引数
        
        # Internal state
        self.temp_file: Optional[str] = None
        self.wrapper_script: Optional[str] = None
        self.stdout_file = None
        self.stderr_file = None
        self.process = None
        self.result_files: Optional[Dict[str, Path]] = None
        
        # Platform detection (memoized)
        self._is_util_linux_cached: Optional[bool] = None
    
    def is_util_linux(self) -> bool:
        """Check if script command is util-linux version (memoized)"""
        if self._is_util_linux_cached is not None:
            return self._is_util_linux_cached
        
        try:
            # script -V を実行してエラーにならなければ util-linux
            result = subprocess.run(
                ['script', '-V'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            self._is_util_linux_cached = (result.returncode == 0)
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            # scriptコマンドが見つからない、またはタイムアウトした場合はmacOS版と判断
            self._is_util_linux_cached = False
        
        return self._is_util_linux_cached
    
    def _get_script_command_options(self, output_file: str, command: str) -> list:
        """Get script command with options, output file, and command based on platform"""
        if self.is_util_linux():
            # Linux (util-linux): script -f -e -q -c '<実行コマンド>' -B <std output file>
            # シングルクォートで囲む必要がある
            return f"'script -f -e -q -c \"{command}\" -B {output_file}'"
        else:
            # macOS: script -F -q -e <std output file> <実行コマンド> (クォートなし)
            # commandはクォートで囲まずにそのまま渡す
            return f"'script -F -q -e {output_file} {command}'"
    
    def validate_params(self) -> bool:
        """Validate execution parameters"""
        # 言語設定のチェック
        lang_config = self.language_configs.get(self.language.lower())
        if not lang_config:
            self.running_tasks[self.task_id]['status'] = self.ExecutionStatus.FAILED
            self.running_tasks[self.task_id]['error'] = f'Unsupported language: {self.language}'
            return False
        
        return True
    
    def prepare_result_files(self) -> bool:
        """Prepare result directory and files"""
        try:
            result_dir = self.get_result_dir(self.tag)
            self.result_files = self.get_result_files(self.task_id, self.tag)
            
            # 結果ディレクトリを作成
            result_dir.mkdir(parents=True, exist_ok=True)
            
            # stderrファイルを開く（stdoutはscriptコマンドがファイルに書き込むため不要）
            self.stderr_file = open(self.result_files['stderr'], 'w', encoding='utf-8', buffering=1)
            
            return True
        except Exception as e:
            if self.stderr_file:
                try:
                    self.stderr_file.close()
                except Exception:
                    pass
            self.running_tasks[self.task_id]['status'] = self.ExecutionStatus.FAILED
            self.running_tasks[self.task_id]['error'] = f'Failed to prepare result files: {e}'
            return False
    
    def create_codeblock_file(self) -> bool:
        """Create code block file in results directory with task_id as filename"""
        try:
            lang_config = self.language_configs.get(self.language.lower())
            
            # resultsディレクトリを取得
            result_dir = self.get_result_dir(self.tag)
            result_dir.mkdir(parents=True, exist_ok=True)
            
            # コード内のRUND_IMAGE_PATHを置換
            processed_code = self.code
            if self.image:
                # 画像パス: .rundmark/results/<tag>/<task_id>.<extension>
                image_path = str(result_dir / f"{self.task_id}.{self.image}")
                # RUND_IMAGE_PATHを実際のパスに置換
                processed_code = processed_code.replace("RUND_IMAGE_PATH", image_path)
                executor_logger.debug(f"[{self.task_id}] Replaced RUND_IMAGE_PATH with: {image_path}")
            
            # コードブロックファイルを作成（task_idをファイル名に使用）
            code_filename = f"{self.task_id}.{lang_config['extension']}"
            code_file_path = result_dir / code_filename
            
            with open(code_file_path, 'w', encoding='utf-8') as f:
                f.write(processed_code)
            
            self.temp_file = str(code_file_path)
            executor_logger.debug(f"[{self.task_id}] Created code block file: {self.temp_file}")
            return True
        except Exception as e:
            self.running_tasks[self.task_id]['status'] = self.ExecutionStatus.FAILED
            self.running_tasks[self.task_id]['error'] = f'Failed to create code block file: {e}'
            return False
    
    def create_wrapper_script(self) -> bool:
        """Create wrapper script that executes the command with the specified language and writes exit code"""
        try:
            # .rundmark/tmpディレクトリを取得
            result_dir = self.get_result_dir(self.tag)
            rundmark_dir = result_dir.parent.parent  # results/tag -> results -> .rundmark
            tmp_dir = rundmark_dir / "tmp"
            tmp_dir.mkdir(parents=True, exist_ok=True)
            
            # ラッパースクリプトを作成
            wrapper_filename = f"{self.task_id}-wrap-{uuid.uuid4().hex}.sh"
            wrapper_file_path = tmp_dir / wrapper_filename
            
            # 言語に応じたコマンドを構築
            lang_config = self.language_configs.get(self.language.lower())
            lang_cmd = lang_config['command'](self.temp_file)
            
            # wrapperコマンドを取得
            wrapper_cmd = []
            if self.wrap:
                wrapper_cmd = self.wrappers.get(self.wrap.lower(), None)
                if wrapper_cmd is None:
                    raise ValueError(f'Unsupported wrapper: {self.wrap}')
            
            # ラッパースクリプトの内容
            return_code_file = str(self.result_files['return_code'])
            
            # コマンドを構築（wrapperコマンド + 言語コマンド）
            if wrapper_cmd:
                cmd_parts = wrapper_cmd + lang_cmd
            else:
                cmd_parts = lang_cmd
            
            # wrapper_script_optsを引数として追加
            args_str = ''
            if self.wrapper_script_opts:
                args_str = ' ' + ' '.join(shlex.quote(arg) for arg in self.wrapper_script_opts)
            
            wrapper_content = f"""#!/bin/bash
# Wrapper script for rundmark execution
# Execute the command with the specified language and capture exit code

{' '.join(shlex.quote(arg) for arg in cmd_parts)}{args_str}
EXIT_CODE=$?
echo $EXIT_CODE > {shlex.quote(return_code_file)}
exit $EXIT_CODE
"""
            
            with open(wrapper_file_path, 'w', encoding='utf-8') as f:
                f.write(wrapper_content)
            
            # 実行権限を付与
            os.chmod(wrapper_file_path, 0o755)
            
            self.wrapper_script = str(wrapper_file_path)
            executor_logger.debug(f"[{self.task_id}] Created wrapper script: {self.wrapper_script}")
            return True
        except Exception as e:
            self.running_tasks[self.task_id]['status'] = self.ExecutionStatus.FAILED
            self.running_tasks[self.task_id]['error'] = f'Failed to create wrapper script: {e}'
            return False
    
    def build_command(self) -> list:
        """Build command to execute"""
        # Always execute the wrapper script (which contains the language command)
        # The wrapper script already contains the language command, with wrap command if specified
        if not self.wrapper_script:
            raise RuntimeError("Wrapper script not created")
        base_cmd = ['bash', self.wrapper_script]
        
        executor_logger.debug(f"Running command: {' '.join(base_cmd)}")
        return base_cmd
    
    
    async def wait_for_completion(self) -> Optional[int]:
        """Wait for process completion and handle result"""
        loop = asyncio.get_event_loop()
        
        try:            
            # return-codeファイルが作成されるまで待機（tmuxセッションの終了確認）
            return_code_file = self.result_files['return_code']
            max_wait_time = self.timeout
            wait_interval = 0.1   # 0.1秒ごとにチェック
            elapsed_time = 0.0
            
            while not return_code_file.exists() and elapsed_time < max_wait_time:
                await asyncio.sleep(wait_interval)
                elapsed_time += wait_interval
            
            if not return_code_file.exists():
                executor_logger.warning(f"[{self.task_id}] Return-code file not created after {max_wait_time} seconds: {return_code_file}")
            
            # stderrファイルをフラッシュして閉じる（stdoutはscriptコマンドが管理）
            if self.stderr_file:
                self.stderr_file.flush()
                self.stderr_file.close()
                self.stderr_file = None
            
            # return-codeファイルからexit codeを読み取る（既に待機済み）
            if return_code_file.exists():
                try:
                    with open(return_code_file, 'r', encoding='utf-8') as f:
                        exit_code_str = f.read().strip()
                        if exit_code_str:
                            actual_exit_code = int(exit_code_str)
                            executor_logger.debug(f"[{self.task_id}] Read exit code from file: {actual_exit_code}")
                except Exception as e:
                    executor_logger.error(f"Failed to read return-code file: {e}")
            else:
                executor_logger.warning(f"[{self.task_id}] Return-code file not created, timeout occurred")
            
            # ログファイルから結果を読み取る
            try:
                with open(self.result_files['stdout'], 'r', encoding='utf-8') as f:
                    stdout = f.read()
                with open(self.result_files['stderr'], 'r', encoding='utf-8') as f:
                    stderr = f.read()
            except Exception as e:
                executor_logger.error(f"Failed to read log files: {e}")
                stdout = ""
                stderr = ""
            
            if elapsed_time >= max_wait_time:
                await self.handle_timeout()
                return None
            
            if actual_exit_code != 0:
                self.running_tasks[self.task_id]['status'] = self.ExecutionStatus.FAILED
                self.running_tasks[self.task_id]['output'] = stdout
                self.running_tasks[self.task_id]['error'] = stderr
            else:
                self.running_tasks[self.task_id]['status'] = self.ExecutionStatus.COMPLETED
                self.running_tasks[self.task_id]['output'] = stdout
                self.running_tasks[self.task_id]['error'] = None
            
            # 完了を通知
            stream_queue = self.running_tasks[self.task_id]['stream_queue']
            await stream_queue.put(('status', {
                'status': self.running_tasks[self.task_id]['status'],
                'output': stdout,
                'error': stderr
            }))
            
            return actual_exit_code
            
        except asyncio.TimeoutError:
            await self.handle_timeout()
            return None
    
    async def handle_timeout(self):
        """Handle process timeout"""
        executor_logger.warning(f"[{self.task_id}] Process timeout after {self.timeout} seconds (PID: {self.process.pid if self.process else 'N/A'})")

        # Stop tmux session        
        self.stop()
        
        # タイムアウト時もreturn-codeファイルを作成
        try:
            with open(self.result_files['return_code'], 'w', encoding='utf-8') as f:
                f.write(str(-1))  # タイムアウトを示す値
        except Exception as e:
            executor_logger.error(f"Failed to write return-code file: {e}")
        
        self.running_tasks[self.task_id]['status'] = self.ExecutionStatus.FAILED
        self.running_tasks[self.task_id]['error'] = f"Process timeout"
        
        stream_queue = self.running_tasks[self.task_id]['stream_queue']
        await stream_queue.put(('error', f"Process timeout\n"))
        await stream_queue.put(('status', {
            'status': self.ExecutionStatus.FAILED,
            'error': f"Process timeout"
        }))
    
    def stop(self):
        """Stop the execution by killing process and tmux session"""
        executor_logger.debug(f"[{self.task_id}] Stopping execution")
                
        # tmuxセッションを終了
        session_name = f"rundmark-{self.task_id}"
        try:
            # tmuxセッションが存在するか確認
            check_result = subprocess.run(
                ['tmux', 'has-session', '-t', session_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            if check_result.returncode == 0:
                # セッションが存在する場合は終了
                executor_logger.debug(f"[{self.task_id}] Killing tmux session: {session_name}")
                subprocess.run(
                    ['tmux', 'kill-session', '-t', session_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                )
                executor_logger.debug(f"[{self.task_id}] Tmux session killed: {session_name}")
            else:
                executor_logger.debug(f"[{self.task_id}] Tmux session not found: {session_name}")
        except subprocess.TimeoutExpired:
            executor_logger.warning(f"[{self.task_id}] Timeout while killing tmux session: {session_name}")
        except Exception as e:
            executor_logger.warning(f"[{self.task_id}] Failed to kill tmux session: {e}")
        
        # ステータスを更新
        if self.task_id in self.running_tasks:
            self.running_tasks[self.task_id]['status'] = self.ExecutionStatus.CANCELLED
            self.running_tasks[self.task_id]['error'] = "Execution cancelled by user"
            executor_logger.debug(f"[{self.task_id}] Status updated to CANCELLED")
    
    def cleanup(self):
        """Clean up resources"""
        # stderrファイルを閉じる（stdoutはscriptコマンドが管理）
        if self.stderr_file:
            try:
                self.stderr_file.close()
            except Exception:
                pass
        
        # コードブロックファイルはresultsディレクトリに保持するため削除しない
        
        # Clean up wrapper script
        if self.wrapper_script and os.path.exists(self.wrapper_script):
            try:
                os.unlink(self.wrapper_script)
            except Exception as e:
                executor_logger.error(f"Failed to remove wrapper script: {self.wrapper_script} : {e}")
        
        # Clean up process reference and stdin
        if self.task_id in self.running_tasks:
            task = self.running_tasks[self.task_id]
            process = task.get('process')
            if process and process.stdin and not process.stdin.closed:
                try:
                    process.stdin.close()
                except Exception:
                    pass
            self.running_tasks[self.task_id]['process'] = None
    
    async def execute(self):
        """Main execution method"""
        executor_logger.debug(f"[{self.task_id}] execute started with timeout={self.timeout} seconds")
        
        # Validate parameters
        if not self.validate_params():
            return
        
        # Prepare result files
        if not self.prepare_result_files():
            return
        
        try:
            # Create code block file
            if not self.create_codeblock_file():
                return

            # Update task status
            self.running_tasks[self.task_id]['status'] = self.ExecutionStatus.RUNNING
            self.running_tasks[self.task_id]['tag'] = self.tag
            self.running_tasks[self.task_id]['log_files'] = self.result_files
            
            # Create wrapper script (always needed to execute code blocks)
            # The wrapper script contains the language command, with wrap command if specified
            if not self.create_wrapper_script():
                return
            
            # Build command for process execution (always executes the wrapper script)
            base_cmd = self.build_command()
            
            # Start process
            loop = asyncio.get_event_loop()
            try:
                self.process = await loop.run_in_executor(None, self._run_process_sync, base_cmd)
            except Exception as e:
                executor_logger.error(f"[{self.task_id}] Failed to start process: {e}")
                self.running_tasks[self.task_id]['status'] = self.ExecutionStatus.FAILED
                self.running_tasks[self.task_id]['error'] = f'Failed to start process: {e}'
                return
            
            executor_logger.debug(f"[{self.task_id}] Process started (PID: {self.process.pid}), timeout={self.timeout} seconds")
            self.running_tasks[self.task_id]['process'] = self.process
            stream_queue = self.running_tasks[self.task_id]['stream_queue']
            read_positions = self.running_tasks[self.task_id].get('read_positions', {})
            self.running_tasks[self.task_id]['read_positions'] = read_positions
            
            # ファイル監視タスクを開始
            asyncio.create_task(self.monitor_log_files(self.task_id, self.tag, stream_queue, read_positions))
            
            # Wait for completion
            executor_logger.debug(f"[{self.task_id}] Waiting for process (PID: {self.process.pid}) to complete with timeout={self.timeout} seconds")
            await self.wait_for_completion()
            
        except Exception as e:
            self.running_tasks[self.task_id]['status'] = self.ExecutionStatus.FAILED
            self.running_tasks[self.task_id]['error'] = str(e)
            
            # エラー時もreturn-codeファイルを作成
            if self.result_files:
                try:
                    with open(self.result_files['return_code'], 'w', encoding='utf-8') as f:
                        f.write(str(-1))
                except Exception:
                    pass
        
        finally:
            self.cleanup()
    
    def _build_tmux_script_command(self, base_cmd: list) -> str:
        """Build tmux script command as a string"""
        # ラッパースクリプトを実行するコマンド
        wrapper_cmd = ['bash', self.wrapper_script]
        wrapper_cmd_str = ' '.join(shlex.quote(arg) for arg in wrapper_cmd)
        
        # scriptコマンドを構築（プラットフォームごとに異なる形式）
        # macOS: script -F -q -e <std output file> bash <wrapper_script>
        # Linux: script -f -e -q -c 'bash <wrapper_script>' -B <std output file>
        script_cmd = self._get_script_command_options(
            str(self.result_files['stdout']),
            wrapper_cmd_str
        )
        
        # tmux new-sessionでscriptコマンドを実行（-dオプションでデタッチモード）
        # tmux new-session -d -s <session_name> 'script ...'
        session_name = f"rundmark-{self.task_id}"
        tmux_cmd = f"tmux new-session -d -s {shlex.quote(session_name)} {script_cmd}"
        
        executor_logger.debug(f"[{self.task_id}] Running tmux script command: {tmux_cmd}")
        return tmux_cmd
    
    def _run_process_sync(self, base_cmd: list) -> subprocess.Popen:
        """Synchronous process runner using tmux script (called from executor thread)"""
        # tmux scriptコマンドを構築
        script_cmd = self._build_tmux_script_command(base_cmd)
        
        # tmux scriptコマンドを実行（shell=Trueで文字列として実行）
        process = subprocess.Popen(
            script_cmd,
            shell=True,
            stdin=None,
            stdout=subprocess.DEVNULL,  # stdoutはscriptコマンドがファイルに書き込むため不要
            stderr=self.stderr_file,
            text=True,
            bufsize=1,
            preexec_fn=os.setsid if os.name != 'nt' else None
        )
        executor_logger.debug(f"[{self.task_id}] Running process: {process}")
        
        return process
