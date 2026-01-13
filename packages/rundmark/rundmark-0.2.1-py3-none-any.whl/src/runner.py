import argparse
import logging
import sys
import asyncio
import uuid
import re
from pathlib import Path

from src.config import init_config
from src.execute.run_block import execute_code_async
from src.execute.file_block import create_file
from src.requests import ExecutionStatus, FileRequest

config = init_config()
from src.execute.run_block import config as run_block_config
run_block_config.__dict__.update(config.__dict__)

def sanitize_tag(tag: str) -> str:
    """Sanitize tag name by replacing path separators and special characters"""
    # Replace path separators with underscores
    tag = tag.replace('/', '_').replace('\\', '_')
    # Remove or replace other problematic characters
    tag = re.sub(r'[<>:"|?*]', '_', tag)
    # Remove leading/trailing dots and spaces
    tag = tag.strip('. ')
    return tag

class CodeBlock:
    def __init__(self, lines: list[str], idx: int):
        self.lines = lines
        self.idx = idx
        self.language = None
        self.code = None
        self.options = None
        self.title = None
        self.options = {}

    def parse_options(self, opt: str):
        """Parse the options and return the key and value

        >>> lines = ["```bash", "echo 'Hello, World!'", "```"]
        >>> opt = "tag=test"
        >>> codeblock = CodeBlock(lines, 0)
        >>> codeblock.parse_options(opt)
        ('tag', 'test')
        >>> opt = "no"
        >>> codeblock = CodeBlock(lines, 0)
        >>> codeblock.parse_options(opt)
        ('no', True)
        """
        if '=' in opt:
            k, v = opt.split('=', 1)
            v = v.strip()
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            elif v.startswith("'") and v.endswith("'"):
                v = v[1:-1]
            return k.strip(), v
        else:
            return opt, True

    def extract_code(self) -> int:
        """
        >>> lines = ["```bash", "echo 'Hello, World!'", "```"]
        >>> codeblock = CodeBlock(lines, 0)
        >>> codeblock.extract_code() # return next line index
        3
        >>> codeblock.code
        "echo 'Hello, World!'"
        """
        self.code = ""
        idx = self.idx + 1
        while not self.lines[idx].startswith('```'):
            self.code += self.lines[idx]
            idx += 1
        logging.debug(f"extracted code from line: {self.idx+1} to {idx}")
        return idx + 1

    def parse_block_start(self) -> None:
        """ Parse the block start and extract the language and options """
        # Remove ```
        line = self.lines[self.idx][3:].strip()
        if line.endswith('}'):
            line = line[:-1]
        logging.debug(f"codeblock start line: {line}")

        # Extract language
        self.language = "bash"
        self.options = {}
        options = ""
        if line:
            if '{' in line:
                self.language, options  = line.split('{', 1)
                self.language = self.language.strip()
                options = options.strip()
                if not self.language:
                    self.language = 'bash'
            else:
                self.language = line.strip()

        # Extract options
        if options:
            for opt in options.split(','):
                k, v = self.parse_options(opt)
                self.options[k] = v
        
        logging.debug(f"codeblock options: {self.options}")

    def runnable(self):
        """ Check if the codeblock is runnable 

        >>> lines = ["```bash", "echo 'Hello, World!'", "```"]
        >>> codeblock = CodeBlock(lines, 0)
        >>> codeblock.parse_block_start()
        >>> codeblock.runnable()
        True
        >>> lines = ["```bash{no}", "echo 'Hello, World!'", "```"]
        >>> codeblock = CodeBlock(lines, 0)
        >>> codeblock.parse_block_start()
        >>> codeblock.runnable()
        False
        """
        return "no" not in self.options

    def initialize_task(self, task_id: str):
        # Sanitize tag to avoid path traversal issues
        self.tag = sanitize_tag(self.tag)
        
        # Initialize task status (same as execute_code does)
        from src.requests import ExecutionStatus
        import threading
        
        config.running_tasks[task_id] = {
            'status': ExecutionStatus.PENDING,
            'output': None,
            'error': None,
            'process': None,
            'stream_queue': asyncio.Queue(),
            'stdin_lock': threading.Lock(),
            'interactive': self.options.get('interactive', False),
            'tag': self.tag,
        }
        run_block_config.running_tasks[task_id] = config.running_tasks[task_id]

    def print_codeblock(self):
        print("==== CODEBLOCK ====")
        print(f"Codeblock:\n{self.code}")
        print(f"Language: {self.language}")
        print(f"Tag: {self.tag}")
        print(f"Options: {self.options}")

    async def run_block(self):
        self.print_codeblock()

        task_id = str(uuid.uuid4())
        self.initialize_task(task_id)
        
        timeout = self.options.get('timeout', None)
        if timeout:
            timeout = int(timeout)
        else:
            timeout = config.timeout_seconds
        
        await execute_code_async(
            task_id=task_id,
            code=self.code,
            language=self.language,
            tag=self.tag,
            wrap=self.options.get('wrap', None),
            timeout=timeout,
            interactive=self.options.get('interactive', False),
            image=self.options.get('image', None),
        )

        executor = config.running_tasks.get(task_id, {}).get('executor')
        if executor:
            await executor.wait_for_completion()
            result = executor.running_tasks[task_id]
            return result
        else:
            return None

    def get_file_path(self):
        path = self.options.get('file', None)
        if path == True:
            idx = self.idx - 1
            while idx > 0:
                if self.lines[idx].strip():
                    return self.lines[idx].strip().replace(' ', '')
                idx -= 1
            return ""

        return path

    async def file_block(self):
        path = self.get_file_path()
        if not path:
            print("No file path provided")
            return False
        print(f"File path: {path}")
        file_request = FileRequest(
            path=path,
            content=self.code,
            sudo=self.options.get('sudo', False),
            password=self.options.get('password', None),
        )
        return await create_file(file_request)

    async def table_block(self):
        print("==== TABLE BLOCK ====")
        print(self.code)
        print("")

    async def run(self):
        if "file" in self.options:
            print("==== FILE BLOCK ====")
            await self.file_block()
            print("")
            return True
        else:
            result = await self.run_block()

        if result:
            if result['status'] == ExecutionStatus.COMPLETED:
                print("==== OUTPUT ====")
                print(result['output'])
                return True
            else:
                print(result['error'])
                return False
        else:
            print("No result")
            return False

