import os
import datetime
import pandas as pd
import scraping


# CSVファイルパス
EXP_CSV_PATH = "amazon_csv/exp_list_{datetime}.csv"

# ファイルの作成
def makedir_for_filepath(filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

# メイン処理
def main():
    
    # CSVの読み込み
    search_csv = input("ASINを取得するCSV名を指定してください。>>")
    spec_cnt = input("キーワードごとの最大取得件数を指定してください。>>")
    spec_page = input("キーワードごとの最大ページ件数を指定してください。>>")
    df = pd.read_csv(os.path.join(os.getcwd(), search_csv))

    # # スクレイピング    
    item_list = scraping.main(df=df, spec_cnt=spec_cnt, spec_page=spec_page)

    # CSVファイル保存処理
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    makedir_for_filepath(EXP_CSV_PATH) 
    df = pd.DataFrame.from_dict(item_list, dtype=object)
    df.to_csv(EXP_CSV_PATH.format(datetime=now), encoding="utf-8-sig")
        
if __name__ == "__main__":        
    main()