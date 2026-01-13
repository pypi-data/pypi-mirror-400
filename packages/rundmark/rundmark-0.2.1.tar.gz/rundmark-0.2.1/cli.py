import re
import argparse
import time
import sys
import json
import os
import getpass
import socket
import http.client
from pathlib import Path
from typing import Optional, List, Dict
from urllib.parse import urlencode


class UnixHTTPConnection(http.client.HTTPConnection):
    """Unix domain socket経由でHTTPリクエストを送るためのカスタムHTTPConnection"""
    def __init__(self, socket_path):
        self.socket_path = socket_path
        super().__init__('localhost')

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.socket_path)


class RunnerCli:
    def __init__(self, socket_file: Optional[str] = None):
        if socket_file:
            self.socket_file = socket_file
        else:
            # デフォルトのソケットファイルパス
            self.socket_file = str(Path.cwd() / ".rundmark" / "rundmark.socket")
        
        # ソケットファイルが存在するか確認
        if not os.path.exists(self.socket_file):
            raise FileNotFoundError(f"Socket file not found: {self.socket_file}")

    def _make_request(self, method: str, path: str, body: Optional[bytes] = None, 
                     headers: Optional[Dict] = None, params: Optional[Dict] = None) -> tuple[int, Dict, bytes]:
        """Unix domain socket経由でHTTPリクエストを送信"""
        if params:
            path += '?' + urlencode(params)
        
        conn = UnixHTTPConnection(self.socket_file)
        try:
            request_headers = {'Content-Type': 'application/json'}
            if headers:
                request_headers.update(headers)
            
            conn.request(method, path, body, request_headers)
            response = conn.getresponse()
            
            status_code = response.status
            response_headers = dict(response.getheaders())
            response_body = response.read()
            
            return status_code, response_headers, response_body
        finally:
            conn.close()

    def login(self) -> bool:
        """認証（Unix domain socket経由の場合は常に成功）"""
        try:
            status_code, _, _ = self._make_request('GET', '/auth/session')
            return status_code == 200
        except Exception as e:
            print(f"Error: Failed to connect to server: {e}")
            return False

    def create_file(self, file_path: str, content: str, sudo: bool = False, password: Optional[str] = None) -> bool:
        """ファイルを作成"""
        try:
            payload = {
                "path": file_path,
                "content": content,
                "sudo": sudo
            }
            if password:
                payload["password"] = password
            
            body = json.dumps(payload).encode('utf-8')
            status_code, _, response_body = self._make_request('POST', '/api/file', body=body)
            
            if status_code == 200:
                return True
            else:
                try:
                    error_detail = json.loads(response_body.decode('utf-8')).get('detail', 'Unknown error')
                    print(f"Error: Failed to create file: {error_detail}")
                except:
                    print(f"Error: Failed to create file: {status_code}")
                return False
        except Exception as e:
            print(f"Error: Failed to connect to server: {e}")
            return False


    def run(self, code: str, language: str = "bash", tag: str = "", task_id: Optional[str] = None, 
            interactive: bool = False) -> Optional[str]:
        """コードを実行開始し、task_idを返す"""
        try:
            payload = {
                "code": code,
                "language": language,
                "tag": tag,
                "interactive": interactive,
            }
            if task_id:
                payload["task_id"] = task_id
            
            body = json.dumps(payload).encode('utf-8')
            status_code, _, response_body = self._make_request('POST', '/api/execute', body=body)
            
            if status_code == 200:
                result = json.loads(response_body.decode('utf-8'))
                return result.get("task_id")
            elif status_code == 401:
                print("Error: Authentication required. Please login first.")
                return None
            else:
                print(f"Error: Failed to start execution: {status_code}")
                print(f"Response: {response_body.decode('utf-8')}")
                return None
        except Exception as e:
            print(f"Error: Failed to connect to server: {e}")
            return None

    def send_input(self, task_id: str, input_data: str) -> bool:
        """実行中のタスクにstdin入力を送信"""
        try:
            body = json.dumps({"input": input_data}).encode('utf-8')
            status_code, _, response_body = self._make_request('POST', f'/api/execute/{task_id}/input', body=body)
            
            if status_code == 200:
                return True
            elif status_code == 404:
                print(f"Error: Task {task_id} not found")
            elif status_code == 400:
                try:
                    detail = json.loads(response_body.decode('utf-8')).get("detail", "Failed to send input")
                    print(f"Error: {detail}")
                except:
                    print(f"Error: Failed to send input")
            elif status_code == 401:
                print("Error: Authentication required. Please login first.")
            else:
                print(f"Error: Failed to send input: {status_code}")
                print(f"Response: {response_body.decode('utf-8')}")
        except Exception as e:
            print(f"Error: Failed to connect to server: {e}")
        return False

    def get_status(self, task_id: str, tag: str) -> Optional[Dict]:
        """実行状態を取得"""
        try:
            status_code, _, response_body = self._make_request(
                'GET', 
                f'/api/execute/{task_id}',
                params={"tag": tag}
            )
            
            if status_code == 200:
                return json.loads(response_body.decode('utf-8'))
            elif status_code == 404:
                print(f"Error: Task {task_id} not found")
                return None
            elif status_code == 401:
                print("Error: Authentication required. Please login first.")
                return None
            else:
                print(f"Error: Failed to get status: {status_code}")
                return None
        except Exception as e:
            print(f"Error: Failed to connect to server: {e}")
            return None

    def wait_for_completion(self, task_id: str, tag: str, poll_interval: float = 0.5, stream: bool = True) -> Optional[Dict]:
        """タスクの完了を待つ（ストリーミング対応）"""
        if stream:
            return self.wait_for_completion_stream(task_id, tag)
        
        # フォールバック: ポーリング方式
        while True:
            status = self.get_status(task_id, tag)
            if not status:
                return None
            
            current_status = status.get("status")
            
            if current_status == "completed":
                return status
            elif current_status == "failed":
                return status
            elif current_status == "cancelled":
                return status
            elif current_status in ["pending", "running"]:
                time.sleep(poll_interval)
            else:
                print(f"Unknown status: {current_status}")
                return status

    def wait_for_completion_stream(self, task_id: str, tag: str) -> Optional[Dict]:
        """ストリーミングでタスクの完了を待つ"""
        try:
            conn = UnixHTTPConnection(self.socket_file)
            path = f'/api/execute/stream/{task_id}?{urlencode({"tag": tag})}'
            conn.request('GET', path, headers={'Accept': 'text/event-stream'})
            response = conn.getresponse()
            
            if response.status == 404:
                print(f"Error: Task {task_id} not found")
                conn.close()
                return None
            elif response.status == 401:
                print("Error: Authentication required. Please login first.")
                conn.close()
                return None
            elif response.status != 200:
                print(f"Error: Failed to stream execution: {response.status}")
                conn.close()
                return None
            
            final_status = None
            
            # SSEストリームを処理
            buffer = b''
            while True:
                chunk = response.read(4096)
                if not chunk:
                    break
                
                buffer += chunk
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    if not line:
                        continue
                    
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])  # 'data: 'を除去
                            event_type = data.get('type')
                            
                            if event_type == 'output':
                                # 標準出力をリアルタイムで表示
                                output_data = data.get('data', '')
                                if output_data:
                                    print(output_data, end='', flush=True)
                            elif event_type == 'error':
                                # エラー出力をリアルタイムで表示
                                error_data = data.get('data', '')
                                if error_data:
                                    print(error_data, end='', flush=True, file=sys.stderr)
                            elif event_type == 'status':
                                # 最終状態を取得
                                final_status = {
                                    'task_id': task_id,
                                    'status': data.get('status'),
                                    'output': data.get('output', ''),
                                    'error': data.get('error', '')
                                }
                                conn.close()
                                return final_status
                        except json.JSONDecodeError:
                            continue
            
            conn.close()
            return final_status
            
        except Exception as e:
            print(f"Error: Failed to connect to server: {e}")
            return None

    def stop(self, task_id: str) -> bool:
        """実行を停止"""
        try:
            body = json.dumps({"task_id": task_id}).encode('utf-8')
            status_code, _, response_body = self._make_request('POST', '/api/execute/stop', body=body)
            
            if status_code == 200:
                result = json.loads(response_body.decode('utf-8'))
                print(f"✓ Execution stopped: {result.get('message')}")
                return True
            elif status_code == 404:
                print(f"Error: Task {task_id} not found")
                return False
            elif status_code == 401:
                print("Error: Authentication required. Please login first.")
                return False
            else:
                print(f"Error: Failed to stop execution: {status_code}")
                return False
        except Exception as e:
            print(f"Error: Failed to connect to server: {e}")
            return False

    def cleanup(self, task_id: str) -> bool:
        """タスクをクリーンアップ"""
        try:
            status_code, _, response_body = self._make_request('DELETE', f'/api/execute/{task_id}')
            
            if status_code == 200:
                result = json.loads(response_body.decode('utf-8'))
                print(f"✓ Task cleaned up: {result.get('message')}")
                return True
            elif status_code == 404:
                print(f"Error: Task {task_id} not found")
                return False
            elif status_code == 401:
                print("Error: Authentication required. Please login first.")
                return False
            else:
                print(f"Error: Failed to cleanup task: {status_code}")
                return False
        except Exception as e:
            print(f"Error: Failed to connect to server: {e}")
            return False

    def run_all(self, code_blocks: List[Dict], base_tag: str, default_sudo_password: Optional[str] = None) -> List[Optional[str]]:
        """複数のコードブロックを順次実行"""
        task_ids = []
        used_tags = set()  # Track used tags to detect duplicates
        
        for i, block in enumerate(code_blocks, 1):
            language = block.get('language', 'bash')
            code = '\n'.join(block.get('code', []))
            options = block.get('language_options', {})
            title = block.get('title', '')
            
            if not code.strip():
                continue
            
            # Generate tag from title (replace spaces with underscores, remove symbols, max 20 characters)
            def sanitize_tag(s):
                """Remove specific symbols: -, `, ", and other common symbols"""
                # Replace spaces with underscores, then remove specific symbols
                s = s.replace(' ', '_')
                # Remove specific symbols: -, `, ", and other common symbols
                s = re.sub(r'[-`"\'\.,;:!?@#$%^&*()+=\[\]{}|\\\/<>~]', '', s)
                return s[:20]
            
            tag_option = options.get('tag')
            if tag_option:
                sanitized_tag_option = sanitize_tag(str(tag_option))
                tag = f"{base_tag}-{sanitized_tag_option}"
            elif title and title.strip():
                tag_from_title = sanitize_tag(title.strip())
                tag = f"{base_tag}-{tag_from_title}"
            else:
                # Fallback: use index if no title
                tag = f"{base_tag}-{i}"
            
            # Check for duplicates - if tag already exists, use index instead
            if tag in used_tags:
                tag = f"{base_tag}-{i}"
            
            # Add tag to used_tags set
            used_tags.add(tag)
                        
            # オプションからsudoとpasswordを取得（file作成用）
            sudo = options.get('sudo', False)
            if isinstance(sudo, str):
                sudo = sudo.lower() in ('yes', 'true', '1')
            
            # passwordの優先順位: オプションで指定 > デフォルトパスワード
            password = options.get('password') or default_sudo_password
            
            # file=オプションがある場合は、ファイルを作成
            file_path = options.get('file')
            if file_path:
                print(f"\nCreating file: {file_path}")
                print("=" * 60)
                if not self.create_file(file_path, code, sudo=sudo, password=password):
                    print(f"✗ Failed to create file: {file_path}")
                    task_ids.append(None)
                print("=" * 60)
                continue

            task_description = title if title else 'unknown task'
            print(f"\n[{i}/{len(code_blocks)}] Running {task_description}...")
            print("=" * 60)

            # インタラクティブ入力の取得（inputオプションがある場合）
            interact_opt = options.get('input', False)
            interactive = False
            interact_input = None
            if interact_opt:
                interactive = True
                prompt_text = interact_opt if isinstance(interact_opt, str) and interact_opt not in ("true", "True") else "Input: "
                interact_input = input(prompt_text)

            task_id = self.run(code, language, tag=tag, interactive=interactive)
            if not task_id:
                print(f"✗ Failed to start execution for block {i}")
                task_ids.append(None)
                continue
            
            task_ids.append(task_id)

            # インタラクティブ入力を送信
            if interactive and interact_input is not None:
                # 実行開始直後は準備時間を確保
                time.sleep(1)
                if not self.send_input(task_id, interact_input):
                    print(f"✗ Failed to send input for task {task_id}")
            
            result = self.wait_for_completion(task_id, tag)
            if result:
                status = result.get('status')
                if status == 'completed':
                    output = result.get('output', '')
                    if output:
                        print(output[:-1])  # 末尾の改行を削除
                elif status == 'failed':
                    error = result.get('error', '')
                    output = result.get('output', '')
                    print(f"✗ Task failed: {task_id}")
                    if error:
                        print(f"Error: {error}")
                    if output:
                        print(output[:-1])  # 末尾の改行を削除
                elif status == 'cancelled':
                    print(f"⚠ Task cancelled: {task_id}")
            else:
                print(f"✗ Failed to get result for task {task_id}")
            
            print("=" * 60)
        
        return task_ids

