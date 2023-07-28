# # 標準ライブラリ
import os
import time
import datetime

# # 外部ライブラリ
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


# LOGファイルパス
LOG_FILE_PATH = "log/log_{datetime}.log"
log_file_path = LOG_FILE_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))


# フォルダ作成
def makedir_for_filepath(filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    
# ログ出力
def log(txt):
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logStr = '[%s: %s] %s' % ('log', now , txt)
    # ログ出力
    makedir_for_filepath(log_file_path)
    with open(log_file_path, 'a', encoding='utf-8_sig') as f:
        f.write(logStr + '\n')
    print(logStr)


# ドライバの定義
def set_driver():

    # USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    options = webdriver.ChromeOptions()

    # 起動オプションの設定
    options.add_argument(f'--user-agent={USER_AGENT}') # ブラウザの種類を特定するための文字列
    options.add_argument('log-level=3') # 不要なログを非表示にする
    options.add_argument('--ignore-certificate-errors') # 不要なログを非表示にする
    options.add_argument('--ignore-ssl-errors') # 不要なログを非表示にする
    # options.add_experimental_option('excludeSwitches', ['enable-logging']) # 不要なログを非表示にする
    options.add_argument('--incognito') # シークレットモードの設定を付与
    
    # ChromeのWebDriverオブジェクトを作成する。
    service = Service(executable_path='./chromedriver-mac-arm64/chromedriver.exe')
    return webdriver.Chrome(service=service, options=options)  

        

def main(df, spec_cnt, spec_page):
    driver = set_driver()
    driver.get("https://www.amazon.co.jp/")
    time.sleep(2)
    
    # 初期設定
    asin_list = []
    item_list = []
    item_cnt = 0

    # キーワードごとに検索結果ページを表示
    def view_page_by_keyword(keyword):
        try:
            driver.find_element(by=By.ID ,value="twotabsearchtextbox").clear()
            driver.find_element(by=By.ID ,value="twotabsearchtextbox").send_keys(keyword)
            driver.find_element(by=By.ID, value="nav-search-submit-button").click()
        except:
            time.sleep(20)
            driver.find_element(by=By.ID ,value="nav-bb-search").clear()
            driver.find_element(by=By.ID ,value="nav-bb-search").send_keys(keyword)
            driver.find_element(by=By.ID, value="nav-bb-button").click()
        time.sleep(2)

    # ASINを取得
    def fetch_asin(spec_cnt, spec_page, keyword, mercari_page_url, mercari_image_url, mercari_price):
        fetch_cnt = 0
        fetch_page = 0
        while fetch_page <= int(spec_page):
            items= driver.find_elements(by=By.CSS_SELECTOR, value=".s-asin") 
            # 指定件数に届くまでASINを取得
            for item in items:
                item_asin = item.get_attribute("data-asin")
                # asin_list.append(
                #     [item_asin, keyword, mercari_page_url, mercari_image_url, mercari_price]
                #     )
                asin_list.append({
                    "検索KW": keyword,
                    "対象商品ページURL": mercari_page_url,
                    "対象商品画像URL": mercari_image_url,
                    "対象商品価格": mercari_price,
                    "ASIN": item_asin,
                })
                fetch_cnt += 1
                if fetch_cnt == int(spec_cnt):
                    break
            fetch_page += 1
            # 件数、ページ数のどちらも指定数に届かなければ次のページへ
            if fetch_cnt==int(spec_cnt) or fetch_page==int(spec_page):
                break
            else:
                try:
                    driver.find_element(by=By.CSS_SELECTOR, value="a.s-pagination-next").click()
                    time.sleep(3)
                except:
                    print("次ページへ遷移できませんででした。")
                    break
                
    # 商品情報を取得
    def fetch_item_info(item_cnt, keyword, mercari_page_url, mercari_image_url, mercari_price, item_asin):
        item_url = f"https://www.amazon.co.jp/dp/{item_asin}"
        driver.get(item_url)
        try:
            # 商品名
            item_name = driver.find_element(by=By.CSS_SELECTOR, value=".product-title-word-break").text
            # 画像URL
            try:
                item_image_url = driver.find_element(by=By.CSS_SELECTOR, value=".itemNo0").find_element(by=By.TAG_NAME, value="img").get_attribute("src")
            except:
                pass
            try:
                review_cnt = driver.find_element(By.ID, "acrCustomerReviewText").text.rstrip("個の評価")
            except:
                review_cnt = ""
            try:
                review = driver.find_element(by=By.XPATH, value='//span[@data-hook="rating-out-of-text"]').text.replace("星5つ中の","")
            except:
                review = ""
        except:
            item_name = ""
            item_image_url = ""
            review_cnt = ""
            review = ""
            
        item_list.append({
            "検索KW": keyword,
            "対象商品ページURL": mercari_page_url,
            "対象商品画像URL": mercari_image_url,
            "対象商品価格": mercari_price,
            "ASIN": item_asin,
            "商品名": item_name,
            "URL": item_url,
            "評価件数": review_cnt,
            "評価": review,
            "画像URL": item_image_url,
        })
        
        log(f"{item_cnt}件目：success：取得完了しました。")

    # メイン処理1（キーワードごとにページを開き、ASINを取得）
    for keyword, mercari_page_url, mercari_image_url, mercari_price in zip(df["商品名"], df["ページURL"], df["1枚目の画像URL"], df["商品価格"]):
        view_page_by_keyword(keyword)
        fetch_asin(spec_cnt, spec_page, keyword, mercari_page_url, mercari_image_url, mercari_price)
    
    # メイン処理2（処理1で取得したASINごとに商品情報を取得） 
    for asin_dict in asin_list:
        # item_asin = asin[0]
        # keyword = asin[1]
        # mercari_page_url = asin[2]
        # mercari_image_url = asin[3]
        # mercari_price = asin[4]
        item_cnt += 1
        fetch_item_info(item_cnt, asin_dict["検索KW"], asin_dict["対象商品ページURL"], asin_dict["対象商品画像URL"], asin_dict["対象商品価格"], asin_dict["ASIN"])
    
    return item_list
