---
target: "http://localhost:8001"
---

---
target: http://localhost:8001
---

## ファイル作成

file オプションでファイルを作成します。`file=/path/to/file`のように指定できます。相対パスの場合は、rundmarkを実行したところから参照します。

```json{file=/tmp/test.json}
{
  "name": "John",
  "age": 30 
}
```

ひとつの Markdown ファイル内で同じファイル名を使用すると挙動がおかしくなります。必要な場合は、`auto-file-update: false` を frontmatter に記載します。

```json{file=/tmp/test2.json}
{
  "name": "John",
  "age": 30
}
```

確認とクリーンアップ。

```bash{run="View the JSON file"}
cat /tmp/test.json
rm /tmp/test.json
```

ファイル名を指定しない場合は、直前の行をファイル名として扱います。

/tmp/test3.json

```{file}
{
  "name": "John",
  "age": 30
}
```
