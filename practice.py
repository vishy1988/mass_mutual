import sqlite3
import pandas as pd
from flask import *
app = Flask(__name__)
@app.route("/social_media_summary")
def show_graph():
    connection = sqlite3.connect('recruit.db')
    query = "select * from customer"
    df_customer = pd.read_sql(query, connection)
    df_fb_usage = df_customer.loc[:,['race_code','facebook_user_rank']]
    df_fb_usage.facebook_user_rank = df_fb_usage.facebook_user_rank.astype(int)
    plot_df = df_fb_usage.groupby('race_code').agg({'facebook_user_rank':'mean'})
    plot_df = plot_df.reset_index()
    query = "select * from race"
    df_race = pd.read_sql(query,connection)
    df_race.columns = ['race_code','value']
    Plot_df_new = plot_df.merge(df_race,on='race_code',how='left')
    Plot_df_new = Plot_df_new.drop(['race_code'],axis=1)
    Plot_df_new.columns = ['Avg_Facebook_User_Rank','Ethinicity']
    df_list = Plot_df_new.values.tolist()
    Plot_df_new.set_index('Ethinicity',inplace=True)
    data = json.dumps(df_list)
    return render_template('display.html',data=data,tables=[Plot_df_new.to_html(classes='Facebook_Usage_SumBmary')],
    titles=['Facebook_Usage_Summary'])
@app.route("/Home_Owner_Details")
def new_graph():
    connection = sqlite3.connect('recruit.db')
    query = "select * from customer"
    df_customer = pd.read_sql(query, connection)
    new_df = df_customer.loc[:,['race_code','home_owner']]
    def label_home_owner (row):
        if row['home_owner']=='O':
            return 'O'
        else:
            return None


    new_df['label_home_owner'] = new_df.apply(label_home_owner, axis=1)
    percent_df = new_df.groupby('race_code').agg({'label_home_owner':'count','home_owner':'count'})
    percent_df = percent_df.reset_index()
    percent_df_new = percent_df.copy()
    percent_df.columns = ['race_code','home_owner_count','total_population']
    query = "select * from race"
    df_race = pd.read_sql(query,connection)
    df_race.columns = ['race_code','value']
    percent_df = percent_df.merge(df_race,on='race_code',how='left')
    percent_df.drop(['race_code'],axis=1,inplace=True)
    percent_df.columns=['Home_Owner_Count','Total_Population','Ethinicity']
    percent_df = percent_df.set_index('Ethinicity')
    percent_df_new['percent_home_owners']= percent_df_new['label_home_owner']/percent_df_new['home_owner']
    percent_df_new['percent_home_owners'] = percent_df_new['percent_home_owners']*100
    percent_df_new.drop(['label_home_owner','home_owner'],axis=1,inplace=True)

    percent_df_new = percent_df_new.merge(df_race,on='race_code',how='right')
    percent_df_new.drop(['race_code'],axis=1,inplace=True)
    percent_df_new.columns = ['percent_home_owners','ethinicity']

    df_list = percent_df_new.values.tolist()
    data = json.dumps(df_list)
    return render_template('new_display.html',data=data,tables=[percent_df.to_html(classes='Home_owner_data')],
    titles=['Home_owner_data'])

if __name__ == "__main__":
    app.run( port=8085,debug=True)
