# input オプション

input オプションを指定することで、対話的な入力が可能です。Cmd + Enter で送信を行うことに注意です。

```bash{input}
echo hello
read -p "input any string: " user
echo "your input is $user"
```

## 入力を隠す

パスワード入力は、input=hide とすることで echo back が隠されます。この場合、Enter のみで送信します。

```bash{run,input=hide}
sudo whoami
```
