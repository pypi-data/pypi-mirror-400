# M21 Editor Backend (Python)

M21 Markdown Editor用のコード実行バックエンドAPIです（Python/FastAPI実装）。

## 機能

- 複数言語のコード実行サポート（bash, python, javascript）
- 非同期実行（バックグラウンドで実行）
- リアルタイムストリーミング出力（SSE）
- 実行結果のファイルキャッシュ（tagベースの管理）
- 実行停止機能
- 実行状態のポーリング
- タイムアウト保護（30秒）
- エラーハンドリング
- CORS対応

## インストール

### 方法1: pipを使用

```bash
pip install -r requirements.txt
```

### 方法2: uvを使用

```bash
uv sync
```

## ビルドと実行

### uv buildを使用してビルド

```bash
cd backend
uv build
```

これにより、`dist/`ディレクトリにwheelファイルが作成されます。

### ビルド後の実行方法

#### 方法1: uv runで直接実行（推奨）

```bash
cd backend
uv run m21-editor
```

デバッグモードで起動する場合:

```bash
cd backend
uv run m21-editor -d
```

sudo機能を有効にして起動する場合:

```bash
cd backend
uv run m21-editor -s
```

デバッグモードとsudo機能の両方を有効にする場合:

```bash
cd backend
uv run m21-editor -d -s
```

#### 方法2: ビルドしたパッケージをインストールして実行

```bash
cd backend
uv build
pip install dist/*.whl
m21-editor
```

デバッグモードで起動:

```bash
m21-editor -d
```

#### 方法3: 従来の方法

```bash
python app.py
```

または

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

## オプション

- `-d`, `--debug`: デバッグモードを有効化（詳細なログを出力）
- `-s`, `--sudo`: sudo機能を有効化（sudo実行とsudo_fileディレクティブを使用可能に）

## API仕様

### POST /api/execute

コードを非同期で実行開始します。実行結果は`results/<tag>/`ディレクトリに保存されます。

**リクエスト:**
```json
{
  "code": "print('hello')",
  "language": "python",
  "tag": "my-task",
  "task_id": "optional-task-id",
  "sudo": false,
  "password": "optional-password"
}
```

**リクエストパラメータ:**
- `code` (必須): 実行するコード
- `language` (オプション): 言語（デフォルト: `bash`）
- `tag` (必須): タスクのタグ名（結果ファイルの保存先ディレクトリ名として使用）
- `task_id` (オプション): タスクID（指定しない場合は自動生成）
- `sudo` (オプション): sudo実行を有効化（デフォルト: `false`）
- `password` (オプション): sudoパスワード（`sudo=true`の場合に必要）

**レスポンス:**
```json
{
  "task_id": "uuid-string",
  "status": "pending",
  "message": "Execution started"
}
```

**実行結果の保存:**
実行結果は以下のファイルとして`results/<tag>/`ディレクトリに保存されます：
- `<task_id>-std.log`: 標準出力
- `<task_id>-err.log`: 標準エラー出力
- `<task_id>-return-code`: リターンコード（テキスト形式）

### GET /api/execute/{task_id}

実行状態を取得します（ポーリング方式）。結果はファイルキャッシュから読み取られます。

**注意:** リアルタイムで出力を取得したい場合は、`/api/execute/stream/{task_id}` を使用してください。

**クエリパラメータ:**
- `tag` (必須): タスクのタグ名

**パスパラメータ:**
- `task_id`: タスクID。`"latest"`を指定すると、指定されたtag内の最新のタスクを取得します。

**レスポンス（実行中）:**
```json
{
  "task_id": "uuid-string",
  "status": "running"
}
```

**レスポンス（完了）:**
```json
{
  "task_id": "uuid-string",
  "status": "completed",
  "output": "hello\n",
  "result": "hello\n"
}
```

**レスポンス（エラー）:**
```json
{
  "task_id": "uuid-string",
  "status": "failed",
  "error": "Error message",
  "output": ""
}
```

**使用例:**
```bash
# 特定のタスクを取得
curl -H "Cookie: m21_session=your-session-id" \
  "http://localhost:8000/api/execute/{task_id}?tag=my-task"

# 最新のタスクを取得
curl -H "Cookie: m21_session=your-session-id" \
  "http://localhost:8000/api/execute/latest?tag=my-task"
```

### GET /api/execute/stream/{task_id}

実行中の出力をリアルタイムでストリーミングします（Server-Sent Events）。ログファイルを監視して新しい内容をストリーミングします。

**クエリパラメータ:**
- `tag` (必須): タスクのタグ名

