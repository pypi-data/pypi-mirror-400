# sudo オプション

sudo オプションを使用すると、input=hide と同じ挙動になります。それと合わせてすべてのブロックを実行するオプションが disable されるので、こちらを使うほうが安全です。

```bash{sudo}
sudo whoami
whoami
```

ファイルに sudo オプションをつけると、root でファイルを作成します。

```json{file=/tmp/test.json,sudo}
{
  "name": "John",
  "age": 30
}
```

確認処理。

```bash{run="View the JSON file"}
ls -l /tmp/test.json
```

```bash{input=hide,run="Delete the JSON file"}
sudo rm /tmp/test.json
```
