# 基本的なテスト

Working drectory of the task.

```bash
pwd
```

指定した言語で実行します。

```python
print("hello")
```

長い出力のテスト。長い出力はスクロールバーが表示されます。

```bash
seq 100
```

リアルタイムアウトプット。時間経過とともに出力が表示されます。

```bash
for i in 1 2 3; do
  echo "Sleep $i second(s)"
  sleep $i
done
echo finished.
```

言語を書いていない場合は、bash スクリプトとして扱われます。

```
echo hello
```

`{no}` オプションを追加すると、実行対象ではなくなります。

```python{no}
print("This is never executed.")
```

実行がエラーになると赤色で表示されます。

```bash
echo failing
false
```

## NOTE

スクリプトの途中でエラーが発生しても結果がエラー終了でなければエラー扱いされません。exit code を参照しています。

block including error.

```bash
ls non-exist
pwd
```

コードブロックの実行結果はOUTPUTに表示され、コードブロックそのものの実行エラーは以下のように表示されます。

```python
with sync_playwright() as p:
    b = PWBrowser(p)
```

## アーキテクチャ

rundmark を実行したディレクトリに .rundmark が作成され、その中にコードブロックをソース・ファイルにして実行できるようにします。また、実行結果もこのなかに保存されます。なお、実行プロセスは tmux の中で実行されます。
