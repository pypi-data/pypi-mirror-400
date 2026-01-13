# Table を実行する

`::: table=<テーブル名>` を書くことで表に名前をつけます。

::: table=sample
| -x | -y | opt |
| :--- | :--- | :--- |
| 1    | true | abc |
| 2    | false | def |
| 3    | true |     |


ハイフンから始まる場合は、それを引数として追加します。true/false で ON/OFF を切り替えられます。
実行がエラーになった場合、その行以降は実行しません。

```bash{table=sample}
if [ "$3" != "-y" ]; then
  echo "error"
  echo "error in stderr" 1>&2
  exit 1
fi
echo $*                                                 
```

この場合、以下のように表を１行ずつ実行していきます。

```bash{no}
bash sample -x 1 -y abc
bash sample -x 2 def
bash sample -x 3 -y
```

同じテーブルを何度も使い回せます。

```bash{table=sample}
echo $*
```