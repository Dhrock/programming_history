import pandas as pd

# header情報
col = ["調査年月日", "調査地名","数"]
col_out = ["調査年月", "調査地名","数"]

# 最終出力にする空データフレーム
df_out = pd.DataFrame(columns=col_out)

# 年月日区分の範囲

date = list(range(20210901,20211301,100))
date_22 = list(range(20220101,20220701,100))
date.extend(date_22)

# date = list(range(20210901,20211301,100))
# date_22 = list(range(20220101,20220701,100))
# date.extend(date_22)

# 入力・出力ファイル名の指定
print('入力するファイル名(演算子も含める)')
input_Filename = input('>> ')
print('出力するファイル名(演算子も含める)')
output_Filename = input('>> ')

# csvファイル読み込み
df = pd.read_csv('inputdata_csv/'+ input_Filename, encoding="utf-8",usecols=[0,1,3])
df_area = pd.read_csv('area_name.csv', encoding="utf-8",usecols=[0])

df = df[df['調査地名'] != '漫湖']
df['数'].astype(int)

# 地名の選別リスト
place_name = df_area['調査地名'].tolist()

#「地名」毎にデータベースの整理
for name in place_name:
    
    # 地名検索
    judge_place = '調査地名 == ' + '"' + str(name) + '"'
    df_place = df.query(judge_place)

    # データベースに検索地名がない場合、調査年月日と数（０）を追加
    if (df_place.empty == True):
        for d in range(len(date)-1):
            df_place_add = pd.DataFrame([[date[d],name,0]],columns=col)
            df_place = pd.concat([df_place,df_place_add])

    for d in range(len(date)-1):
        month_sum = 0

        # 月の範囲
        low = date[d]
        up = date[d+1]
        judge_date = str(low) + ' <= 調査年月日 < ' + str(up)
        
        df_month = df_place.query(judge_date)
        
        # データベースに指定の月がある場合は、その月における"数"の合計値を算出し、年と月のみを"調査年月日"に出力する
        # 指定の月がない場合は、"数"の0にして返す
        if(df_month.empty == False):
            month_sum = df_month['数'].sum()
            df_month_add = pd.DataFrame([[int(date[d]/100),name,month_sum]],columns=col_out)
            df_out = pd.concat([df_out,df_month_add])
        else:
            df_month_add = pd.DataFrame([[int(date[d]/100),name,0]],columns=col_out)
            df_out = pd.concat([df_out,df_month_add])

df_out.to_csv('outputdata_csv/' + output_Filename, encoding='utf-8_sig', index=False)
