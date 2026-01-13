```bash{run="stream ouput test"}
echo sleeping
sleep 3
echo woke up
sleep 1
```

```bash{run}
touch /tmp/f
tail -f /tmp/f
```

```bash{run="stream ouput test"}
echo -n sleeping | tee -a /tmp/f
sleep 5
echo woke up | tee -a /tmp/f
sleep 1
```
