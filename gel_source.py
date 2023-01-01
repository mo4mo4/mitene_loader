# 必要ライブラリ(pipで要インストール)
#  - ffmpeg-python
#
# 必要外部アプリ
#  - ffmpeg(https://github.com/BtbN/FFmpeg-Builds/releases)

# --------------------------------------------------------------------------------
# 初期設定
# --------------------------------------------------------------------------------
# 保存先フォルダ
dir = r"C:\log"
# ブラウザ版みてねのURL
mitene_url = "https://mitene.us/f/xxxxxxx"


# --------------------------------------------------------------------------------
# 以下コード

import urllib.request
import requests
import os
import glob
import ffmpeg
import shutil

os.chdir(dir)
print(os.getcwd())

# 動画用にバッファーフォルダを作成する（なければ）
buf_dir = dir+r'\buf'
os.makedirs(buf_dir, exist_ok=True)

end_flag = False
pageno = 1


while end_flag == False : 

    url = mitene_url+ "?page="+str(pageno)

    response = urllib.request.urlopen(url)
    encodeData = response.read().decode('utf-8_sig').split('\n')

    # jsonからmediaFilesを抜粋(falseとtrueを大文字にしておかないと怒られたので置換)
    mediaFiles = eval(encodeData[2].split(";")[1].split(".media=")[1].replace('false', 'False').replace('true', 'True').replace('null', '0'))['mediaFiles']

    # mediaFilesの中身が空だったらループ終了
    if len(mediaFiles) < 1 :
        print("Download done!")
        end_flag = True
        break
    
    # 1ページの画像・動画を取得する
    for i in range(0, len(mediaFiles)):
    
        dict_data = mediaFiles[i]

        # タイムスタンプの取得
        date = dict_data['tookAt'].replace(':','').replace('+0900','').replace('T','_')

        # media typeのチェック
        media = dict_data['mediaType']

        # media typeに応じてデータを取得
        if media == 'movie' :

            #ファイル名の作成
            file_name = date+".mp4"

            print("Page %s, No.%s : filename %s" % (pageno, i+1, file_name), end='')
            if os.path.isfile(file_name) :
                print('\talready existed.')
                continue

            # バッファフォルダに移動
            os.chdir(buf_dir)

            # 動画はtsファイルを細切れされているので、URLを全取得する
            media_url_tmp = dict_data['expiringVideoUrl']
            response = requests.get(media_url_tmp)
            encodeData = response.text.split('\n')

            cnt=0
            # 細切れにされた動画をダウンロード
            for i in range(len(encodeData)):
                if 'https' in encodeData[i] :
                    cnt=cnt+1
                    # 元ファイルがtsファイルなので、一応合わせておく
                    ts_name = str(cnt).zfill(3)+'.ts'
                    response = requests.get(encodeData[i])       
                    with open(ts_name, "wb") as saveFile:
                        saveFile.write(response.content)
                    print('.', end='')                 

            #フォルダ内のファイルパスを取得する
            file_list = glob.glob(buf_dir+r'\*')

            # 動画を結合する
            ffmpeg.input("concat:" + "|".join(file_list)).output(dir+r'\\'+file_name, c="copy").run()
            print('done')

            # 元のディレクトリに戻る
            os.chdir(dir)

            # バッファフォルダの中身を空にする
            shutil.rmtree(buf_dir)
            os.mkdir(buf_dir)

        else : #elif media == 'photo' :
            media_url = dict_data['expiringUrl']

            #ファイル名の作成
            file_name = date+".jpg"

            print("Page %s, No.%s : filename %s" % (pageno, i+1, file_name),end='')
            if os.path.isfile(file_name) :
                print('\talready existed.')
                continue

            # ファイルのダウンロード
            response = requests.get(media_url)       
            with open(file_name, "wb") as saveFile:
                saveFile.write(response.content)
            
            print('\tdone')

    pageno = pageno+1
        

