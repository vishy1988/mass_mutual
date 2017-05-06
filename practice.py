import sqlite3
import pandas as pd
from flask import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO,StringIO
app = Flask(__name__)
@app.route("/social_media_summary")
def show_graph():
    connection = sqlite3.connect('recruit.db')
    query = "select * from customer"
    df_customer = pd.read_sql(query, connection)
    FB_Data = df_customer.loc[:,['race_code','facebook_user_rank']]
    FB_Data.facebook_user_rank = FB_Data.facebook_user_rank.astype(int)
    race_data = FB_Data.groupby('race_code').agg({'facebook_user_rank':'mean'})
    race_data = race_data.reset_index()
    query = "select * from race"
    df_race = pd.read_sql(query,connection)
    df_race.columns = ['race_code','value']
    race_data_plot = race_data.merge(df_race,on='race_code',how='left')
    race_data_plot = race_data_plot.drop(['race_code'],axis=1)
    race_data_plot.columns = ['Avg_Facebook_User_Rank','Ethinicity']
    race_data_list = race_data_plot.values.tolist()
    race_data_plot.set_index('Ethinicity',inplace=True)
    data = json.dumps(race_data_list)
    return render_template('display.html',data=data,tables=[race_data_plot.to_html(classes='Facebook_Usage_Summmary')],
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

@app.route("/buff/")
def new_fig():
    connection = sqlite3.connect('recruit.db')
    query = "select * from customer"
    df_customer = pd.read_sql(query, connection)
    trial_df = df_customer.loc[:,['state','race_code','travel_spending']]
    travel_df = trial_df.groupby(['state','race_code']).agg({'travel_spending':'mean'})
    travel_df = travel_df.reset_index()
    filter_travel = travel_df[(travel_df.state=='CA')|(travel_df.state=='MA')|(travel_df.state=='NY')]
    query = "select * from race"
    df_race = pd.read_sql(query,connection)
    df_race.columns = ['race_code','value']
    travel_data = filter_travel.merge(df_race,on='race_code',how='right')
    travel_data = travel_data.drop(['race_code'],axis=1)
    travel_data.columns = ['state','avg_travel_spending','ethinicity']
    travel_data.set_index(['state','ethinicity'],inplace=True)

    plt.style.use('ggplot')

    plt.rcParams['xtick.color']='k'
    plt.rcParams['xtick.labelsize']='x-large'


    travel_data.unstack(level=0).plot(kind='bar', subplots=True, legend=False)
    buff = BytesIO()
    plt.tight_layout()
    plt.savefig(buff, format='png', dpi=150)
    buff.seek(0)
    return send_file(buff, mimetype='image/png')

@app.route('/image/')
def images():
    return render_template("image.html")





if __name__ == "__main__":
    app.run( port=8010,debug=True)
