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

# CUI から以下のコマンドで起動します。

    python3 uploader.py

アップローダ
------------

# uploader.py

    アップロードされたファイルを保存・分類します

# use_ssd.py

    SSD の実装を利用して画像の分類・保存を行います

# files/

    アップロードされたファイルが格納されます

# processed_imgs/

    分類後の画像が格納されます

分類だけ
--------

# process_img.py

    分類だけ行います。
    files/ ディレクトリのファイルを分類し、processed_imgs/ に格納します