class ParseMardown:
    def __init__(self, input_file):
        self.input_file = input_file

    def extract_title_from_previous_line(self, before_code):
        """Extract title from the line immediately before the code block"""
        if not before_code:
            return ''
        lines = before_code.split('\n')
        # Find the last non-empty line before the code block
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            # Skip empty lines and markdown special characters
            if line and \
               not line.startswith('#') and \
               not line.startswith('*') and \
               not line.startswith('-') and \
               not line.startswith('>') and \
               not line.startswith('`') and \
               not line.startswith('[') and \
               not line.startswith('|') and \
               not re.match(r'^(\d+\.|\d+\))\s', line) and \
               not line.startswith('```'):
                return line
        return ''

    def get_code_blocks(self):
        code_blocks = []
        current_block = None
        current_language = None
        current_options = {}
        before_code_lines = []  # Track lines before current code block

        try:
            with open(self.input_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('```'):
                        # コードブロックの開始または終了
                        rest = stripped[3:].strip()  # ``` を除去
                        
                        if current_block is not None:
                            # コードブロックの終了
                            if current_block:  # 空でない場合のみ追加
                                # Extract title from lines before this code block
                                before_code = ''.join(before_code_lines)
                                title = self.extract_title_from_previous_line(before_code)
                                code_blocks.append({
                                    'language': current_language or 'bash',
                                    'language_options': current_options,
                                    'code': current_block,
                                    'title': title
                                })
                            current_block = None
                            current_language = None
                            current_options = {}
                            before_code_lines = []
                        else:
                            # コードブロックの開始
                            if rest:
                                # 言語とオプションを解析
                                # Example: bash{run="create a user",file=/tmp/new-file.sh,sudo=yes}
                                lang_match = re.match(r'^([a-zA-Z0-9_+-]+)(\{.*\})?$', rest)
                                if lang_match:
                                    current_language = lang_match.group(1)
                                    opts_str = lang_match.group(2)
                                    if opts_str:
                                        # Remove braces
                                        opts_str = opts_str[1:-1]
                                        for opt in opts_str.split(','):
                                            opt = opt.strip()
                                            if '=' in opt:
                                                k, v = opt.split('=', 1)
                                                v = v.strip()
                                                if v.startswith('"') and v.endswith('"'):
                                                    v = v[1:-1]
                                                elif v.startswith("'") and v.endswith("'"):
                                                    v = v[1:-1]
                                                current_options[k.strip()] = v
                                            else:
                                                current_options[opt] = True
                                else:
                                    current_language = rest
                            current_block = []
                    else:
                        # コードブロック内の行
                        if current_block is not None:
                            current_block.append(line.rstrip('\n'))
                        else:
                            # Track lines before code block
                            before_code_lines.append(line)
                
                # ファイル終端で開いたままのコードブロックを処理
                if current_block is not None and current_block:
                    before_code = ''.join(before_code_lines)
                    title = self.extract_title_from_previous_line(before_code)
                    code_blocks.append({
                        'language': current_language or 'bash',
                        'language_options': current_options,
                        'code': current_block,
                        'title': title
                    })

        except FileNotFoundError:
            print(f"File not found: {self.input_file}")
            return []
        except Exception as e:
            print(f"Error reading file: {e}")
            return []

        return code_blocks



def main():
    parser = argparse.ArgumentParser(description='Parse and run Markdown file')
    parser.add_argument('input_file', type=str, help='The input Markdown file')
    parser.add_argument('--socket-file', type=str, default=None,
                        help='Path to Unix domain socket file (default: .rundmark/rundmark.socket)')
    parser.add_argument('-s', '--sudo', action='store_true',
                        help='Prompt for sudo password for code blocks that require sudo')
    args = parser.parse_args()

    # Parse Markdown file
    parse_markdown = ParseMardown(args.input_file)
    code_blocks = parse_markdown.get_code_blocks()
    
    if not code_blocks:
        print("No code blocks found in the Markdown file")
        return

    print(f"Found {len(code_blocks)} code block(s)")
    
    # 入力ファイル名からbase_tagを生成（.md拡張子を除去）
    input_file_path = Path(args.input_file)
    base_tag = input_file_path.stem  # .mdを除去したファイル名
    
    # sudoパスワードを取得（-sオプションが指定された場合）
    sudo_password = None
    if args.sudo:
        sudo_password = getpass.getpass("Enter sudo password: ")
    
    # Initialize runner
    try:
        runner = RunnerCli(socket_file=args.socket_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Login (Unix domain socket経由の場合は常に成功)
    if not runner.login():
        print("Failed to authenticate. Exiting.")
        sys.exit(1)
    
    # Run all code blocks
    runner.run_all(code_blocks, base_tag=base_tag, default_sudo_password=sudo_password)

if __name__ == "__main__":
    main()