def read_markdown(markdown_file: str) -> list[CodeBlock]:
    codeblocks = []
    try:
        with open(markdown_file, 'r') as file:
            lines = file.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

    max_idx = len(lines)
    idx = 0
    while idx < max_idx:
        line = lines[idx]
        if line.startswith('```'):
            codeblock = CodeBlock(lines, idx)
            codeblock.parse_block_start()
            idx = codeblock.extract_code()
            if codeblock.runnable():
                # Use basename of markdown file for tag
                markdown_path = Path(markdown_file)
                basename = markdown_path.stem  # filename without extension
                codeblock.tag = f"{basename}-{idx}"
                codeblocks.append(codeblock)
        else:
            idx += 1

    return codeblocks

async def main(file_name: str, keep_going: bool = False):
    config.set_global_variables(file_name)
    codeblocks = read_markdown(config.files_dir / file_name)
    failed_blocks = []
    skip_blocks = []

    for codeblock in codeblocks:
        if "skip" in codeblock.options:
            print(f"Skipping codeblock {codeblock.tag}")
            skip_blocks.append(codeblock.tag)
            continue
        if not await codeblock.run():
            error_msg = f"❌ Codeblock {codeblock.tag} failed"
            print(error_msg)
            if keep_going:
                failed_blocks.append(codeblock.tag)
                continue
            else:
                break
    
    if skip_blocks:
        print(f"\n⚠️  {len(skip_blocks)} codeblock(s) skipped: {', '.join(skip_blocks)}")

    if keep_going and failed_blocks:
        print(f"\n⚠️  {len(failed_blocks)} codeblock(s) failed: {', '.join(failed_blocks)}")
        return False
    
    return True

def from_rundmark(file_name: str, debug: bool = False, keep_going: bool = False):
    """Entry point for rundmark -f command"""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    
    asyncio.run(main(file_name, keep_going=keep_going))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run Markdown')
    parser.add_argument('file_name', type=str, help='The Markdown file to run')
    parser.add_argument('--test', action='store_true', help='Enable test mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('-k', '--keep-going', action='store_true', help='Continue processing even if errors occur')
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.test:
        import doctest
        doctest.testmod(verbose=True)
        sys.exit(0)

    asyncio.run(main(args.file_name, keep_going=args.keep_going))