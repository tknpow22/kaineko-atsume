実行
----

# アドレス・ポート

    uploader.go の

        http.ListenAndServe("0.0.0.0:8080", nil)

    を必要であれば、環境にあわせて変更します。

# アドレス・ポートが利用できるよう、ファイアウォールを設定します。

# CUI から以下のコマンドで起動します。

    go run uploader.go

