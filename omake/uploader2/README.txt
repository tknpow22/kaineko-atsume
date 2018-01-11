実行
----

# 以下のファイルを https://github.com/rykov8/ssd_keras からダウンロードします

    ssd.py
    ssd_layers.py
    ssd_utils.py

    なお、現時点(2017/12)では ssd_layers.py を Keras の最新版に合わすため、
    以下の修正が必要です。

        ssd_layers.py:
            #def get_output_shape_for(self, input_shape):
            def compute_output_shape(self, input_shape):

# 以下のファイルを https://mega.nz/#F!7RowVLCL!q3cEVRK9jyOSB9el3SssIA からダウンロードします

    weights_SSD300.hdf5

# アドレス・ポート

    uploader.py の

        run(host='0.0.0.0', port=8080, debug=True, reloader=False)

    を必要であれば、環境にあわせて変更します。

# アドレス・ポートが利用できるよう、ファイアウォールを設定します。

# CUI から以下のコマンドで起動します。

    python3 uploader.py

アップローダ
------------

# uploader.py

    アップロードされたファイルを判定後、保存します

# use_ssd.py

    SSD の実装を利用して画像の判定を行います

# files/

    アップロードされたファイルが格納されます

判定だけ
--------

# process_img.py

    判定だけ行います。
    files/ ディレクトリのファイルを判定します