**パスパラメータ:**
- `task_id`: タスクID。`"latest"`を指定すると、指定されたtag内の最新のタスクをストリーミングします。

**レスポンス形式:**
```
Content-Type: text/event-stream

data: {"type": "output", "data": "hello\n"}
data: {"type": "error", "data": "warning message\n"}
data: {"type": "status", "status": "completed", "output": "hello\n", "error": ""}
```

**イベントタイプ:**
- `output`: 標準出力の行
- `error`: エラー出力の行
- `status`: タスクの最終状態（完了、失敗、キャンセル）

**使用例:**
```bash
# 特定のタスクをストリーミング
curl -N -H "Cookie: m21_session=your-session-id" \
  "http://localhost:8000/api/execute/stream/{task_id}?tag=my-task"

# 最新のタスクをストリーミング
curl -N -H "Cookie: m21_session=your-session-id" \
  "http://localhost:8000/api/execute/stream/latest?tag=my-task"
```

### POST /api/execute/stop

実行を停止します。

**リクエスト:**
```json
{
  "task_id": "uuid-string"
}
```

**レスポンス:**
```json
{
  "task_id": "uuid-string",
  "status": "cancelled",
  "message": "Execution stopped"
}
```

### DELETE /api/execute/{task_id}

タスクをクリーンアップします。

### POST /api/file

ファイルを作成します。

**リクエスト:**
```json
{
  "path": "/tmp/example.txt",
  "content": "Hello, World!",
  "sudo": false,
  "password": "optional-password"
}
```

**リクエストパラメータ:**
- `path` (必須): 作成するファイルのパス
- `content` (必須): ファイルの内容
- `sudo` (オプション): sudoでファイルを作成（デフォルト: `false`）
- `password` (オプション): sudoパスワード（`sudo=true`の場合に必要）

**レスポンス:**
```json
{
  "message": "File created successfully",
  "path": "/tmp/example.txt"
}
```

**注意事項:**
- `sudo=true`の場合、サーバー起動時に`-s`オプションが必要です
- `sudo=true`の場合、`password`パラメータが必須です

### POST /api/upload

バイナリファイルをアップロードします（multipart/form-data形式）。

**リクエスト形式:**
```
Content-Type: multipart/form-data

file: <バイナリファイル>
path: <保存先のパス>
sudo: <true/false> (オプション)
password: <sudoパスワード> (オプション)
```

**リクエストパラメータ:**
- `file` (必須): アップロードするバイナリファイル
- `path` (必須): 保存先のパス
- `sudo` (オプション): sudoでファイルをアップロード（デフォルト: `false`）
- `password` (オプション): sudoパスワード（`sudo=true`の場合に必要）

**レスポンス:**
```json
{
  "message": "File uploaded successfully",
  "path": "/tmp/uploaded-file.bin",
  "filename": "original-filename.bin",
  "size": 12345
}
```

**注意事項:**
- `sudo=true`の場合、サーバー起動時に`-s`オプションが必要です
- `sudo=true`の場合、`password`パラメータが必須です
- バイナリファイル（画像、実行ファイル、圧縮ファイルなど）をアップロードできます
- テキストファイルもアップロード可能ですが、バイナリファイル用のエンドポイントです

## CLIツール

Markdownファイル内のコードブロックを実行するCLIツールが利用可能です。

### 基本的な使い方

```bash
python cli.py example.md --url http://localhost:8000/notebook/?token=YOUR_ACCESS_TOKEN
```

### オプション

- `--url` (必須): バックエンドサーバーのURL（トークンを含む完全なURL）
- `-s`, `--sudo`: sudoパスワードの入力プロンプトを表示
- `--cookie-file`: クッキーファイルのパス（デフォルト: `cookie.json`）

### タグの自動生成

CLIツールは、入力ファイル名から自動的にタグを生成します。各コードブロックには、`{入力ファイル名（.md拡張子なし）}-{ブロック番号}`形式のタグが割り当てられます。

例: `example.md`ファイルの2番目のコードブロックは、タグ`example-2`で実行されます。

実行結果は`results/{タグ名}/`ディレクトリに保存されます。

### Markdownコードブロックオプション

コードブロックの言語指定部分にオプションを追加できます。

- **`run`**: タスクの説明（表示用）

  ```bash{run="タスクの説明"}
  echo "Hello, World!"
  ```


- **`file`**: コードブロックの内容をファイルに書き込む（実行は行わない）

````
```json{file=/tmp/data.json}
{
  "name": "John",
  "age": 30
}
```
````

- **`sudo`**: sudo実行を有効化
  ````
  ```bash{sudo=yes,run="管理者権限で実行"}
  whoami
  ```
  ````
